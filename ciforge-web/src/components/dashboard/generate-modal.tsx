"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Github, CheckCircle, Loader2, Copy, Check } from "lucide-react";
import { useRouter } from "next/navigation";

const PLATFORMS = [
  { id: "github_actions", label: "GitHub Actions", icon: "🐙" },
  { id: "gitlab_ci", label: "GitLab CI", icon: "🦊" },
  { id: "jenkins", label: "Jenkins", icon: "⚙️" },
];

// Maps backend stage names → agent index
const STAGE_TO_AGENT: Record<string, number> = {
  intake: 0,
  analyzing: 1,
  planning: 1,
  generating: 2,
  validating: 3,
  completed: 3,
};

const AGENTS = [
  "[1/4] Repo Analysis Agent",
  "[2/4] Planner Agent",
  "[3/4] Pipeline Generator Agent",
  "[4/4] Validation Agent",
];

interface Props {
  open: boolean;
  onClose: () => void;
  initialUrl?: string;
  initialPlatform?: string;
}

export function GenerateModal({ open, onClose, initialUrl = "", initialPlatform = "github_actions" }: Props) {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState("github_actions");
  const [stage, setStage] = useState<"form" | "generating" | "done" | "error">("form");
  const [currentAgent, setCurrentAgent] = useState(-1);
  const [doneAgents, setDoneAgents] = useState<number[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [generatedYaml, setGeneratedYaml] = useState<string>("");
  const [validationPassed, setValidationPassed] = useState<boolean | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [copied, setCopied] = useState(false);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  // Reset on open
  useEffect(() => {
    if (open) {
      setUrl(initialUrl);
      setPlatform(initialPlatform);
      setStage("form");
      setCurrentAgent(-1);
      setDoneAgents([]);
      setSessionId(null);
      setGeneratedYaml("");
      setValidationPassed(null);
      setErrorMsg("");
      setCopied(false);
    }
  }, [open, initialUrl, initialPlatform]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  async function handleGenerate() {
    if (!url.trim()) return;
    setStage("generating");
    setCurrentAgent(0);

    try {
      // POST to backend via Next.js API proxy
      const res = await fetch("/api/pipelines/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: url.trim(),
          platform,
          auto_approve: true,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || "Backend error");
      }

      const data = await res.json();
      const sid = data.session_id;
      setSessionId(sid);

      // Start polling for status
      pollRef.current = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/pipelines/status/${sid}`);
          if (!statusRes.ok) return;

          const status = await statusRes.json();
          const backendStage: string = status.current_stage || "unknown";
          const agentIdx = STAGE_TO_AGENT[backendStage] ?? -1;

          if (agentIdx >= 0) {
            setCurrentAgent(agentIdx);
            // Mark previous agents as done
            setDoneAgents(
              Array.from({ length: agentIdx }, (_, i) => i)
            );
          }

          if (status.status === "completed" || backendStage === "completed") {
            // Done — mark all agents complete
            setDoneAgents([0, 1, 2, 3]);
            setCurrentAgent(-1);

            // Extract generated YAML
            const files = status.generated_files || [];
            if (files.length > 0) {
              setGeneratedYaml(files[0].content || "");
            }
            setValidationPassed(status.validation_passed ?? null);

            if (pollRef.current) clearInterval(pollRef.current);
            setStage("done");
          } else if (status.status === "failed") {
            if (pollRef.current) clearInterval(pollRef.current);
            setErrorMsg("Pipeline generation failed. Check that the backend is running and the repo URL is valid.");
            setStage("error");
          }
        } catch {
          // Polling error — continue
        }
      }, 1500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to connect to backend";
      setErrorMsg(msg);
      setStage("error");
    }
  }

  function handleViewPipeline() {
    if (pollRef.current) clearInterval(pollRef.current);
    onClose();
    router.push("/dashboard/pipelines");
  }

  function handleCopy() {
    if (generatedYaml) {
      navigator.clipboard.writeText(generatedYaml);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[200] flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)" }}
          onClick={(e) => e.target === e.currentTarget && onClose()}
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="w-full max-w-[540px] rounded-2xl p-8 relative"
            style={{ background: "var(--surface)", border: "1px solid var(--border2)" }}
          >
            {/* Close */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-7 h-7 rounded-lg flex items-center justify-center transition-all"
              style={{ color: "var(--text3)", background: "transparent" }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = "var(--surface2)";
                (e.currentTarget as HTMLButtonElement).style.color = "var(--text)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                (e.currentTarget as HTMLButtonElement).style.color = "var(--text3)";
              }}
            >
              <X size={16} />
            </button>

            <AnimatePresence mode="wait">
              {/* FORM */}
              {stage === "form" && (
                <motion.div
                  key="form"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <h2
                    className="text-[22px] font-bold tracking-tight mb-1"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    Generate Pipeline
                  </h2>
                  <p className="text-sm mb-7 font-light" style={{ color: "var(--text2)" }}>
                    Enter a repository URL and choose your CI/CD platform.
                  </p>

                  <div className="mb-5">
                    <label
                      className="block text-xs mb-2"
                      style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
                    >
                      // repository url
                    </label>
                    <div
                      className="flex items-center gap-2.5 px-4 py-3 rounded-xl"
                      style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
                    >
                      <Github size={15} style={{ color: "var(--text3)", flexShrink: 0 }} />
                      <input
                        autoFocus
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                        placeholder="https://github.com/user/repo"
                        className="flex-1 bg-transparent text-sm outline-none"
                        style={{ color: "var(--text)", fontFamily: "var(--font-mono)" }}
                      />
                    </div>
                  </div>

                  <div className="mb-7">
                    <label
                      className="block text-xs mb-3"
                      style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
                    >
                      // target platform
                    </label>
                    <div className="grid grid-cols-3 gap-2.5">
                      {PLATFORMS.map((p) => (
                        <button
                          key={p.id}
                          onClick={() => setPlatform(p.id)}
                          className="p-3.5 rounded-xl text-center transition-all"
                          style={{
                            background: platform === p.id ? "rgba(139,92,246,0.1)" : "var(--bg)",
                            border: platform === p.id ? "1px solid var(--purple)" : "1px solid var(--border)",
                          }}
                        >
                          <div className="text-xl mb-1.5">{p.icon}</div>
                          <div
                            className="text-[11px]"
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

                  <div className="flex gap-2.5">
                    <button
                      onClick={onClose}
                      className="flex-1 py-3 rounded-xl text-sm transition-all"
                      style={{
                        background: "none",
                        border: "1px solid var(--border2)",
                        color: "var(--text2)",
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleGenerate}
                      disabled={!url.trim()}
                      className="flex-[2] py-3 rounded-xl text-sm font-medium text-white transition-all disabled:opacity-40"
                      style={{
                        background: "linear-gradient(135deg, var(--purple), var(--indigo))",
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
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="flex items-center gap-2.5 mb-1">
                    <Loader2 size={18} className="animate-spin" style={{ color: "var(--purple2)" }} />
                    <h2
                      className="text-[20px] font-bold tracking-tight"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      Generating...
                    </h2>
                  </div>
                  <p
                    className="text-sm mb-6 ml-7 truncate"
                    style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
                  >
                    {url}
                  </p>

                  <div>
                    {AGENTS.map((agent, i) => {
                      const isDone = doneAgents.includes(i);
                      const isActive = currentAgent === i && !isDone;
                      return (
                        <div
                          key={i}
                          className="flex items-center gap-3 py-3.5"
                          style={{
                            borderBottom: i < AGENTS.length - 1 ? "1px solid var(--border)" : "none",
                          }}
                        >
                          {isDone ? (
                            <CheckCircle size={16} style={{ color: "var(--green)", flexShrink: 0 }} />
                          ) : isActive ? (
                            <Loader2 size={16} className="animate-spin flex-shrink-0" style={{ color: "var(--purple2)" }} />
                          ) : (
                            <div
                              className="w-4 h-4 rounded-full border-2 flex-shrink-0"
                              style={{ borderColor: "var(--border2)" }}
                            />
                          )}
                          <span
                            className="text-sm"
                            style={{
                              fontFamily: "var(--font-mono)",
                              color: isDone ? "var(--green)" : isActive ? "var(--purple2)" : "var(--text3)",
                            }}
                          >
                            {agent}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </motion.div>
              )}

              {/* DONE */}
              {stage === "done" && (
                <motion.div
                  key="done"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="text-center py-2 mb-5">
                    <div className="text-5xl mb-4">✅</div>
                    <h2
                      className="text-[22px] font-bold tracking-tight mb-2"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      Pipeline generated!
                    </h2>
                    <p className="text-sm mb-1 font-light" style={{ color: "var(--text2)" }}>
                      {validationPassed === true
                        ? "Validation passed · 0 issues found"
                        : validationPassed === false
                        ? "Validation completed with warnings"
                        : "Pipeline generation complete"}
                    </p>
                    <p
                      className="text-xs truncate"
                      style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
                    >
                      {url}
                    </p>
                  </div>

                  {/* YAML preview */}
                  {generatedYaml && (
                    <div
                      className="rounded-xl overflow-hidden mb-5"
                      style={{ border: "1px solid var(--border)" }}
                    >
                      <div
                        className="flex items-center justify-between px-4 py-2"
                        style={{ background: "var(--surface2)", borderBottom: "1px solid var(--border)" }}
                      >
                        <span
                          className="text-xs"
                          style={{ fontFamily: "var(--font-mono)", color: "var(--text3)" }}
                        >
                          Generated YAML · {generatedYaml.split("\n").length} lines
                        </span>
                        <button
                          onClick={handleCopy}
                          className="flex items-center gap-1.5 text-xs transition-colors"
                          style={{ color: copied ? "var(--green)" : "var(--purple2)" }}
                        >
                          {copied ? <Check size={12} /> : <Copy size={12} />}
                          {copied ? "Copied!" : "Copy"}
                        </button>
                      </div>
                      <pre
                        className="p-4 text-xs leading-5"
                        style={{
                          fontFamily: "var(--font-mono)",
                          color: "var(--text2)",
                          background: "var(--bg)",
                          maxHeight: "240px",
                          overflowY: "auto",
                          overflowX: "auto",
                          whiteSpace: "pre",        /* preserve all whitespace exactly */
                          wordBreak: "keep-all",    /* never break ${{ }} expressions */
                          tabSize: 2,
                        }}
                      >
                        {generatedYaml}
                      </pre>
                    </div>
                  )}

                  <div className="flex gap-2.5">
                    <button
                      onClick={onClose}
                      className="flex-1 py-3 rounded-xl text-sm transition-all"
                      style={{ background: "none", border: "1px solid var(--border2)", color: "var(--text2)" }}
                    >
                      Close
                    </button>
                    <button
                      onClick={handleViewPipeline}
                      className="flex-[2] py-3 rounded-xl text-sm font-medium text-white"
                      style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
                    >
                      View All Pipelines →
                    </button>
                  </div>
                </motion.div>
              )}

              {/* ERROR */}
              {stage === "error" && (
                <motion.div
                  key="error"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="text-center py-4">
                    <div className="text-5xl mb-4">❌</div>
                    <h2
                      className="text-[22px] font-bold tracking-tight mb-2"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      Generation failed
                    </h2>
                    <p
                      className="text-sm mb-6 font-light leading-relaxed"
                      style={{ color: "var(--text2)" }}
                    >
                      {errorMsg || "An unexpected error occurred."}
                    </p>
                    <div className="flex gap-2.5">
                      <button
                        onClick={onClose}
                        className="flex-1 py-3 rounded-xl text-sm"
                        style={{ background: "none", border: "1px solid var(--border2)", color: "var(--text2)" }}
                      >
                        Close
                      </button>
                      <button
                        onClick={() => setStage("form")}
                        className="flex-[2] py-3 rounded-xl text-sm font-medium text-white"
                        style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
                      >
                        Try Again
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
