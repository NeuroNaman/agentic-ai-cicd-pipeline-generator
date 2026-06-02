import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Hero } from "@/components/landing/hero";
import { LogosStrip, HowItWorks, Features, Stats, Agents, CTA } from "@/components/landing/sections";
import { CodeDemo } from "@/components/landing/code-demo";
import { ParticleCanvas } from "@/components/ui/particle-canvas";

export default function HomePage() {
  return (
    <main className="relative min-h-screen bg-bg overflow-x-hidden">
      <ParticleCanvas />
      {/* Glow orbs */}
      <div className="fixed w-[600px] h-[600px] rounded-full pointer-events-none z-0"
        style={{ background: "rgba(139,92,246,0.07)", filter: "blur(120px)", top: "-200px", left: "-200px" }} />
      <div className="fixed w-[500px] h-[500px] rounded-full pointer-events-none z-0"
        style={{ background: "rgba(99,102,241,0.05)", filter: "blur(120px)", bottom: "200px", right: "-200px" }} />

      <Navbar />
      <Hero />
      <LogosStrip />
      <HowItWorks />
      <Features />
      <Stats />
      <Agents />
      <CodeDemo />
      <CTA />
      <Footer />
    </main>
  );
}
