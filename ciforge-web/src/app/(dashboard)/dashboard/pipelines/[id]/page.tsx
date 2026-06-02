"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, Copy, Check, Download, CheckCircle,
  XCircle, Clock, GitBranch, Layers,
} from "lucide-react";

const PLATFORM_META: Record<string, { label: string; icon: string }> = {
  github_actions: { label: "GitHub Actions", icon: "🐙" },
  gitlab_ci: { label: "GitLab CI", icon: "🦊" },
  jenkins: { label: "Jenkins", icon: "⚙️" },
  circleci: { label: "CircleCI", icon: "🔵" },
  azure_devops: { label: "Azure DevOps", icon: "🔷" },
};

const FILE_NAMES: Record<string, string> = {
  github_actions: ".github/workflows/ci-cd.yml",
  gitlab_ci: ".gitlab-ci.yml",
  jenkins: "Jenkinsfile",
  circleci: ".circleci/config.yml",
  azure_devops: "azure-pipelines.yml",
};

function getRepoName(url: string): string {
  try {
    return new URL(url).pathname.replace(/^\//, "").replace(/\.git$/, "");
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

interface SessionStatus {
  session_id: string;
  status: string;
  current_stage: string;
  execution_logs: string[];
  generated_files: Array<{ path: string; content: string }> | null;
  validation_passed: boolean | null;
}

interface SessionMeta {
  repo_url: string;
  platform: string;
  created_at: string;
  frameworks: string[];
  languages: string[];
}

export default function PipelineDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [statusData, setStatusData] = useState<SessionStatus | null>(null);
  const [meta, setMeta] = useState<SessionMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [activeFile, setActiveFile] = useState(0);
  const [activeTab, setActiveTab] = useState<"yaml" | "logs">("yaml");

  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      try {
        // Fetch detailed status (with file contents)
        const statusRes = await fetch(`/api/pipelines/status/${id}`);
        if (!statusRes.ok) {
          setError("Pipeline not found.");
          setLoading(false);
          return;
        }
        const status: SessionStatus = await statusRes.json();
        setStatusData(status);

        // Fetch session list to get meta info (repo_url, platform, etc.)
        const sessionsRes = await fetch("/api/pipelines/sessions");
        if (sessionsRes.ok) {
          const sessions: Array<SessionMeta & { session_id: string }> = await sessionsRes.json();
          const found = sessions.find((s) => s.session_id === id);
          if (found) setMeta(found);
        }
      } catch {
        setError("Failed to load pipeline. Is the backend running?");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  function handleCopy(content: string) {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload(content: string, filename: string) {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename.split("/").pop() || "pipeline";
    a.click();
    URL.revokeObjectURL(url);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div
            className="w-8 h-8 border-2 rounded-full animate-spin"
            style={{ borderColor: "var(--border2)", borderTopColor: "var(--purple2)" }}
          />
          <p className="text-sm" style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
            Loading pipeline...
          </p>
        </div>
      </div>
    );
  }

  if (error || !statusData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="text-5xl">😶</div>
        <h2 className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
          {error || "Pipeline not found"}
        </h2>
        <Link
          href="/dashboard/pipelines"
          className="flex items-center gap-2 text-sm transition-colors"
          style={{ color: "var(--purple2)" }}
        >
          <ArrowLeft size={14} /> Back to pipelines
        </Link>
      </div>
    );
  }

  const platform = meta?.platform || "github_actions";
  const pm = PLATFORM_META[platform] || { label: platform, icon: "⚙️" };
  const files = statusData.generated_files || [];
  const currentFile = files[activeFile];
  const fileName = currentFile?.path || FILE_NAMES[platform] || "pipeline";
  const content = currentFile?.content || "";
  const repoName = meta?.repo_url ? getRepoName(meta.repo_url) : id;
  const stack = [...(meta?.frameworks || []), ...(meta?.languages || [])].slice(0, 4).join(" · ");

  const statusColor =
    statusData.status === "completed"
      ? "var(--green)"
      : statusData.status === "failed"
      ? "#ef4444"
      : "var(--purple2)";

  return (
    <div className="max-w-5xl mx-auto">
      {/* Back */}
      <Link
        href="/dashboard/pipelines"
        className="inline-flex items-center gap-1.5 text-xs mb-6 transition-colors"
        style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
        onMouseEnter={(e) => ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)")}
        onMouseLeave={(e) => ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text3)")}
      >
        <ArrowLeft size={13} /> Back to pipelines
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
            style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
          >
            {pm.icon}
          </div>
          <div>
            <h1
              className="text-[22px] font-bold tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {repoName}
            </h1>
            <div
              className="flex items-center gap-2 text-xs mt-1"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              <span>{pm.label}</span>
              {stack && <><span>·</span><span>{stack}</span></>}
              {meta?.created_at && <><span>·</span><span>{getRelativeTime(meta.created_at)}</span></>}
            </div>
          </div>
        </div>

        {/* Status badge */}
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium"
          style={{
            background: `${statusColor}18`,
            border: `1px solid ${statusColor}40`,
            color: statusColor,
            fontFamily: "var(--font-mono)",
          }}
        >
          {statusData.status === "completed" ? (
            <CheckCircle size={13} />
          ) : statusData.status === "failed" ? (
            <XCircle size={13} />
          ) : (
            <Clock size={13} />
          )}
          {statusData.status}
        </div>
      </div>

      {/* Meta cards */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {[
          {
            icon: GitBranch,
            label: "Repository",
            value: meta?.repo_url || "—",
            truncate: true,
            href: meta?.repo_url,
          },
          {
            icon: Layers,
            label: "Platform",
            value: pm.label,
            truncate: false,
            href: undefined,
          },
          {
            icon: CheckCircle,
            label: "Validation",
            value:
              statusData.validation_passed === true
                ? "Passed ✓"
                : statusData.validation_passed === false
                ? "Failed ✗"
                : "—",
            truncate: false,
            href: undefined,
            color:
              statusData.validation_passed === true
                ? "var(--green)"
                : statusData.validation_passed === false
                ? "#ef4444"
                : "var(--text2)",
          },
        ].map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className="rounded-xl p-4"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              <div
                className="flex items-center gap-1.5 text-[11px] mb-2"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                <Icon size={12} />
                {card.label}
              </div>
              {card.href ? (
                <a
                  href={card.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[13px] font-medium truncate block transition-colors"
                  style={{ color: "var(--purple2)" }}
                >
                  {card.value}
                </a>
              ) : (
                <div
                  className={`text-[13px] font-medium ${card.truncate ? "truncate" : ""}`}
                  style={{ color: card.color || "var(--text)" }}
                >
                  {card.value}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div
        className="flex gap-0.5 p-1 rounded-xl mb-4 w-fit"
        style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
      >
        {(["yaml", "logs"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="px-4 py-1.5 rounded-lg text-xs transition-all capitalize"
            style={{
              background: activeTab === tab ? "var(--surface2)" : "transparent",
              color: activeTab === tab ? "var(--text)" : "var(--text3)",
              fontFamily: "var(--font-mono)",
              border: activeTab === tab ? "1px solid var(--border2)" : "1px solid transparent",
            }}
          >
            {tab === "yaml" ? "Generated YAML" : "Execution Logs"}
          </button>
        ))}
      </div>

      {/* YAML tab */}
      {activeTab === "yaml" && (
        <div
          className="rounded-2xl overflow-hidden"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          {/* File tabs (if multiple files) */}
          {files.length > 1 && (
            <div
              className="flex gap-0.5 px-4 pt-3"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              {files.map((f, i) => (
                <button
                  key={i}
                  onClick={() => setActiveFile(i)}
                  className="px-3 py-1.5 text-xs rounded-t-lg transition-all"
                  style={{
                    background: activeFile === i ? "var(--bg)" : "transparent",
                    color: activeFile === i ? "var(--text)" : "var(--text3)",
                    fontFamily: "var(--font-mono)",
                    borderBottom: activeFile === i ? "2px solid var(--purple)" : "2px solid transparent",
                  }}
                >
                  {f.path.split("/").pop()}
                </button>
              ))}
            </div>
          )}

          {/* File header */}
          <div
            className="flex items-center justify-between px-5 py-3"
            style={{
              background: "var(--surface2)",
              borderBottom: "1px solid var(--border)",
            }}
          >
            <div className="flex items-center gap-3">
              <div className="flex gap-1.5">
                {["#ff5f57", "#ffbd2e", "#28ca41"].map((c) => (
                  <div key={c} className="w-3 h-3 rounded-full" style={{ background: c }} />
                ))}
              </div>
              <span
                className="text-xs"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                {fileName}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span
                className="text-[10px] px-2 py-0.5 rounded"
                style={{
                  background: "rgba(139,92,246,0.15)",
                  color: "var(--purple2)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                YAML
              </span>
              <button
                onClick={() => handleCopy(content)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs transition-all"
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  color: copied ? "var(--green)" : "var(--text2)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {copied ? <Check size={12} /> : <Copy size={12} />}
                {copied ? "Copied!" : "Copy"}
              </button>
              <button
                onClick={() => handleDownload(content, fileName)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs text-white"
                style={{
                  background: "linear-gradient(135deg, var(--purple), var(--indigo))",
                  fontFamily: "var(--font-mono)",
                }}
              >
                <Download size={12} />
                Download
              </button>
            </div>
          </div>

          {/* Code */}
          {content ? (
            <div className="overflow-auto max-h-[520px]">
              <pre
                className="p-6 text-[12.5px] leading-7"
                style={{ fontFamily: "var(--font-mono)", color: "var(--text2)", margin: 0 }}
              >
                <code>{content}</code>
              </pre>
            </div>
          ) : (
            <div className="p-12 text-center">
              <div className="text-3xl mb-3 opacity-30">📄</div>
              <p className="text-sm" style={{ color: "var(--text3)" }}>
                No YAML content available yet
              </p>
            </div>
          )}

          {/* Footer */}
          {statusData.validation_passed !== null && (
            <div
              className="flex items-center justify-between px-5 py-3"
              style={{ borderTop: "1px solid var(--border)", background: "var(--surface2)" }}
            >
              <div
                className="flex items-center gap-4 text-xs"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                {statusData.validation_passed ? (
                  <>
                    <span style={{ color: "var(--green)" }}>✓ Syntax valid</span>
                    <span style={{ color: "var(--green)" }}>✓ Semantic valid</span>
                    <span style={{ color: "var(--green)" }}>✓ Security passed</span>
                    <span style={{ color: "var(--green)" }}>✓ 0 issues</span>
                  </>
                ) : (
                  <span style={{ color: "#ef4444" }}>✗ Validation failed</span>
                )}
              </div>
              <div
                className="text-xs"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                {pm.label}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Logs tab */}
      {activeTab === "logs" && (
        <div
          className="rounded-2xl overflow-hidden"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          <div
            className="flex items-center justify-between px-5 py-3"
            style={{ background: "var(--surface2)", borderBottom: "1px solid var(--border)" }}
          >
            <span
              className="text-xs"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              execution logs
            </span>
            <span
              className="text-xs"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              {statusData.execution_logs?.length || 0} entries
            </span>
          </div>

          <div className="overflow-auto max-h-[520px]">
            {statusData.execution_logs && statusData.execution_logs.length > 0 ? (
              <div className="p-4 flex flex-col gap-1">
                {statusData.execution_logs.map((log, i) => (
                  <div
                    key={i}
                    className="text-[12px] py-1 px-3 rounded"
                    style={{
                      fontFamily: "var(--font-mono)",
                      color: log.includes("fail") || log.includes("error")
                        ? "#ef4444"
                        : log.includes("✓") || log.includes("success") || log.includes("complet")
                        ? "var(--green)"
                        : "var(--text2)",
                      background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                    }}
                  >
                    <span style={{ color: "var(--text3)", marginRight: "12px" }}>
                      {String(i + 1).padStart(3, "0")}
                    </span>
                    {log}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="text-3xl mb-3 opacity-30">📋</div>
                <p className="text-sm" style={{ color: "var(--text3)" }}>
                  No logs available
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
