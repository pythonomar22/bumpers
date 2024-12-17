"use client"

import Image from "next/image"
import { SiOpenai, SiLangchain } from 'react-icons/si'

export function FrameworkSupport() {
  const frameworks = [
    { 
      name: "LangChain", 
      icon: <SiLangchain className="w-12 h-12 text-[#00ABAB]" /> 
    },
    { 
      name: "OpenAI", 
      icon: <SiOpenai className="w-12 h-12 text-white" /> 
    },
    { 
      name: "Anthropic", 
      icon: <Image 
              src="/anthropic.png" 
              alt="Anthropic" 
              width={48} 
              height={48} 
              className="object-contain"
            /> 
    },
    { 
      name: "LlamaIndex", 
      icon: <Image 
              src="/llamaindex.jpeg" 
              alt="LlamaIndex" 
              width={48} 
              height={48} 
              className="object-contain"
            /> 
    },
    { 
      name: "Mistral", 
      icon: <Image 
              src="/mistral.webp" 
              alt="Mistral" 
              width={48} 
              height={48} 
              className="object-contain"
            /> 
    },
  ]

  return (
    <section className="py-24">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">
          Support for your Favorite Framework + LLM
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          {frameworks.map((framework) => (
            <div
              key={framework.name}
              className="flex flex-col items-center justify-center gap-4 p-6 rounded-lg bg-[#111] hover:bg-[#222] transition-colors"
            >
              {framework.icon}
              <span className="text-sm text-gray-400">{framework.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
} 