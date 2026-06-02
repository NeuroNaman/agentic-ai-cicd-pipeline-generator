"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Eye, EyeOff, Terminal } from "lucide-react";

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    // For now sign in with credentials (extend with DB later)
    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });
    if (result?.error) {
      setError("Invalid credentials. Use demo@ciforge.dev / demo123 to try the demo.");
      setLoading(false);
    } else {
      router.push("/dashboard");
    }
  }

  const features = [
    {
      icon: "⚡",
      title: "Generate pipelines in seconds",
      desc: "Paste any GitHub URL. Get a production-ready CI/CD pipeline instantly.",
      color: "rgba(139,92,246,0.1)",
      border: "rgba(139,92,246,0.2)",
    },
    {
      icon: "🔍",
      title: "AI detects your full stack",
      desc: "Languages, frameworks, Docker, Kubernetes — detected automatically.",
      color: "rgba(6,182,212,0.1)",
      border: "rgba(6,182,212,0.2)",
    },
    {
      icon: "✅",
      title: "Validated before you ship",
      desc: "4-layer validation: syntax, semantics, security, dry-run.",
      color: "rgba(16,185,129,0.1)",
      border: "rgba(16,185,129,0.2)",
    },
    {
      icon: "🔄",
      title: "Self-healing on failure",
      desc: "Auto-diagnoses errors and generates fixes. Up to 3 retries.",
      color: "rgba(245,158,11,0.1)",
      border: "rgba(245,158,11,0.2)",
    },
  ];

  return (
    <div
      className="min-h-screen grid grid-cols-1 lg:grid-cols-2"
      style={{ background: "var(--bg)" }}
    >
      {/* LEFT — FORM */}
      <div className="flex items-center justify-center p-8 lg:p-16 relative">
        <div className="absolute inset-0 grid-bg opacity-50" />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse at 30% 50%, rgba(139,92,246,0.06) 0%, transparent 70%)",
          }}
        />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-[400px] relative z-10"
        >
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 mb-12 no-underline">
            <div
              className="w-9 h-9 rounded-[9px] flex items-center justify-center text-base"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
            >
              ⚡
            </div>
            <span
              className="text-xl font-bold tracking-tight"
              style={{ fontFamily: "var(--font-display)", color: "var(--text)" }}
            >
              CIForge
            </span>
          </Link>

          <h1
            className="text-3xl font-bold tracking-tight mb-2"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Create your account
          </h1>
          <p className="text-[15px] font-light mb-10" style={{ color: "var(--text2)" }}>
            Start generating pipelines for free
          </p>

          {/* Demo hint */}
          <div
            className="flex items-center gap-3 px-4 py-3 rounded-xl mb-6"
            style={{
              background: "rgba(139,92,246,0.06)",
              border: "1px solid rgba(139,92,246,0.15)",
            }}
          >
            <Terminal size={14} style={{ color: "var(--purple2)", flexShrink: 0 }} />
            <p
              className="text-xs"
              style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
            >
              Demo: <span style={{ color: "var(--purple2)" }}>demo@ciforge.dev</span>{" "}
              / <span style={{ color: "var(--purple2)" }}>demo123</span>
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSignup} className="flex flex-col gap-4">
            {error && (
              <div
                className="p-3 rounded-lg text-sm text-center"
                style={{
                  background: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.2)",
                  color: "#ef4444",
                }}
              >
                {error}
              </div>
            )}

            {/* Name */}
            <div>
              <label
                className="block text-xs mb-2"
                style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
              >
                Full name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
                className="w-full px-4 py-3 rounded-[9px] text-sm outline-none transition-all"
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  color: "var(--text)",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = "var(--purple)";
                  e.currentTarget.style.boxShadow = "0 0 0 3px rgba(139,92,246,0.1)";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = "var(--border)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              />
            </div>

            {/* Email */}
            <div>
              <label
                className="block text-xs mb-2"
                style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
              >
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                className="w-full px-4 py-3 rounded-[9px] text-sm outline-none transition-all"
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  color: "var(--text)",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = "var(--purple)";
                  e.currentTarget.style.boxShadow = "0 0 0 3px rgba(139,92,246,0.1)";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = "var(--border)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              />
            </div>

            {/* Password */}
            <div>
              <label
                className="block text-xs mb-2"
                style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
              >
                Password
              </label>
              <div className="relative">
                <input
                  type={showPass ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 characters"
                  required
                  minLength={8}
                  className="w-full px-4 py-3 pr-11 rounded-[9px] text-sm outline-none transition-all"
                  style={{
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    color: "var(--text)",
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = "var(--purple)";
                    e.currentTarget.style.boxShadow = "0 0 0 3px rgba(139,92,246,0.1)";
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = "var(--border)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{
                    color: "var(--text3)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-[10px] text-[15px] font-medium text-white mt-1 disabled:opacity-60 flex items-center justify-center gap-2"
              style={{
                background: "linear-gradient(135deg, var(--purple), var(--indigo))",
                border: "none",
                cursor: "pointer",
                boxShadow: "0 0 30px rgba(139,92,246,0.25)",
              }}
            >
              {loading ? (
                <span
                  className="w-4 h-4 border-2 rounded-full animate-spin"
                  style={{
                    borderColor: "rgba(255,255,255,0.3)",
                    borderTopColor: "white",
                  }}
                />
              ) : (
                <>
                  Create CIForge account
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Sign in link */}
          <p className="text-center mt-6 text-sm" style={{ color: "var(--text3)" }}>
            Already have an account?{" "}
            <Link
              href="/login"
              className="transition-colors"
              style={{ color: "var(--purple2)" }}
            >
              Sign in
            </Link>
          </p>

          <p
            className="text-center mt-4 text-xs leading-relaxed"
            style={{ color: "var(--text3)" }}
          >
            By creating an account you agree to our{" "}
            <Link href="/terms" className="underline">
              Terms
            </Link>{" "}
            and{" "}
            <Link href="/privacy" className="underline">
              Privacy Policy
            </Link>
          </p>
        </motion.div>
      </div>

      {/* RIGHT — FEATURE PANEL */}
      <div
        className="hidden lg:flex flex-col justify-center p-16 relative overflow-hidden"
        style={{
          background: "var(--surface)",
          borderLeft: "1px solid var(--border)",
        }}
      >
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse at 70% 30%, rgba(139,92,246,0.08) 0%, transparent 60%)",
          }}
        />

        <div className="relative z-10">
          {/* Live badge */}
          <div
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs mb-12"
            style={{
              background: "rgba(16,185,129,0.1)",
              border: "1px solid rgba(16,185,129,0.25)",
              color: "#10b981",
              fontFamily: "var(--font-mono)",
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: "#10b981", animation: "pulse-dot 1.5s infinite" }}
            />
            Open Source · Free Forever
          </div>

          <p
            className="text-xs mb-12 tracking-widest uppercase"
            style={{ color: "var(--purple2)", fontFamily: "var(--font-mono)" }}
          >
            // what you get for free
          </p>

          <div className="flex flex-col gap-8 mb-12">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.15, duration: 0.5 }}
                className="flex gap-4 items-start"
              >
                <div
                  className="w-10 h-10 rounded-[10px] flex items-center justify-center text-lg flex-shrink-0 mt-0.5"
                  style={{ background: f.color, border: `1px solid ${f.border}` }}
                >
                  {f.icon}
                </div>
                <div>
                  <div
                    className="text-base font-semibold mb-1 tracking-tight"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {f.title}
                  </div>
                  <p
                    className="text-sm font-light leading-relaxed"
                    style={{ color: "var(--text2)" }}
                  >
                    {f.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Mini terminal */}
          <div
            className="rounded-xl overflow-hidden"
            style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
          >
            <div
              className="flex items-center gap-2 px-4 py-2.5"
              style={{
                background: "var(--surface2)",
                borderBottom: "1px solid var(--border)",
              }}
            >
              {["#ff5f57", "#ffbd2e", "#28ca41"].map((c) => (
                <div key={c} className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
              ))}
            </div>
            <div
              className="p-4 text-xs leading-7"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              <div style={{ color: "var(--purple2)" }}>
                ❯{" "}
                <span style={{ color: "var(--text)" }}>
                  ciforge generate github.com/user/api
                </span>
              </div>
              <div style={{ color: "var(--cyan)" }}>  Analyzing repository...</div>
              <div style={{ color: "#10b981" }}>  ✓ Python · FastAPI · Docker · pytest</div>
              <div style={{ color: "#10b981" }}>  ✓ Pipeline generated · Validated</div>
              <div style={{ color: "var(--text3)" }}>
                  → .github/workflows/ci-cd.yml
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}