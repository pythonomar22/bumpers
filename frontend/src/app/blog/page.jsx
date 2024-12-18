import { SiteHeader } from "@/components/site-header"
import Link from "next/link"

export default function Blog() {
  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main className="container py-24">
        <div className="grid grid-cols-1 gap-8 max-w-sm">
          <BlogCard
            title="Introducing Bumpers: Safety Guardrails for AI Agents"
            description="Learn how Bumpers helps you build safer and more reliable AI agents with built-in guardrails and validation."
            date="March 20, 2024"
            href="/blog/introducing-bumpers"
          />
        </div>
      </main>
    </div>
  )
}

function BlogCard({ title, description, date, href }) {
  return (
    <div className="rounded-lg border border-border/40 bg-card/50 p-6 hover:border-border transition-colors">
      <p className="text-sm text-muted-foreground mb-3">{date}</p>
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p className="text-muted-foreground mb-4">{description}</p>
      <Link href={href} className="text-sm font-medium hover:underline">
        Read more →
      </Link>
    </div>
  )
} 