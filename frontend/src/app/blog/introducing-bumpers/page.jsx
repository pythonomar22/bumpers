import { SiteHeader } from "@/components/site-header"

export default function BlogPost() {
  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main className="container py-24 max-w-3xl">
        <article className="prose prose-invert">
          <p className="text-sm text-muted-foreground">March 20, 2024</p>
          <h1 className="text-4xl font-bold mt-2 mb-8">Introducing Bumpers: Safety Guardrails for AI Agents</h1>
          {/* Content will go here */}
        </article>
      </main>
    </div>
  )
} 