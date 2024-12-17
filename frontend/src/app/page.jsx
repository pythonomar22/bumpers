import { SiteHeader } from "@/components/site-header"
import { HeroSection } from "@/components/hero-section"
import { FeaturesGrid } from "@/components/features-grid"
import { FrameworkSupport } from "@/components/framework-support"
import { PricingSection } from "@/components/pricing-section"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main>
        <HeroSection />
        <FeaturesGrid />
        <FrameworkSupport />
        <PricingSection />
      </main>
    </div>
  )
}
