"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ExternalLink, RefreshCw } from "lucide-react";

type Status = "passed" | "running" | "failed" | "pending";

interface Pipeline {
  id: string;
  repo: string;
  platform: string;
  platformIcon: string;
  stack: string;
  file: string;
  status: Status;
  time: string;
}

const PLATFORM_META: Record<string, { label: string; icon: string }> = {
  github_actions: { label: "GitHub Actions", icon: "🐙" },
  gitlab_ci: { label: "GitLab CI", icon: "🦊" },
  jenkins: { label: "Jenkins", icon: "⚙️" },
  circleci: { label: "CircleCI", icon: "🔵" },
  azure_devops: { label: "Azure DevOps", icon: "🔷" },
};

const PLATFORM_FILE: Record<string, string> = {
  github_actions: ".github/workflows/ci-cd.yml",
  gitlab_ci: ".gitlab-ci.yml",
  jenkins: "Jenkinsfile",
  circleci: ".circleci/config.yml",
  azure_devops: "azure-pipelines.yml",
};

function getRepoName(url: string): string {
  try {
    const u = new URL(url);
    return u.pathname.replace(/^\//, "").replace(/\.git$/, "") || url;
  } catch {
    return url;
  }
}

function getRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function sessionToStatus(session: { status: string; validation_passed: boolean | null }): Status {
  if (session.status === "running" || session.status === "pending") return "running";
  if (session.status === "failed") return "failed";
  if (session.validation_passed === false) return "failed";
  if (session.status === "completed") return "passed";
  return "pending";
}

const STATUS_STYLES: Record<Status, { bg: string; color: string; border: string; label: string }> = {
  passed: {
    bg: "rgba(16,185,129,0.08)",
    color: "#10b981",
    border: "rgba(16,185,129,0.2)",
    label: "passed",
  },
  running: {
    bg: "rgba(139,92,246,0.08)",
    color: "#a78bfa",
    border: "rgba(139,92,246,0.2)",
    label: "running",
  },
  failed: {
    bg: "rgba(239,68,68,0.08)",
    color: "#ef4444",
    border: "rgba(239,68,68,0.2)",
    label: "failed",
  },
  pending: {
    bg: "rgba(245,158,11,0.08)",
    color: "#f59e0b",
    border: "rgba(245,158,11,0.2)",
    label: "pending",
  },
};

interface Props {
  limit?: number;
  search?: string;
  platform?: string;
  status?: string;
}

export function PipelineList({ limit, search = "", platform = "All", status = "All" }: Props) {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function fetchPipelines() {
      setLoading(true);
      try {
        const res = await fetch("/api/pipelines/sessions");
        if (!res.ok) throw new Error("Backend offline");

        const sessions: Array<{
          session_id: string;
          repo_url: string;
          platform: string;
          status: string;
          created_at: string;
          validation_passed: boolean | null;
          generated_files: string[];
          frameworks: string[];
          languages: string[];
        }> = await res.json();

        if (cancelled) return;

        const mapped: Pipeline[] = sessions
          .filter((s) => s.repo_url) // skip sessions without a repo URL
          .reverse() // newest first
          .map((s) => {
            const pm = PLATFORM_META[s.platform] || { label: s.platform, icon: "⚙️" };
            const file =
              s.generated_files?.[0] || PLATFORM_FILE[s.platform] || "pipeline";
            const stack = [...(s.frameworks || []), ...(s.languages || [])]
              .slice(0, 3)
              .join(" · ") || "Unknown stack";

            return {
              id: s.session_id,
              repo: getRepoName(s.repo_url),
              platform: pm.label,
              platformIcon: pm.icon,
              stack,
              file,
              status: sessionToStatus({ status: s.status, validation_passed: s.validation_passed }),
              time: s.created_at ? getRelativeTime(s.created_at) : "—",
            };
          });

        setPipelines(mapped);
      } catch {
        setPipelines([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchPipelines();
    return () => { cancelled = true; };
  }, [refreshKey]);

  let displayed = pipelines;

  if (search) {
    displayed = displayed.filter(
      (p) =>
        p.repo.toLowerCase().includes(search.toLowerCase()) ||
        p.stack.toLowerCase().includes(search.toLowerCase())
    );
  }

  if (platform !== "All") {
    displayed = displayed.filter((p) => p.platform === platform);
  }

  if (status !== "All") {
    displayed = displayed.filter((p) => p.status === status);
  }

  if (limit) {
    displayed = displayed.slice(0, limit);
  }

  if (loading) {
    return (
      <div className="flex flex-col gap-2.5">
        {[...Array(limit || 3)].map((_, i) => (
          <div
            key={i}
            className="rounded-xl px-5 py-4 animate-pulse"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              height: "64px",
            }}
          />
        ))}
      </div>
    );
  }

  if (displayed.length === 0) {
    return (
      <div
        className="rounded-xl p-12 text-center"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        <div className="text-4xl mb-4 opacity-30">⚡</div>
        <div className="text-base mb-2" style={{ color: "var(--text2)" }}>
          {pipelines.length === 0 ? "No pipelines yet" : "No pipelines match filters"}
        </div>
        <p className="text-sm mb-4" style={{ color: "var(--text3)" }}>
          {pipelines.length === 0
            ? "Generate your first pipeline using the button above."
            : "Try adjusting your filters."}
        </p>
        <button
          onClick={() => setRefreshKey((k) => k + 1)}
          className="inline-flex items-center gap-2 text-xs transition-colors"
          style={{ color: "var(--purple2)", fontFamily: "var(--font-mono)" }}
        >
          <RefreshCw size={12} /> Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2.5">
      {displayed.map((pipeline) => {
        const s = STATUS_STYLES[pipeline.status];
        return (
          <Link
            key={pipeline.id}
            href={`/dashboard/pipelines/${pipeline.id}`}
            className="flex items-center gap-4 px-5 py-4 rounded-xl transition-all group"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              textDecoration: "none",
              color: "inherit",
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget as HTMLAnchorElement;
              el.style.borderColor = "var(--border2)";
              el.style.background = "var(--surface2)";
              el.style.transform = "translateX(2px)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget as HTMLAnchorElement;
              el.style.borderColor = "var(--border)";
              el.style.background = "var(--surface)";
              el.style.transform = "translateX(0)";
            }}
          >
            {/* Platform icon */}
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center text-base flex-shrink-0"
              style={{ background: "rgba(255,255,255,0.04)" }}
            >
              {pipeline.platformIcon}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="text-[14px] font-medium mb-0.5 truncate">{pipeline.repo}</div>
              <div
                className="flex items-center gap-2 text-[12px] truncate"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                <span>{pipeline.platform}</span>
                <span>·</span>
                <span className="truncate">{pipeline.stack}</span>
                <span>·</span>
                <span className="truncate">{pipeline.file}</span>
              </div>
            </div>

            {/* Status */}
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium flex-shrink-0"
              style={{
                background: s.bg,
                color: s.color,
                border: `1px solid ${s.border}`,
                fontFamily: "var(--font-mono)",
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  background: s.color,
                  animation: pipeline.status === "running" ? "pulse-dot 1.5s infinite" : "none",
                }}
              />
              {s.label}
            </div>

            {/* Time */}
            <div
              className="text-[11px] flex-shrink-0"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              {pipeline.time}
            </div>

            {/* External icon */}
            <ExternalLink
              size={13}
              className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
              style={{ color: "var(--text3)" }}
            />
          </Link>
        );
      })}
    </div>
  );
}
