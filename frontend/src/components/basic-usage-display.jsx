"use client"

import Editor from "@monaco-editor/react"
import { Card } from "@/components/ui/card"

export function BasicUsageDisplay() {
  const codeExample = `from bumpers.core.engine import CoreValidationEngine, ValidationPoint
from bumpers.policy.parser import PolicyParser
from bumpers.integrations.react import GuardedReActAgent
from bumpers.logging.file_logger import FileLogger
from bumpers.validators.action import ActionWhitelistValidator
from bumpers.validators.content import ContentFilterValidator
from cerebras.cloud.sdk import Cerebras
import os

os.environ["CEREBRAS_API_KEY"] = "<your-api-key>"

# Initialize logger and validation engine
logger = FileLogger("logs")
cve = CoreValidationEngine(logger=logger)

# Load policies and create validators
parser = PolicyParser()
policy = parser.load_policy_file("./policies/react.yaml")
validators = parser.create_validators(policy)

for validator in validators:
    if isinstance(validator, ActionWhitelistValidator):
        cve.register_validator(validator, ValidationPoint.PRE_ACTION)
    elif isinstance(validator, ContentFilterValidator):
        cve.register_validator(validator, ValidationPoint.PRE_OUTPUT)

# Define known actions (tools)
from original_react import wikipedia, calculate
known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate
}

# Prompt
prompt = "Your agent instructions..."

# Wrap a Cerebras-powered chatbot with Bumpers
class CerebrasChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        self.client = Cerebras()

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        # Prepare messages and call Cerebras for inference
        all_messages = []
        if self.system:
            all_messages.append({"role": "system", "content": self.system})
        all_messages.extend(self.messages)
        
        response = self.client.chat.completions.create(
            messages=all_messages,
            model="llama3.3-70b"
        )
        result = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": result})
        return result

agent = GuardedReActAgent(
    validation_engine=cve,
    bot_class=CerebrasChatBot,
    prompt=prompt
)

# Run a test query
result = agent.query("What is 20 * 15?", known_actions)
print("Final Result:", result)`

  const numberOfLines = codeExample.split('\n').length
  const editorHeight = `${numberOfLines * 22}px`

  return (
    <Card className="overflow-hidden border border-[#333] rounded-xl bg-[#1e1e1e] shadow-2xl mb-8">
      <div className="flex items-center gap-2 bg-[#1e1e1e] px-4 py-2 border-b border-[#333]">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-[#ff5f57]"></div>
          <div className="w-3 h-3 rounded-full bg-[#febc2e]"></div>
          <div className="w-3 h-3 rounded-full bg-[#28c840]"></div>
        </div>
        <div className="text-xs text-gray-400 ml-2">basic_example.py</div>
      </div>
      
      <div className="p-5">
        <Editor
          height={editorHeight}
          defaultLanguage="python"
          defaultValue={codeExample}
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
            padding: { top: 0, bottom: 0 }
          }}
        />
      </div>
    </Card>
  )
} 