import { Card } from "@/components/ui/card"
import { SiOpenai, SiLangchain } from 'react-icons/si'
import { TbBrain } from 'react-icons/tb'
import { GiArtificialIntelligence } from 'react-icons/gi'
import { BsRobot } from 'react-icons/bs'

export function FrameworkSupport() {
  const frameworks = [
    { 
      name: "LangChain", 
      icon: <SiLangchain className="w-8 h-8 text-[#00A3A3]" />,
      description: "Build LLM-powered applications with safety"
    },
    { 
      name: "OpenAI", 
      icon: <SiOpenai className="w-8 h-8 text-[#00A67E]" />,
      description: "Secure integration with OpenAI models"
    },
    { 
      name: "Anthropic", 
      icon: <TbBrain className="w-8 h-8 text-[#9B8AFB]" />,
      description: "Safe interactions with Claude and other models"
    },
    { 
      name: "LlamaIndex", 
      icon: <GiArtificialIntelligence className="w-8 h-8 text-[#FF4B4B]" />,
      description: "Structured data handling with guardrails"
    },
    { 
      name: "Mistral", 
      icon: <BsRobot className="w-8 h-8 text-[#7A88FB]" />,
      description: "Enhanced safety for Mistral models"
    }
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
              <div key={index} className="text-center group">
                <div className="w-16 h-16 rounded-full bg-background/50 p-3 mb-3 mx-auto relative backdrop-blur-sm 
                              transition-all duration-200 group-hover:bg-background/80">
                  <div className="w-full h-full flex items-center justify-center">
                    {framework.icon}
                  </div>
                </div>
                <p className="text-sm font-medium mb-1">{framework.name}</p>
                <p className="text-xs text-muted-foreground max-w-[150px] opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  {framework.description}
                </p>
              </div>
            ))}
          </div>
          <div className="absolute top-1/2 left-[20%] right-[20%] border-t border-primary/20 -z-10" />
        </div>
      </Card>
    </div>
  )
} 