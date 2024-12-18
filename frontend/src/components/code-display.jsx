"use client"

import Editor from "@monaco-editor/react"
import { Card } from "@/components/ui/card"

export function CodeDisplay() {
  const codeExample = `class ActionWhitelistValidator(BaseValidator):
    def __init__(self, allowed_actions):
        super().__init__("action_whitelist")
        self.allowed = set(allowed_actions)
    
    def validate(self, context):
        action = context.get("action")
        if action not in self.allowed:
            return ValidationResult(False, 
                                 f"Action '{action}' not allowed", 
                                 self.name, 
                                 ValidationPoint.PRE_ACTION, 
                                 context)
        return ValidationResult(True, 
                              f"Action '{action}' is allowed",
                              self.name,
                              ValidationPoint.PRE_ACTION,
                              context)`

  // Calculate height based on number of lines (approximately 20px per line)
  const numberOfLines = codeExample.split('\n').length
  const editorHeight = `${numberOfLines * 22}px` // 22px per line to account for line spacing

  return (
    <Card className="overflow-hidden border border-[#333] rounded-xl bg-[#1e1e1e] shadow-2xl mb-8">
      <div className="flex items-center gap-2 bg-[#1e1e1e] px-4 py-2 border-b border-[#333]">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-[#ff5f57]"></div>
          <div className="w-3 h-3 rounded-full bg-[#febc2e]"></div>
          <div className="w-3 h-3 rounded-full bg-[#28c840]"></div>
        </div>
        <div className="text-xs text-gray-400 ml-2">validator.py</div>
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