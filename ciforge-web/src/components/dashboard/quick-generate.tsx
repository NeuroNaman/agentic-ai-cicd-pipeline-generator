"use client";

import { useState } from "react";
import { Github, Zap } from "lucide-react";
import { GenerateModal } from "./generate-modal";

interface Props {
  compact?: boolean;
}

const PLATFORMS = [
  { id: "github_actions", label: "GHA" },
  { id: "gitlab_ci", label: "GitLab" },
  { id: "jenkins", label: "Jenkins" },
];

export function QuickGenerate({ compact }: Props) {
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState("github_actions");
  const [modalOpen, setModalOpen] = useState(false);

  function handleGo() {
    if (!url.trim()) return;
    setModalOpen(true);
  }

  if (compact) {
    return (
      <>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all"
          style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
        >
          <Zap size={14} />
          Generate Pipeline
        </button>
        <GenerateModal open={modalOpen} onClose={() => setModalOpen(false)} />
      </>
    );
  }

  return (
    <>
      <div>
        <h2
          className="text-base font-semibold tracking-tight mb-4"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Quick Generate
        </h2>
        <div
          className="rounded-xl p-4"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          <div
            className="text-[11px] mb-3"
            style={{ color: "var(--purple2)", fontFamily: "var(--font-mono)" }}
          >
            // paste repo url
          </div>

          {/* Input row */}
          <div className="flex gap-2 mb-3">
            <div
              className="flex items-center gap-2 flex-1 px-3 py-2 rounded-lg"
              style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
            >
              <Github size={13} style={{ color: "var(--text3)", flexShrink: 0 }} />
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGo()}
                placeholder="github.com/user/repo"
                className="flex-1 bg-transparent text-xs outline-none"
                style={{ color: "var(--text)", fontFamily: "var(--font-mono)" }}
              />
            </div>
            <button
              onClick={handleGo}
              disabled={!url.trim()}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-white transition-all disabled:opacity-40"
              style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))", whiteSpace: "nowrap" }}
            >
              <Zap size={12} />
              Go
            </button>
          </div>

          {/* Platform buttons */}
          <div className="flex gap-1.5">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => setPlatform(p.id)}
                className="flex-1 py-1.5 rounded-lg text-[11px] text-center transition-all"
                style={{
                  fontFamily: "var(--font-mono)",
                  background: platform === p.id ? "rgba(139,92,246,0.1)" : "var(--bg)",
                  border: platform === p.id ? "1px solid rgba(139,92,246,0.3)" : "1px solid var(--border)",
                  color: platform === p.id ? "var(--purple2)" : "var(--text3)",
                }}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <GenerateModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        initialUrl={url}
        initialPlatform={platform}
      />
    </>
  );
}
