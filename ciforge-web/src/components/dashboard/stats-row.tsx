"use client";

import { useEffect, useState } from "react";
import { Zap, CheckCircle, Clock, Layers } from "lucide-react";

interface StatsData {
  total: number;
  successRate: string;
  platforms: number;
  platformNames: string;
}

function calcStats(sessions: Array<{ status: string; platform: string; validation_passed: boolean | null }>): StatsData {
  const total = sessions.length;
  const completed = sessions.filter((s) => s.status === "completed");
  const passed = completed.filter((s) => s.validation_passed !== false).length;
  const successRate = total === 0 ? "—" : `${Math.round((passed / Math.max(completed.length, 1)) * 100)}%`;
  const platformSet = new Set(sessions.map((s) => s.platform).filter(Boolean));
  const PLATFORM_SHORT: Record<string, string> = {
    github_actions: "GHA",
    gitlab_ci: "GitLab",
    jenkins: "Jenkins",
    circleci: "Circle",
    azure_devops: "Azure",
  };
  const platformNames = [...platformSet].map((p) => PLATFORM_SHORT[p] || p).join(" · ");

  return {
    total,
    successRate,
    platforms: platformSet.size,
    platformNames: platformNames || "—",
  };
}

export function StatsRow() {
  const [stats, setStats] = useState<StatsData>({
    total: 0,
    successRate: "—",
    platforms: 0,
    platformNames: "—",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function fetchStats() {
      try {
        const res = await fetch("/api/pipelines/sessions");
        if (!res.ok) throw new Error("offline");
        const sessions = await res.json();
        if (!cancelled) {
          setStats(calcStats(sessions));
        }
      } catch {
        // Backend offline — keep zeros
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchStats();
    // Auto-refresh every 15s to pick up new generations
    const interval = setInterval(fetchStats, 15000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  const STATS_CONFIG = [
    {
      label: "total_pipelines",
      value: loading ? "…" : String(stats.total),
      change: loading ? "" : stats.total === 0 ? "Generate your first" : `${stats.total} sessions in memory`,
      positive: stats.total > 0 ? true : null,
      icon: Zap,
      gradient: "linear-gradient(90deg, var(--purple), var(--indigo))",
    },
    {
      label: "success_rate",
      value: loading ? "…" : stats.successRate,
      change: loading ? "" : stats.total === 0 ? "no data yet" : "validation pass rate",
      positive: stats.successRate !== "—" && stats.successRate !== "0%" ? true : null,
      icon: CheckCircle,
      gradient: "linear-gradient(90deg, var(--green), var(--cyan))",
    },
    {
      label: "avg_gen_time",
      value: "~30s",
      change: "typical generation time",
      positive: null,
      icon: Clock,
      gradient: "linear-gradient(90deg, var(--amber), #f97316)",
    },
    {
      label: "platforms",
      value: loading ? "…" : String(stats.platforms || "—"),
      change: loading ? "" : stats.platformNames,
      positive: null,
      icon: Layers,
      gradient: "linear-gradient(90deg, var(--cyan), var(--indigo))",
    },
  ];

  return (
    <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
      {STATS_CONFIG.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className="relative overflow-hidden rounded-xl p-5 group transition-all cursor-default"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget as HTMLDivElement;
              el.style.borderColor = "var(--border2)";
              el.querySelector(".stat-top-bar")?.setAttribute(
                "style",
                `opacity:1;background:${stat.gradient};height:2px;position:absolute;top:0;left:0;right:0;transition:opacity 0.25s;`
              );
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget as HTMLDivElement;
              el.style.borderColor = "var(--border)";
              el.querySelector(".stat-top-bar")?.setAttribute(
                "style",
                `opacity:0;background:${stat.gradient};height:2px;position:absolute;top:0;left:0;right:0;transition:opacity 0.25s;`
              );
            }}
          >
            {/* Top border gradient */}
            <div
              className="stat-top-bar"
              style={{
                opacity: 0,
                background: stat.gradient,
                height: "2px",
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                transition: "opacity 0.25s",
              }}
            />

            <div className="flex items-center justify-between mb-3">
              <span
                className="text-[11px]"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                {stat.label}
              </span>
              <Icon size={15} style={{ color: "var(--text3)" }} />
            </div>

            <div
              className="text-[30px] font-bold tracking-tight mb-1.5"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {stat.value}
            </div>

            <div
              className="text-xs truncate"
              style={{
                fontFamily: "var(--font-mono)",
                color:
                  stat.positive === true
                    ? "var(--green)"
                    : stat.positive === false
                    ? "var(--red)"
                    : "var(--text3)",
              }}
            >
              {stat.change}
            </div>
          </div>
        );
      })}
    </div>
  );
}
