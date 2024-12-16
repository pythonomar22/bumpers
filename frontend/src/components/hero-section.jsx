"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Editor from "@monaco-editor/react"

export function HeroSection() {
  const frameworks = [
    { id: "openai", name: "OpenAI", icon: "🧠" },
    { id: "langchain", name: "LangChain", icon: "⛓️", default: true },
    { id: "crewai", name: "CrewAI", icon: "👥" },
    { id: "controlflow", name: "Controlflow", icon: "🔄" },
    { id: "fastapi", name: "FastAPI", icon: "⚡" },
    { id: "flask", name: "Flask", icon: "🌶️" }
  ]

  const handleCopy = (code) => {
    navigator.clipboard.writeText(code)
  }

  const codeExamples = {
    langchain: `from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from guardrails.core.approval import ApprovalMethod, Guardrails

gr = Guardrails(api_key="sk-example-key", verbose=True)

@tool
def add(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y

@gr.require_approval()
def multiply(x: int, y: int) -> int:
    """multiply two numbers"""
    return x * y

tools = [add.as_tool(), multiply.as_tool()]`,
    openai: `import json
import logging
from openai import OpenAI
from humanlayer import HumanLayer

hl = HumanLayer.cloud(verbose=True)

PROMPT = "multiply 2 and 5, then add 32 to the result"

# add can be called without approval
def add(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y

# but multiply must be approved by a human
@hl.require_approval()
def multiply(x: int, y: int) -> int:
    """multiply two numbers"""
    return x * y`,
    crewai: `from crewai import Agent, Task, Crew
from guardrails.core.approval import Guardrails

gr = Guardrails()

@gr.require_approval()
def execute_task(agent: Agent, task: Task):
    """Execute task with safety validation."""
    return agent.execute(task)

# Create agents with guardrails
researcher = Agent(
    role='Researcher',
    goal='Conduct thorough research',
    backstory='Expert at analyzing data',
    allow_delegation=False
)`,
  }

  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="text-center space-y-8 mb-16 max-w-[800px] mx-auto px-4">
        <h1 className="text-6xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
          Guardrails for AI Agents
        </h1>
        <p className="text-xl text-muted-foreground">
          A powerful validation and safety framework that ensures AI agents operate within defined boundaries and ethical guidelines.
        </p>
        <div className="flex items-center justify-center space-x-4 pt-4">
          <Button size="lg" className="h-12 px-8">Get Started</Button>
          <Button variant="outline" size="lg" className="h-12 px-8">Watch Demo</Button>
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
          
          <Tabs defaultValue="langchain" className="w-full">
            <div className="bg-[#252526] border-b border-[#333]">
              <TabsList className="w-full justify-start h-auto p-0 bg-transparent">
                {frameworks.map((fw) => (
                  <TabsTrigger
                    key={fw.id}
                    value={fw.id}
                    className="px-4 py-3 rounded-none data-[state=active]:bg-[#1e1e1e] data-[state=active]:border-b-2 data-[state=active]:border-[#007acc] text-[#8a8a8a] data-[state=active]:text-white flex items-center gap-2"
                  >
                    <span>{fw.icon}</span>
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
                      height="400px"
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
                  <div className="absolute top-8 right-8">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-xs text-gray-400 hover:text-white hover:bg-white/10"
                      onClick={() => handleCopy(codeExamples[fw.id])}
                    >
                      Copy
                    </Button>
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