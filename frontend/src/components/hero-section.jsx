"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Editor from "@monaco-editor/react"
import { SiOpenai, SiLangchain } from 'react-icons/si'
import { GiRobotGolem } from 'react-icons/gi'

export function HeroSection() {
  const frameworks = [
    { id: "react", name: "ReAct", icon: <GiRobotGolem className="w-5 h-5" />, default: true },
    { id: "langchain", name: "LangChain", icon: <SiLangchain className="w-5 h-5" /> },
    { id: "openai", name: "OpenAI", icon: <SiOpenai className="w-5 h-5" /> },
  ]

  const codeExamples = {
    react: `from bumpers.integrations.react import GuardedReActAgent
from bumpers.core.engine import CoreValidationEngine
from bumpers.validators.action import ActionWhitelistValidator

# Initialize validation engine
engine = CoreValidationEngine()

# Register action whitelist validator
validator = ActionWhitelistValidator(allowed_actions=["search", "calculate"])
engine.register_validator(validator, "pre_action")

# Define available actions
actions = {
    "search": wikipedia_search,
    "calculate": safe_calculator
}

# Create guarded ReAct agent
agent = GuardedReActAgent(
    validation_engine=engine,
    prompt="You are a helpful AI assistant that can search and calculate."
)

# Run agent with safety guardrails
result = agent.query("What is 20 * 15?", actions) `,
    langchain: `from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from bumpers.core.engine import CoreValidationEngine, ValidationPoint
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.validators.content import ContentFilterValidator
from bumpers.logging import FileLogger

# Initialize validation engine with logging
logger = FileLogger("logs")
engine = CoreValidationEngine(logger=logger)

# Register validators for different validation points
action_validator = ActionWhitelistValidator(allowed_actions=["search", "calculate"])
content_validator = ContentFilterValidator(blocked_categories=["HARM", "HATE"])

engine.register_validator(action_validator, ValidationPoint.PRE_ACTION)
engine.register_validator(content_validator, ValidationPoint.PRE_OUTPUT)

# Define LangChain components
llm = ChatOpenAI(temperature=0)
known_actions = {
    "search": wikipedia_search,
    "calculate": safe_calculator
}

# Create LangChain agent with guardrails
agent = initialize_agent(
    tools=known_actions.values(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    validation_engine=engine  # Integrate guardrails
)

# Run agent with safety checks
result = agent.run("What is the capital of France and its population?")
# Will validate actions and content before execution`,
    openai: `import json
from openai import OpenAI
from guardrails.core.approval import Guardrails

gr = Guardrails()

# Function that can be called without approval
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    return wikipedia.summary(query)

# Function that requires human approval
@gr.require_approval()
def execute_code(code: str) -> str:
    """Execute potentially risky code with human oversight."""
    return eval(code)  # Only runs after approval

# Example usage
result = search_wikipedia("Python language")  # Runs immediately
code_result = execute_code("print('Hello')")  # Requires approval`,
  }

  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="text-center space-y-8 mb-16 max-w-[800px] mx-auto px-4">
        <div className="space-y-2">
          <h1 className="text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500 leading-tight">
            Bumpers
          </h1>
          <p className="text-2xl font-medium text-gray-400">
            guardrails for ai agents
          </p>
        </div>
        <p className="text-lg text-muted-foreground/80 max-w-[600px] mx-auto">
          An API and SDK for building safe and reliable AI agents that stay on task and within bounds.
        </p>
        <div className="flex items-center justify-center space-x-4 pt-4">
          <Button size="lg" className="h-12 px-8">Get Started</Button>
          <Button variant="outline" size="lg" className="h-12 px-8 bg-[#2A2A2A] hover:bg-[#333333]">Watch Demo</Button>
        </div>
      </div>

      <div className="w-full max-w-[1000px] mx-auto px-4">
        <Card className="overflow-hidden border border-[#333] rounded-xl bg-[#1e1e1e] shadow-2xl">
          <div className="flex items-center gap-2 bg-[#1e1e1e] px-4 py-2 border-b border-[#333]">
            <div className="flex space-x-2">
              <div className="w-3 h-3 rounded-full bg-[#ff5f57]"></div>
              <div className="w-3 h-3 rounded-full bg-[#febc2e]"></div>
              <div className="w-3 h-3 rounded-full bg-[#28c840]"></div>
            </div>
            <div className="text-xs text-gray-400 ml-2">example.py</div>
          </div>
          
          <Tabs defaultValue="react" className="w-full">
            <div className="bg-[#252526] border-b border-[#333]">
              <TabsList className="w-full justify-start h-auto p-0 bg-transparent">
                {frameworks.map((fw) => (
                  <TabsTrigger
                    key={fw.id}
                    value={fw.id}
                    className="px-4 py-3 rounded-none data-[state=active]:bg-[#1e1e1e] data-[state=active]:border-b-2 data-[state=active]:border-[#007acc] text-[#8a8a8a] data-[state=active]:text-white flex items-center gap-2"
                  >
                    {fw.icon}
                    {fw.name}
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>

            {frameworks.map((fw) => (
              <TabsContent key={fw.id} value={fw.id} className="p-0 bg-[#1e1e1e] border-0">
                <div className="relative">
                  <div className="p-6">
                    <Editor
                      height="550px"
                      defaultLanguage="python"
                      defaultValue={codeExamples[fw.id] || "# Example coming soon..."}
                      theme="vs-dark"
                      options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 14,
                        lineNumbers: "off",
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        folding: false,
                        lineDecorationsWidth: 0,
                        lineNumbersMinChars: 0,
                        renderLineHighlight: "none",
                        scrollbar: {
                          vertical: "hidden",
                          horizontal: "hidden"
                        },
                        wordWrap: "on",
                        padding: { top: 20, bottom: 20 }
                      }}
                    />
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </Card>
      </div>
    </div>
  )
} 