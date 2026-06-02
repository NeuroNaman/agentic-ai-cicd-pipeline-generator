"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Star } from "lucide-react";

const TERMINAL_LINES = [
  { type: "dim", text: "" },
  { type: "info", text: "  Cloning repository..." },
  { type: "dim", text: "  ✓ Cloned in 2.3s" },
  { type: "dim", text: "" },
  { type: "info", text: "  [1/4] Repo Analysis Agent" },
  { type: "success", text: "  ✓ Detected: Python 98.8%, Shell 1.2%" },
  { type: "success", text: "  ✓ Framework: Flask, FastAPI" },
  { type: "success", text: "  ✓ Docker: multi-stage build detected" },
  { type: "success", text: "  ✓ Tests: pytest" },
  { type: "dim", text: "" },
  { type: "info", text: "  [2/4] Planner Agent" },
  { type: "success", text: "  ✓ Platform: GitHub Actions" },
  { type: "success", text: "  ✓ Stages: install → lint → test → docker" },
  { type: "dim", text: "" },
  { type: "info", text: "  [3/4] Pipeline Generator Agent" },
  { type: "success", text: "  ✓ Generated: .github/workflows/ci-cd.yml" },
  { type: "dim", text: "" },
  { type: "info", text: "  [4/4] Validation Agent" },
  { type: "success", text: "  ✓ Syntax valid · Semantic valid" },
  { type: "success", text: "  ✓ Security passed · 0 issues" },
  { type: "dim", text: "" },
  { type: "success", text: "  ✓ Pipeline generated in 2.56s" },
];

const LINE_COLORS: Record<string, string> = {
  dim: "var(--text3)",
  info: "var(--cyan)",
  success: "#10b981",
  prompt: "var(--purple2)",
};

export function Hero() {
  const outputRef = useRef<HTMLDivElement>(null);
  const lineIdx = useRef(0);
  const timer = useRef<NodeJS.Timeout>();

  function addLine() {
    const el = outputRef.current;
    if (!el) return;

    if (lineIdx.current >= TERMINAL_LINES.length) {
      setTimeout(() => {
        el.innerHTML =
          '<span style="color:var(--purple2)">❯ </span><span style="color:var(--text)">ciforge generate github.com/pallets/flask --auto-approve</span>';
        lineIdx.current = 0;
        timer.current = setTimeout(addLine, 800);
      }, 3000);
      return;
    }

    const line = TERMINAL_LINES[lineIdx.current];
    const span = document.createElement("span");
    span.style.display = "block";
    span.style.color = LINE_COLORS[line.type] || "var(--text)";
    span.textContent = line.text;
    el.appendChild(span);
    el.scrollTop = el.scrollHeight;
    lineIdx.current++;

    const delay = lineIdx.current < 3 ? 400 : 120;
    timer.current = setTimeout(addLine, delay);
  }

  useEffect(() => {
    timer.current = setTimeout(addLine, 1200);
    return () => clearTimeout(timer.current);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center pt-32 pb-20">
      <div className="absolute inset-0 grid-bg" />

      <div className="max-w-[1200px] mx-auto px-6 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
          {/* LEFT */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs mb-7"
              style={{
                background: "rgba(139,92,246,0.1)",
                border: "1px solid rgba(139,92,246,0.3)",
                color: "var(--purple2)",
                fontFamily: "var(--font-mono)",
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: "var(--green)", animation: "pulse-dot 2s infinite" }}
              />
              Open Source · Free Forever
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="font-bold leading-[1.05] mb-6"
              style={{
                fontFamily: "var(--font-display)",
                fontSize: "clamp(42px, 5vw, 68px)",
                letterSpacing: "-2px",
              }}
            >
              Your AI<br />
              <span className="gradient-text">DevOps Engineer</span><br />
              on autopilot
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-lg font-light leading-relaxed mb-10 max-w-[480px]"
              style={{ color: "var(--text2)" }}
            >
              CIForge analyzes any GitHub repository and generates
              production-ready CI/CD pipelines in seconds. No DevOps expertise required.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex items-center gap-4 mb-14"
            >
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-[15px] font-medium text-white no-underline transition-all"
                style={{
                  background: "linear-gradient(135deg, #8b5cf6, #6366f1)",
                  boxShadow: "0 0 40px rgba(139,92,246,0.3)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.transform = "translateY(-2px)";
                  (e.currentTarget as HTMLAnchorElement).style.boxShadow = "0 0 60px rgba(139,92,246,0.4)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.transform = "translateY(0)";
                  (e.currentTarget as HTMLAnchorElement).style.boxShadow = "0 0 40px rgba(139,92,246,0.3)";
                }}
              >
                ⚡ Start generating free
                <ArrowRight size={16} />
              </Link>

              <a
                href="https://github.com/NeuroNaman"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-[15px] no-underline transition-all"
                style={{
                  border: "1px solid var(--border2)",
                  color: "var(--text2)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.color = "var(--text)";
                  (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--purple)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)";
                  (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--border2)";
                }}
              >
                <Star size={15} />
                Star on GitHub
              </a>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="flex gap-10"
            >
              {[
                { num: "64/64", label: "Test checks passing" },
                { num: "<5s", label: "Avg generation time" },
                { num: "3+", label: "CI/CD platforms" },
              ].map((s) => (
                <div key={s.label}>
                  <div
                    className="text-[28px] font-bold tracking-tight mb-1"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {s.num}
                  </div>
                  <div className="text-xs" style={{ color: "var(--text3)" }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* RIGHT — Terminal */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            {/* Floating badges */}
            <div
              className="absolute -top-5 right-10 px-3 py-1.5 rounded-lg text-xs z-10"
              style={{
                background: "rgba(16,185,129,0.1)",
                border: "1px solid rgba(16,185,129,0.3)",
                color: "#10b981",
                fontFamily: "var(--font-mono)",
                animation: "float 3s ease-in-out infinite",
              }}
            >
              ✓ Validation passed
            </div>
            <div
              className="absolute -bottom-5 left-10 px-3 py-1.5 rounded-lg text-xs z-10"
              style={{
                background: "rgba(139,92,246,0.1)",
                border: "1px solid rgba(139,92,246,0.3)",
                color: "var(--purple2)",
                fontFamily: "var(--font-mono)",
                animation: "float 3s ease-in-out infinite 1.5s",
              }}
            >
              ↓ Jenkinsfile · GitLab CI · GHA
            </div>

            {/* Terminal */}
            <div
              className="rounded-2xl overflow-hidden"
              style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
                boxShadow: "0 0 80px rgba(139,92,246,0.1), 0 40px 80px rgba(0,0,0,0.5)",
              }}
            >
              {/* Terminal header */}
              <div
                className="flex items-center gap-3 px-5 py-3.5"
                style={{ background: "var(--surface2)", borderBottom: "1px solid var(--border)" }}
              >
                <div className="flex gap-1.5">
                  {["#ff5f57", "#ffbd2e", "#28ca41"].map((c) => (
                    <div key={c} className="w-3 h-3 rounded-full" style={{ background: c }} />
                  ))}
                </div>
                <span
                  className="text-xs ml-2"
                  style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
                >
                  ciforge — generate pipeline
                </span>
              </div>

              {/* Terminal body */}
              <div className="p-6 min-h-[320px] overflow-y-auto" style={{ maxHeight: "340px" }}>
                <div
                  className="text-[13px] leading-[1.8]"
                  style={{ fontFamily: "var(--font-mono)" }}
                >
                  <span style={{ color: "var(--purple2)" }}>❯ </span>
                  <span style={{ color: "var(--text)" }}>
                    ciforge generate github.com/pallets/flask --auto-approve
                  </span>
                </div>
                <div
                  ref={outputRef}
                  className="text-[13px] leading-[1.8] mt-1 overflow-y-auto"
                  style={{ fontFamily: "var(--font-mono)" }}
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
