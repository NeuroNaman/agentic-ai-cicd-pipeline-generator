"use client";
// ─── LOGOS STRIP ──────────────────────────────────────────────────────────────
export function LogosStrip() {
  const logos = [
    { icon: "🐙", label: "GitHub Actions" },
    { icon: "🦊", label: "GitLab CI" },
    { icon: "⚙️", label: "Jenkins" },
    { icon: "🐳", label: "Docker" },
    { icon: "☸️", label: "Kubernetes" },
    { icon: "🔷", label: "Terraform" },
  ];
  return (
    <div className="relative z-10 py-10"
      style={{ borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
      <div className="max-w-[1200px] mx-auto px-6">
        <p className="text-center text-xs mb-8 tracking-widest"
          style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
          WORKS WITH YOUR ENTIRE STACK
        </p>
        <div className="flex items-center justify-center gap-12 flex-wrap">
          {logos.map((l) => (
            <div key={l.label} className="flex items-center gap-2.5 cursor-default"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)", fontSize: "15px" }}>
              <span className="w-7 h-7 rounded-lg flex items-center justify-center text-sm"
                style={{ background: "rgba(255,255,255,0.04)" }}>{l.icon}</span>
              {l.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── HOW IT WORKS ─────────────────────────────────────────────────────────────
export function HowItWorks() {
  const steps = [
    { num: "01", icon: "🔗", title: "Paste your repo URL",
      desc: "Drop any GitHub URL. CIForge clones it and performs a deep scan of your entire codebase structure instantly." },
    { num: "02", icon: "🤖", title: "AI analyzes everything",
      desc: "Four specialized AI agents detect your languages, frameworks, Docker configs, Kubernetes manifests, and existing CI/CD setups automatically." },
    { num: "03", icon: "⚡", title: "Download your pipeline",
      desc: "Get a production-ready, validated CI/CD configuration file. Syntax checked, security scanned, and ready to commit." },
  ];
  return (
    <section id="how-it-works" className="relative z-10 py-24">
      <div className="max-w-[1200px] mx-auto px-6">
        <p className="text-xs mb-4"
          style={{ color: "var(--purple)", fontFamily: "var(--font-mono)", letterSpacing: "0.15em" }}>
          // how it works
        </p>
        <h2 className="font-bold leading-tight mb-4"
          style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px,4vw,52px)", letterSpacing: "-1.5px" }}>
          From repo URL to pipeline in <span className="gradient-text">3 steps</span>
        </h2>
        <p className="text-lg font-light leading-relaxed mb-16 max-w-[560px]" style={{ color: "var(--text2)" }}>
          No DevOps expertise needed. CIForge handles everything from analysis to generation to validation.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-[2px] rounded-2xl overflow-hidden"
          style={{ background: "var(--border)", border: "1px solid var(--border)" }}>
          {steps.map((step) => (
            <div key={step.num} className="relative p-12"
              style={{ background: "var(--surface)" }}>
              <div className="absolute top-5 right-6 font-bold leading-none"
                style={{ fontFamily: "var(--font-display)", fontSize: "80px", color: "rgba(139,92,246,0.06)", letterSpacing: "-4px" }}>
                {step.num}
              </div>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-xl mb-6"
                style={{ background: "rgba(139,92,246,0.1)", border: "1px solid rgba(139,92,246,0.2)" }}>
                {step.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3 tracking-tight"
                style={{ fontFamily: "var(--font-display)" }}>{step.title}</h3>
              <p className="text-sm font-light leading-relaxed" style={{ color: "var(--text2)" }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── FEATURES ─────────────────────────────────────────────────────────────────
export function Features() {
  const features = [
    { icon: "🔍", iconBg: "rgba(139,92,246,0.1)", iconBorder: "rgba(139,92,246,0.2)",
      title: "Intelligent Repo Analysis", desc: "Detects 15+ languages, 20+ frameworks, all package managers, Docker configs, Kubernetes manifests, and existing CI/CD setups automatically." },
    { icon: "📋", iconBg: "rgba(6,182,212,0.1)", iconBorder: "rgba(6,182,212,0.2)",
      title: "Strategic Planning", desc: "Determines optimal pipeline stages, deployment strategies (rolling, blue-green, canary), caching strategies, and environment configurations." },
    { icon: "⚙️", iconBg: "rgba(16,185,129,0.1)", iconBorder: "rgba(16,185,129,0.2)",
      title: "Pipeline Generation", desc: "Produces valid, production-ready CI/CD configs for GitHub Actions, GitLab CI, and Jenkins. Hybrid template + AI approach." },
    { icon: "✅", iconBg: "rgba(245,158,11,0.1)", iconBorder: "rgba(245,158,11,0.2)",
      title: "4-Layer Validation", desc: "Validates syntax, semantics, security (no hardcoded secrets), and runs a dry-run before handing you the file." },
    { icon: "🔄", iconBg: "rgba(239,68,68,0.1)", iconBorder: "rgba(239,68,68,0.2)",
      title: "Self-Healing", desc: "When pipelines fail, the Self-Healing agent classifies the error, diagnoses root cause, and auto-generates fixes with retry loops." },
    { icon: "👤", iconBg: "rgba(99,102,241,0.1)", iconBorder: "rgba(99,102,241,0.2)",
      title: "Human-in-the-Loop", desc: "Optional approval gates before deployment. Full control when you want it, full automation when you don't." },
  ];
  return (
    <section id="features" className="relative z-10 py-24" style={{ background: "var(--bg2)" }}>
      <div className="max-w-[1200px] mx-auto px-6">
        <p className="text-xs mb-4"
          style={{ color: "var(--purple)", fontFamily: "var(--font-mono)", letterSpacing: "0.15em" }}>
          // capabilities
        </p>
        <h2 className="font-bold leading-tight mb-4"
          style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px,4vw,52px)", letterSpacing: "-1.5px" }}>
          Everything a senior<br />DevOps engineer does
        </h2>
        <p className="text-lg font-light leading-relaxed mb-16 max-w-[560px]" style={{ color: "var(--text2)" }}>
          Built with LangGraph multi-agent orchestration. Each agent is a specialist.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="rounded-2xl p-8 relative overflow-hidden"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="w-11 h-11 rounded-[10px] flex items-center justify-center text-xl mb-5"
                style={{ background: f.iconBg, border: `1px solid ${f.iconBorder}` }}>{f.icon}</div>
              <h3 className="text-[17px] font-semibold mb-2.5 tracking-tight"
                style={{ fontFamily: "var(--font-display)" }}>{f.title}</h3>
              <p className="text-sm font-light leading-relaxed" style={{ color: "var(--text2)" }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── STATS ────────────────────────────────────────────────────────────────────
export function Stats() {
  const stats = [
    { num: "100%", label: "test_pass_rate" },
    { num: "64", label: "validation_checks" },
    { num: "15+", label: "languages_detected" },
    { num: "<5s", label: "avg_generation_time" },
  ];
  return (
    <div className="relative z-10 py-20"
      style={{ borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-[2px] rounded-2xl overflow-hidden"
          style={{ background: "var(--border)", border: "1px solid var(--border)" }}>
          {stats.map((s) => (
            <div key={s.label} className="text-center py-10" style={{ background: "var(--surface)" }}>
              <div className="text-[48px] font-bold tracking-tight mb-2"
                style={{ fontFamily: "var(--font-display)", letterSpacing: "-2px" }}>{s.num}</div>
              <div className="text-sm" style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── AGENTS ───────────────────────────────────────────────────────────────────
export function Agents() {
  const agents = [
    { icon: "🔍", bg: "rgba(139,92,246,0.1)", border: "rgba(139,92,246,0.2)",
      title: "Repo Analysis Agent",
      desc: "Deep repository inspection. Detects languages, frameworks, package managers, Docker, Kubernetes, Terraform, and existing CI/CD configs with zero configuration.",
      tag: "🔵 Always runs first", tagBg: "rgba(139,92,246,0.1)", tagColor: "var(--purple2)" },
    { icon: "📋", bg: "rgba(6,182,212,0.1)", border: "rgba(6,182,212,0.2)",
      title: "Planner Agent",
      desc: "Strategic pipeline architect. Selects the optimal CI/CD platform, determines pipeline stages, deployment strategy, secrets needed, and environment matrix.",
      tag: "🔵 Runs after analysis", tagBg: "rgba(6,182,212,0.1)", tagColor: "var(--cyan)" },
    { icon: "⚙️", bg: "rgba(16,185,129,0.1)", border: "rgba(16,185,129,0.2)",
      title: "Pipeline Generator Agent",
      desc: "Produces the actual YAML/Groovy config files. Uses a hybrid template + LLM approach to generate idiomatic, production-grade pipeline configurations.",
      tag: "🟢 Core output agent", tagBg: "rgba(16,185,129,0.1)", tagColor: "var(--green)" },
    { icon: "🛡️", bg: "rgba(239,68,68,0.1)", border: "rgba(239,68,68,0.2)",
      title: "Validation Agent",
      desc: "4-layer quality gate. Validates syntax, semantic correctness, scans for hardcoded secrets and permission issues. Nothing ships without passing all checks.",
      tag: "🔴 Quality gate", tagBg: "rgba(239,68,68,0.1)", tagColor: "#f87171" },
  ];
  return (
    <section id="agents" className="relative z-10 py-24">
      <div className="max-w-[1200px] mx-auto px-6">
        <p className="text-xs mb-4"
          style={{ color: "var(--purple)", fontFamily: "var(--font-mono)", letterSpacing: "0.15em" }}>
          // multi-agent system
        </p>
        <h2 className="font-bold leading-tight mb-4"
          style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px,4vw,52px)", letterSpacing: "-1.5px" }}>
          4 AI agents.<br />One perfect pipeline.
        </h2>
        <p className="text-lg font-light leading-relaxed mb-16 max-w-[560px]" style={{ color: "var(--text2)" }}>
          Orchestrated by LangGraph with conditional routing, retries, and checkpointing.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((a) => (
            <div key={a.title} className="flex gap-5 p-8 rounded-2xl"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                style={{ background: a.bg, border: `1px solid ${a.border}` }}>{a.icon}</div>
              <div>
                <h3 className="text-[17px] font-semibold mb-2 tracking-tight"
                  style={{ fontFamily: "var(--font-display)" }}>{a.title}</h3>
                <p className="text-sm font-light leading-relaxed mb-3" style={{ color: "var(--text2)" }}>{a.desc}</p>
                <span className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded"
                  style={{ background: a.tagBg, color: a.tagColor, fontFamily: "var(--font-mono)" }}>{a.tag}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── CTA ──────────────────────────────────────────────────────────────────────
export function CTA() {
  return (
    <section className="relative z-10 py-28">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="relative rounded-3xl p-20 text-center overflow-hidden"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <div className="absolute top-0 left-1/4 right-1/4 h-px"
            style={{ background: "linear-gradient(90deg, transparent, var(--purple), var(--indigo), transparent)" }} />
          <div className="absolute inset-0 pointer-events-none"
            style={{ background: "radial-gradient(ellipse at top center, rgba(139,92,246,0.05) 0%, transparent 60%)" }} />
          <p className="text-xs mb-4 relative"
            style={{ color: "var(--purple)", fontFamily: "var(--font-mono)", letterSpacing: "0.15em" }}>
            // get started
          </p>
          <h2 className="font-bold leading-tight mb-5 relative"
            style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px,4vw,52px)", letterSpacing: "-2px" }}>
            Ship pipelines.<br />Not boilerplate.
          </h2>
          <p className="text-lg font-light mb-10 relative" style={{ color: "var(--text2)" }}>
            Open source, free forever. No credit card. No DevOps expertise required.
          </p>
          <div className="flex items-center justify-center gap-4 relative">
            <a href="/dashboard"
              className="inline-flex items-center gap-2.5 px-9 py-4 rounded-xl text-base font-medium text-white no-underline"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)", boxShadow: "0 0 50px rgba(139,92,246,0.3)" }}>
              ⚡ Start generating free
            </a>
            <a href="https://github.com/NeuroNaman" target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2.5 px-9 py-4 rounded-xl text-base no-underline"
              style={{ border: "1px solid var(--border2)", color: "var(--text2)" }}>
              ★ View on GitHub
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
