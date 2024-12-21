from typing import Dict, Any, Optional, List
import numpy as np
from sentence_transformers import SentenceTransformer
from .base import BaseValidator, FailStrategy
from ..core.engine import ValidationResult, ValidationPoint

class SemanticDriftValidator(BaseValidator):
    """
    Sophisticated validator that detects semantic drift in agent responses using
    sentence transformers and multiple validation strategies.
    """
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 similarity_threshold: float = 0.7,
                 context_window: int = 3,
                 name: str = "semantic_drift",
                 fail_strategy: FailStrategy = FailStrategy.RAISE_ERROR):
        """
        Initialize the semantic drift validator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
            similarity_threshold: Minimum cosine similarity required
            context_window: Number of previous responses to maintain for context
            name: Validator name
            fail_strategy: Strategy to use when validation fails
        """
        super().__init__(name, fail_strategy)
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.context_window = context_window
        self.initial_goal_embedding = None
        self.context_history: List[Dict] = []
        
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def _get_context_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with context window consideration"""
        # Include previous context in embedding calculation
        context_texts = [item["text"] for item in self.context_history[-self.context_window:]]
        context_texts.append(text)
        
        # Get embeddings for all texts
        embeddings = self.model.encode(context_texts)
        
        # Weight recent context more heavily
        weights = np.exp(np.linspace(-2, 0, len(embeddings)))
        weights = weights / weights.sum()
        
        # Return weighted average embedding
        return np.average(embeddings, axis=0, weights=weights)
    
    def _analyze_semantic_components(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze different semantic components of the response"""
        components = {}
        
        # Get relevant text parts
        thought = context.get("thought", "")
        action = f"{context.get('action', '')}: {context.get('action_input', '')}"
        observation = context.get("observation", "")
        output = context.get("output", "")
        
        # Calculate similarity for each component
        if self.initial_goal_embedding is not None:
            if thought:
                components["thought_similarity"] = self._compute_similarity(
                    self.initial_goal_embedding,
                    self.model.encode(thought)
                )
            if action:
                components["action_similarity"] = self._compute_similarity(
                    self.initial_goal_embedding,
                    self.model.encode(action)
                )
            if observation:
                components["observation_similarity"] = self._compute_similarity(
                    self.initial_goal_embedding,
                    self.model.encode(observation)
                )
            if output:
                components["output_similarity"] = self._compute_similarity(
                    self.initial_goal_embedding,
                    self.model.encode(output)
                )
                
        return components
    
    def _update_context_history(self, context: Dict[str, Any]):
        """Update the context history with new response"""
        # Combine relevant parts into single context
        text_parts = []
        if context.get("thought"):
            text_parts.append(f"Thought: {context['thought']}")
        if context.get("action"):
            text_parts.append(f"Action: {context['action']}: {context.get('action_input', '')}")
        if context.get("observation"):
            text_parts.append(f"Observation: {context['observation']}")
        if context.get("output"):
            text_parts.append(f"Output: {context['output']}")
            
        combined_text = " ".join(text_parts)
        
        # Add to history
        self.context_history.append({
            "text": combined_text,
            "embedding": self.model.encode(combined_text)
        })
        
        # Maintain context window
        if len(self.context_history) > self.context_window:
            self.context_history.pop(0)

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate that response maintains semantic similarity with original goal.
        Uses multiple validation strategies and context history.
        """
        # Get the question/goal if this is the first validation
        question = context.get("question", "")
        if question and self.initial_goal_embedding is None:
            self.initial_goal_embedding = self.model.encode(question)
            self._update_context_history(context)
            return ValidationResult(
                passed=True,
                message="Initial goal embedding stored",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context,
                fail_strategy=self.fail_strategy
            )
            
        # Get current context embedding
        current_text = " ".join([
            context.get("thought", ""),
            context.get("action", ""),
            context.get("observation", ""),
            context.get("output", "")
        ])
        
        if not current_text.strip():
            return ValidationResult(
                passed=True,
                message="No content to validate",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context,
                fail_strategy=self.fail_strategy
            )
            
        # Get embedding with context consideration
        current_embedding = self._get_context_embedding(current_text)
        
        # Calculate overall similarity
        similarity = self._compute_similarity(
            self.initial_goal_embedding,
            current_embedding
        )
        
        # Get component-wise analysis
        component_similarities = self._analyze_semantic_components(context)
        
        # Update context history
        self._update_context_history(context)
        
        # Determine if response has drifted too far
        if similarity < self.similarity_threshold:
            # Create detailed message about drift
            drift_details = [f"Overall similarity: {similarity:.2f}"]
            for component, comp_sim in component_similarities.items():
                drift_details.append(f"{component}: {comp_sim:.2f}")
                
            return ValidationResult(
                passed=False,
                message=f"Semantic drift detected:\n" + "\n".join(drift_details),
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context,
                fail_strategy=self.fail_strategy
            )
            
        return ValidationResult(
            passed=True,
            message=f"Response maintains semantic similarity: {similarity:.2f}",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context,
            fail_strategy=self.fail_strategy
        ) 