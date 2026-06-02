"use client";

import { useEffect, useState } from "react";

interface Activity {
  icon: string;
  iconBg: string;
  iconColor: string;
  title: string;
  detail: string;
  time: string;
}

function getRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function getRepoName(url: string): string {
  try {
    return new URL(url).pathname.replace(/^\//, "").replace(/\.git$/, "");
  } catch {
    return url;
  }
}

const PLATFORM_SHORT: Record<string, string> = {
  github_actions: "GitHub Actions",
  gitlab_ci: "GitLab CI",
  jenkins: "Jenkins",
  circleci: "CircleCI",
  azure_devops: "Azure DevOps",
};

function sessionToActivity(s: {
  session_id: string;
  status: string;
  repo_url: string;
  platform: string;
  created_at: string;
  validation_passed: boolean | null;
  frameworks: string[];
  languages: string[];
}): Activity {
  const repo = getRepoName(s.repo_url);
  const platform = PLATFORM_SHORT[s.platform] || s.platform;
  const stack = [...(s.frameworks || []), ...(s.languages || [])].slice(0, 2).join(", ");

  if (s.status === "running" || s.status === "pending") {
    return {
      icon: "⟳",
      iconBg: "rgba(139,92,246,0.1)",
      iconColor: "#a78bfa",
      title: "Pipeline generating",
      detail: `${repo} · ${platform}`,
      time: getRelativeTime(s.created_at),
    };
  }

  if (s.status === "failed") {
    return {
      icon: "✗",
      iconBg: "rgba(239,68,68,0.1)",
      iconColor: "#ef4444",
      title: "Generation failed",
      detail: `${repo} · ${platform}`,
      time: getRelativeTime(s.created_at),
    };
  }

  // completed
  if (s.validation_passed === false) {
    return {
      icon: "⚠",
      iconBg: "rgba(245,158,11,0.1)",
      iconColor: "#f59e0b",
      title: "Pipeline with warnings",
      detail: `${repo} · ${platform}`,
      time: getRelativeTime(s.created_at),
    };
  }

  return {
    icon: "✓",
    iconBg: "rgba(16,185,129,0.1)",
    iconColor: "#10b981",
    title: "Pipeline validated",
    detail: `${repo} · ${stack || platform}`,
    time: getRelativeTime(s.created_at),
  };
}

export function ActivityFeed() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchActivity() {
      try {
        const res = await fetch("/api/pipelines/sessions");
        if (!res.ok) throw new Error("offline");
        const sessions = await res.json();
        if (cancelled) return;
        const mapped: Activity[] = sessions
          .filter((s: { repo_url: string }) => s.repo_url)
          .reverse()
          .slice(0, 6)
          .map(sessionToActivity);
        setActivities(mapped);
      } catch {
        setActivities([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchActivity();
    const interval = setInterval(fetchActivity, 15000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-sm font-semibold tracking-tight"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Activity
        </h2>
        <span
          className="text-xs"
          style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
        >
          live
        </span>
      </div>

      <div
        className="rounded-xl px-4 py-1"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        {loading ? (
          <>
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="flex gap-3 py-3.5 animate-pulse"
                style={{ borderBottom: i < 2 ? "1px solid var(--border)" : "none" }}
              >
                <div
                  className="w-7 h-7 rounded-full flex-shrink-0"
                  style={{ background: "var(--surface2)" }}
                />
                <div className="flex-1">
                  <div
                    className="h-3 rounded mb-2"
                    style={{ background: "var(--surface2)", width: "60%" }}
                  />
                  <div
                    className="h-2.5 rounded"
                    style={{ background: "var(--surface2)", width: "80%" }}
                  />
                </div>
              </div>
            ))}
          </>
        ) : activities.length === 0 ? (
          <div className="py-8 text-center">
            <div className="text-2xl mb-2 opacity-30">📋</div>
            <div
              className="text-xs"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              No activity yet
            </div>
          </div>
        ) : (
          activities.map((a, i) => (
            <div
              key={i}
              className="flex gap-3 py-3.5"
              style={{
                borderBottom:
                  i < activities.length - 1 ? "1px solid var(--border)" : "none",
              }}
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs flex-shrink-0 mt-0.5"
                style={{ background: a.iconBg, color: a.iconColor }}
              >
                {a.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-medium">{a.title}</div>
                <div
                  className="text-[12px] mt-0.5 truncate font-light"
                  style={{ color: "var(--text2)" }}
                >
                  {a.detail}
                </div>
                <div
                  className="text-[11px] mt-1"
                  style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
                >
                  {a.time}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
