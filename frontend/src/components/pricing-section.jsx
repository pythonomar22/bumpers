"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Check } from 'lucide-react'

export function PricingSection() {
  const plans = [
    {
      name: "Basic",
      price: "$0",
      description: "free forever for personal use",
      features: [
        "Basic validation suite (Action & Content)",
        "5,000 validator calls/month",
        "Local validation engine",
        "Single environment",
        "Community support",
        "7-day validation logs retention",
        "Basic analytics dashboard"
      ]
    },
    {
      name: "Pro",
      price: "$10",
      description: "for building AI applications",
      features: [
        "Everything in Developer, plus:",
        "100,000 validator calls/month",
        "Advanced validators (Semantic Drift, etc)",
        "Custom validation rules & policies",
        "Multiple environments (dev/staging/prod)",
        "Priority email & Discord support",
        "30-day validation logs retention",
        "Advanced analytics & monitoring",
        "Collaborative policy management"
      ]
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "for organizations requiring maximum control",
      features: [
        "Everything in Team, plus:",
        "Unlimited validator calls",
        "Custom validator development",
        "RBAC & SSO integration",
        "Compliance templates (SOC2, HIPAA)",
        "CI/CD pipeline integration",
        "Dedicated support manager",
        "1-year validation logs retention",
        "On-premises deployment option"
      ]
    }
  ]

  return (
    <section id="pricing" className="py-24 bg-background">
      <div className="container">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl font-bold">Plans & Pricing</h2>
          <p className="text-muted-foreground max-w-[600px] mx-auto">
            Choose the right plan for your AI agent safety needs
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <Card key={index} className="relative p-8 bg-card/50">
              <div className="space-y-6">
                <div className="space-y-2">
                  <h3 className="text-xl font-bold">{plan.name}</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    {plan.price !== "Custom" && <span className="text-muted-foreground">/month</span>}
                  </div>
                  <p className="text-sm text-muted-foreground">{plan.description}</p>
                </div>
                
                <div className="space-y-4">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-primary shrink-0" />
                      <span className="text-sm text-muted-foreground">{feature}</span>
                    </div>
                  ))}
                </div>

                <Button 
                  className="w-full" 
                  variant={index === 1 ? "default" : "outline"}
                >
                  {index === 2 ? "Contact Sales" : "Get Started"}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
} 