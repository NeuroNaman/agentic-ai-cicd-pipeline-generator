"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Github, CheckCircle, XCircle, Loader2 } from "lucide-react";
import Link from "next/link";
import { PipelineViewer } from "@/components/dashboard/pipeline-viewer";

type Stage = "idle" | "generating" | "done" | "error";

const PLATFORMS = [
  { id: "github_actions", label: "GitHub Actions", icon: "🐙", file: ".github/workflows/ci-cd.yml" },
  { id: "gitlab_ci", label: "GitLab CI", icon: "🦊", file: ".gitlab-ci.yml" },
  { id: "jenkins", label: "Jenkins", icon: "⚙️", file: "Jenkinsfile" },
];

const AGENTS = [
  { label: "Repo Analysis Agent", desc: "Scanning languages, frameworks, Docker, K8s..." },
  { label: "Planner Agent", desc: "Determining stages, deployment strategy..." },
  { label: "Pipeline Generator Agent", desc: "Generating configuration files..." },
  { label: "Validation Agent", desc: "Syntax · Semantic · Security checks..." },
];

export default function GenerateNewPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [platform, setPlatform] = useState("github_actions");
  const [stage, setStage] = useState<Stage>("idle");
  const [currentAgent, setCurrentAgent] = useState(-1);
  const [doneAgents, setDoneAgents] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [sessionId, setSessionId] = useState("");
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!repoUrl.trim()) return;
    setStage("generating");
    setCurrentAgent(0);
    setDoneAgents([]);
    setError("");
    setResult(null);

    try {
      // Call our Next.js API route which proxies to FastAPI
      const res = await fetch("/api/pipelines/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: repoUrl.startsWith("http") ? repoUrl : `https://github.com/${repoUrl}`,
          platform,
          auto_approve: true,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Generation failed");

      setSessionId(data.session_id);

      // Poll for completion with animated agent steps
      for (let i = 0; i < AGENTS.length; i++) {
        setCurrentAgent(i);
        await new Promise((r) => setTimeout(r, 800 + Math.random() * 600));
        setDoneAgents((prev) => [...prev, i]);
      }

      // Get final status
      const statusRes = await fetch(`/api/pipelines/status/${data.session_id}`);
      const statusData = await statusRes.json();
      setResult(statusData);
      setStage("done");
    } catch (err: any) {
      setError(err.message || "Something went wrong");
      setStage("error");
    }
  }

  function reset() {
    setStage("idle");
    setCurrentAgent(-1);
    setDoneAgents([]);
    setResult(null);
    setError("");
  }

  const selectedPlatform = PLATFORMS.find((p) => p.id === platform)!;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back */}
      <Link
        href="/dashboard/pipelines"
        className="inline-flex items-center gap-2 text-sm mb-6 transition-colors"
        style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
      >
        <ArrowLeft size={14} />
        back to pipelines
      </Link>

      <h1
        className="text-[26px] font-bold tracking-tight mb-1"
        style={{ fontFamily: "var(--font-display)" }}
      >
        Generate Pipeline
      </h1>
      <p className="text-sm font-light mb-8" style={{ color: "var(--text2)" }}>
        Paste a GitHub repository URL and choose your target CI/CD platform.
      </p>

      <AnimatePresence mode="wait">
        {/* IDLE — INPUT FORM */}
        {stage === "idle" && (
          <motion.div
            key="form"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
          >
            <div
              className="rounded-2xl p-8"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              {/* URL input */}
              <div className="mb-6">
                <label
                  className="block text-xs mb-2"
                  style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
                >
                  // repository url
                </label>
                <div
                  className="flex items-center gap-3 px-4 py-3 rounded-xl"
                  style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
                  onClick={() => document.getElementById("repo-input")?.focus()}
                >
                  <Github size={16} style={{ color: "var(--text3)", flexShrink: 0 }} />
                  <input
                    id="repo-input"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                    placeholder="github.com/user/repo or paste full URL"
                    className="flex-1 bg-transparent text-sm outline-none"
                    style={{ color: "var(--text)", fontFamily: "var(--font-mono)" }}
                  />
                </div>
              </div>

              {/* Platform selector */}
              <div className="mb-8">
                <label
                  className="block text-xs mb-3"
                  style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
                >
                  // target platform
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {PLATFORMS.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setPlatform(p.id)}
                      className="p-4 rounded-xl text-center transition-all"
                      style={{
                        background: platform === p.id ? "rgba(139,92,246,0.1)" : "var(--bg)",
                        border: platform === p.id ? "1px solid var(--purple)" : "1px solid var(--border)",
                      }}
                    >
                      <div className="text-2xl mb-2">{p.icon}</div>
                      <div
                        className="text-xs"
                        style={{
                          fontFamily: "var(--font-mono)",
                          color: platform === p.id ? "var(--purple2)" : "var(--text2)",
                        }}
                      >
                        {p.label}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={!repoUrl.trim()}
                className="w-full py-3.5 rounded-xl text-[15px] font-medium text-white transition-all disabled:opacity-40 flex items-center justify-center gap-2"
                style={{
                  background: "linear-gradient(135deg, var(--purple), var(--indigo))",
                  boxShadow: "0 0 30px rgba(139,92,246,0.25)",
                }}
              >
                ⚡ Generate Pipeline
              </button>
            </div>
          </motion.div>
        )}

        {/* GENERATING */}
        {stage === "generating" && (
          <motion.div
            key="generating"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
          >
            <div
              className="rounded-2xl p-8"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              <div className="flex items-center gap-3 mb-2">
                <Loader2
                  size={20}
                  className="animate-spin"
                  style={{ color: "var(--purple2)" }}
                />
                <h2
                  className="text-lg font-semibold tracking-tight"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  Generating your pipeline...
                </h2>
              </div>
              <p
                className="text-sm mb-8 ml-8"
                style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
              >
                {repoUrl}
              </p>

              <div className="flex flex-col gap-0">
                {AGENTS.map((agent, i) => {
                  const isDone = doneAgents.includes(i);
                  const isActive = currentAgent === i && !isDone;
                  return (
                    <div
                      key={i}
                      className="flex items-start gap-4 py-4"
                      style={{
                        borderBottom:
                          i < AGENTS.length - 1 ? "1px solid var(--border)" : "none",
                      }}
                    >
                      <div className="mt-0.5 flex-shrink-0">
                        {isDone ? (
                          <CheckCircle size={18} style={{ color: "var(--green)" }} />
                        ) : isActive ? (
                          <Loader2
                            size={18}
                            className="animate-spin"
                            style={{ color: "var(--purple2)" }}
                          />
                        ) : (
                          <div
                            className="w-[18px] h-[18px] rounded-full border-2"
                            style={{ borderColor: "var(--border2)" }}
                          />
                        )}
                      </div>
                      <div>
                        <div
                          className="text-sm font-medium"
                          style={{
                            color: isDone
                              ? "var(--green)"
                              : isActive
                              ? "var(--purple2)"
                              : "var(--text3)",
                          }}
                        >
                          [{i + 1}/4] {agent.label}
                        </div>
                        {isActive && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-xs mt-1"
                            style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
                          >
                            {agent.desc}
                          </motion.div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}

        {/* DONE */}
        {stage === "done" && result && (
          <motion.div
            key="done"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Success banner */}
            <div
              className="flex items-center gap-3 p-4 rounded-xl mb-5"
              style={{
                background: "rgba(16,185,129,0.05)",
                border: "1px solid rgba(16,185,129,0.2)",
              }}
            >
              <CheckCircle size={20} style={{ color: "var(--green)" }} />
              <div>
                <div className="text-sm font-medium" style={{ color: "var(--green)" }}>
                  Pipeline generated successfully
                </div>
                <div
                  className="text-xs mt-0.5"
                  style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
                >
                  {selectedPlatform.file} · Validation passed · 0 issues
                </div>
              </div>
              <button
                onClick={reset}
                className="ml-auto text-xs px-3 py-1.5 rounded-lg transition-all"
                style={{
                  background: "var(--surface2)",
                  color: "var(--text2)",
                  fontFamily: "var(--font-mono)",
                  border: "1px solid var(--border)",
                }}
              >
                Generate another
              </button>
            </div>

            <PipelineViewer result={result} platform={platform} />
          </motion.div>
        )}

        {/* ERROR */}
        {stage === "error" && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div
              className="flex items-start gap-4 p-6 rounded-2xl"
              style={{ background: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.2)" }}
            >
              <XCircle size={22} style={{ color: "var(--red)", flexShrink: 0 }} />
              <div className="flex-1">
                <div className="font-semibold mb-1" style={{ color: "var(--red)" }}>
                  Generation failed
                </div>
                <p className="text-sm mb-4" style={{ color: "var(--text2)" }}>
                  {error}
                </p>
                <button
                  onClick={reset}
                  className="text-sm px-4 py-2 rounded-lg transition-all"
                  style={{
                    background: "var(--surface2)",
                    color: "var(--text)",
                    border: "1px solid var(--border)",
                  }}
                >
                  Try again
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
