import Image from "next/image"
import { Card } from "@/components/ui/card"

export function FrameworkSupport() {
  const frameworks = [
    { name: "LangChain", logo: "/logos/langchain.svg" },
    { name: "OpenAI", logo: "/logos/openai.svg" },
    { name: "Anthropic", logo: "/logos/anthropic.svg" },
    { name: "LlamaIndex", logo: "/logos/llamaindex.svg" },
    { name: "Mistral", logo: "/logos/mistral.svg" }
  ]

  return (
    <div className="container py-24">
      <h2 className="text-3xl font-bold text-center mb-12">
        Support for your Favorite Framework + LLM
      </h2>
      <Card className="p-8 bg-card/50">
        <div className="relative">
          <div className="flex justify-center items-center gap-12 flex-wrap">
            {frameworks.map((framework, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 rounded-full bg-background p-2 mb-2 mx-auto relative">
                  <div className="w-full h-full bg-gray-800 rounded-full flex items-center justify-center">
                    {framework.name[0]}
                  </div>
                </div>
                <p className="text-sm font-medium">{framework.name}</p>
              </div>
            ))}
          </div>
          <div className="absolute top-1/2 left-[20%] right-[20%] border-t border-primary/20 -z-10" />
        </div>
      </Card>
    </div>
  )
} 