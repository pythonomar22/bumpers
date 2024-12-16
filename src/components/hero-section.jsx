"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Globe, Code2, Terminal } from 'lucide-react'

export function HeroSection() {
  return (
    <div className="container px-4 py-24">
      <div className="flex flex-col items-center text-center space-y-8 mb-12">
        <h1 className="text-5xl font-bold tracking-tight">
          Guardrails for AI Agents
        </h1>
        <p className="text-xl text-muted-foreground max-w-[750px]">
          A powerful validation and safety framework that ensures AI agents operate within defined boundaries and ethical guidelines.
        </p>
        <div className="flex items-center space-x-4">
          <Button size="lg">Get Started</Button>
          <Button variant="outline" size="lg">Watch Demo</Button>
        </div>
      </div>

      <Card className="w-full max-w-4xl mx-auto">
        <Tabs defaultValue="python" className="w-full">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="python">
              <Terminal className="mr-2 h-4 w-4" />
              Python
            </TabsTrigger>
            <TabsTrigger value="typescript">
              <Code2 className="mr-2 h-4 w-4" />
              TypeScript
            </TabsTrigger>
            <TabsTrigger value="rest">
              <Globe className="mr-2 h-4 w-4" />
              REST API
            </TabsTrigger>
          </TabsList>
          <TabsContent value="python" className="p-6 bg-black rounded-b-lg">
            <pre className="text-sm text-green-400">
              <code>{`from guardrails import Validator, ValidationResult
from guardrails.validators import ActionWhitelist

# Initialize the validator
validator = Validator(
    validators=[
        ActionWhitelist(allowed_actions=["search", "analyze", "summarize"])
    ]
)

# Example function with guardrails
@validator.validate
def safe_agent_action(action, params):
    """Execute an action with safety guardrails."""
    # Your agent logic here
    return {"status": "success", "action": action}`}</code>
            </pre>
          </TabsContent>
          <TabsContent value="typescript" className="p-6 bg-black rounded-b-lg">
            {/* TypeScript example would go here */}
          </TabsContent>
          <TabsContent value="rest" className="p-6 bg-black rounded-b-lg">
            {/* REST API example would go here */}
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
} 