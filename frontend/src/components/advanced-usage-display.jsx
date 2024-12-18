"use client"

import Editor from "@monaco-editor/react"
import { Card } from "@/components/ui/card"

export function AdvancedUsageDisplay() {
  const codeExample = `from bumpers.validators.semantic import SemanticDriftValidator
from bumpers.monitoring.monitor import BumpersMonitor
from bumpers.monitoring.conditions import (
    create_high_failure_rate_condition,
    create_repeated_intervention_condition
)

# Add a semantic drift validator
def mock_embedding_model(text: str) -> np.ndarray:
    # Dummy embeddings, replace with a real model call
    import numpy as np
    return np.random.rand(384)

semantic_validator = SemanticDriftValidator(
    embedding_model=mock_embedding_model,
    similarity_threshold=0.7
)

cve.register_validator(semantic_validator, ValidationPoint.PRE_OUTPUT)

# Setup a monitor for alerts
monitor = BumpersMonitor(
    logger=logger,
    alert_handlers=[lambda m: print("ALERT:", m)],
    check_interval=60
)
monitor.add_condition(create_high_failure_rate_condition(threshold=0.3))
monitor.add_condition(create_repeated_intervention_condition(action="wikipedia", count=2))
monitor.start()

# Now you have continuous monitoring, alerts, and richer validations in place.`

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
        <div className="text-xs text-gray-400 ml-2">advanced_example.py</div>
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