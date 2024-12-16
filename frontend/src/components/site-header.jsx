import Link from "next/link"
import { DiscordLogoIcon } from '@radix-ui/react-icons'
import { Github } from 'lucide-react'
import { Button } from "@/components/ui/button"

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="header-container flex h-16 items-center">
        <div className="flex items-center space-x-16">
          <Link href="/" className="font-bold text-xl">
            Guardrails
          </Link>
          <nav className="flex items-center space-x-8 text-sm font-medium">
            <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              Get Started
            </Link>
            <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              How it Works
            </Link>
            <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
          </nav>
        </div>
        <div className="ml-auto flex items-center space-x-6">
          <Button variant="ghost" size="icon" className="hover:bg-secondary">
            <DiscordLogoIcon className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="hover:bg-secondary">
            <Github className="h-5 w-5" />
          </Button>
          <Button variant="ghost" className="text-sm">Docs</Button>
          <Button variant="ghost" className="text-sm">Log in</Button>
          <Button className="text-sm bg-white text-black hover:bg-white/90">Sign up</Button>
        </div>
      </div>
    </header>
  )
} 