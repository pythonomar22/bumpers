import Link from "next/link"
import { DiscordLogoIcon } from '@radix-ui/react-icons'
import { Github } from 'lucide-react'
import { Button } from "@/components/ui/button"

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-8">
          <Link href="/" className="font-bold text-xl">
            Guardrails
          </Link>
        </div>
        <nav className="flex items-center space-x-6 text-sm font-medium">
          <Link href="#" className="transition-colors hover:text-foreground/80">
            Get Started
          </Link>
          <Link href="#" className="transition-colors hover:text-foreground/80">
            How it Works
          </Link>
          <Link href="#" className="transition-colors hover:text-foreground/80">
            Features
          </Link>
          <Link href="#" className="transition-colors hover:text-foreground/80">
            Pricing
          </Link>
        </nav>
        <div className="ml-auto flex items-center space-x-4">
          <Button variant="ghost" size="icon">
            <DiscordLogoIcon className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Github className="h-5 w-5" />
          </Button>
          <Button variant="ghost">Docs</Button>
          <Button variant="ghost">Log in</Button>
          <Button>Sign up</Button>
        </div>
      </div>
    </header>
  )
} 