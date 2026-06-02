"use client";

import { useEffect, useState } from "react";

const LANG_COLORS: Record<string, string> = {
  Python: "linear-gradient(90deg, #8b5cf6, #6366f1)",
  JavaScript: "linear-gradient(90deg, #f59e0b, #f97316)",
  TypeScript: "linear-gradient(90deg, #06b6d4, #6366f1)",
  Go: "linear-gradient(90deg, #06b6d4, #0ea5e9)",
  Java: "linear-gradient(90deg, #ef4444, #f97316)",
  Rust: "linear-gradient(90deg, #f97316, #f59e0b)",
  Ruby: "linear-gradient(90deg, #ef4444, #ec4899)",
  Shell: "#10b981",
  Dockerfile: "#06b6d4",
  Lua: "#8b5cf6",
};

function pickColor(lang: string): string {
  return (
    LANG_COLORS[lang] ||
    `linear-gradient(90deg, hsl(${(lang.charCodeAt(0) * 37) % 360}, 60%, 60%), hsl(${(lang.charCodeAt(0) * 37 + 60) % 360}, 60%, 60%))`
  );
}

export function LanguageBreakdown() {
  const [langs, setLangs] = useState<Array<{ name: string; count: number }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchLangs() {
      try {
        const res = await fetch("/api/pipelines/sessions");
        if (!res.ok) throw new Error("offline");
        const sessions: Array<{ languages: string[] }> = await res.json();
        if (cancelled) return;

        // Count language occurrences across all sessions
        const counts: Record<string, number> = {};
        for (const s of sessions) {
          for (const lang of s.languages || []) {
            counts[lang] = (counts[lang] || 0) + 1;
          }
        }

        const total = Object.values(counts).reduce((a, b) => a + b, 0);
        const sorted = Object.entries(counts)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([name, count]) => ({ name, count }));

        setLangs(sorted.map((l) => ({ ...l, pct: total > 0 ? Math.round((l.count / total) * 100) : 0 })));
      } catch {
        setLangs([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchLangs();
    const interval = setInterval(fetchLangs, 15000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  const langsWithPct = langs as Array<{ name: string; count: number; pct: number }>;

  return (
    <div
      className="rounded-xl p-4"
      style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
    >
      <h2
        className="text-sm font-semibold tracking-tight mb-4"
        style={{ fontFamily: "var(--font-display)" }}
      >
        Languages Detected
      </h2>

      {loading ? (
        <div className="flex flex-col gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 animate-pulse">
              <div
                className="rounded"
                style={{ background: "var(--surface2)", width: "72px", height: "12px" }}
              />
              <div
                className="flex-1 h-1 rounded-full"
                style={{ background: "var(--surface2)" }}
              />
              <div
                className="rounded"
                style={{ background: "var(--surface2)", width: "32px", height: "12px" }}
              />
            </div>
          ))}
        </div>
      ) : langsWithPct.length === 0 ? (
        <div className="py-4 text-center">
          <div
            className="text-xs"
            style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
          >
            No languages detected yet
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {langsWithPct.map((lang) => (
            <div key={lang.name} className="flex items-center gap-3">
              <div
                className="text-xs min-w-[72px]"
                style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}
              >
                {lang.name}
              </div>
              <div
                className="flex-1 h-1 rounded-full overflow-hidden"
                style={{ background: "var(--surface2)" }}
              >
                <div
                  className="h-full rounded-full"
                  style={{ width: `${lang.pct}%`, background: pickColor(lang.name) }}
                />
              </div>
              <div
                className="text-xs min-w-[32px] text-right"
                style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
              >
                {lang.pct}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
