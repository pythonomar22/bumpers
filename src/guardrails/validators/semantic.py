from typing import List, Dict, Any, Optional
import numpy as np
from .base import BaseValidator
from ..core.engine import ValidationResult, ValidationPoint

class SemanticDriftValidator(BaseValidator):
    def __init__(self, 
                 embedding_model,  # Function that converts text to embeddings
                 similarity_threshold: float = 0.7,
                 name: str = "semantic_drift"):
        super().__init__(name)
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.initial_goal_embedding = None
        
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        current_text = context.get("output", "")
        original_goal = context.get("question", "")
        turn = context.get("turn", 0)
        
        # On first turn, store the goal embedding
        if turn == 1 or self.initial_goal_embedding is None:
            self.initial_goal_embedding = self.embedding_model(original_goal)
            return ValidationResult(
                passed=True,
                message="Initial goal embedding stored",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context
            )
            
        # Compare current output with original goal
        current_embedding = self.embedding_model(current_text)
        similarity = self._compute_similarity(
            self.initial_goal_embedding, 
            current_embedding
        )
        
        if similarity < self.similarity_threshold:
            return ValidationResult(
                passed=False,
                message=f"Semantic drift detected: similarity {similarity:.2f} below threshold {self.similarity_threshold}",
                validator_name=self.name,
                validation_point=ValidationPoint.PRE_OUTPUT,
                context=context
            )
            
        return ValidationResult(
            passed=True,
            message=f"Output remains aligned with goal (similarity: {similarity:.2f})",
            validator_name=self.name,
            validation_point=ValidationPoint.PRE_OUTPUT,
            context=context
        ) 