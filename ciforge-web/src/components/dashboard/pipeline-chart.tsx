"use client";

import { useState, useEffect } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface DayPoint {
  day: string;
  pipelines: number;
}

function buildChartData(
  sessions: Array<{ created_at: string; status: string }>,
  days: number
): DayPoint[] {
  const now = Date.now();
  const map: Record<string, number> = {};

  // Initialize slots
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now - i * 86400000);
    const key = days <= 7
      ? d.toLocaleDateString("en-US", { weekday: "short" })
      : days <= 30
      ? `${d.getMonth() + 1}/${d.getDate()}`
      : d.toLocaleDateString("en-US", { month: "short" });
    map[key] = (map[key] || 0);
  }

  for (const s of sessions) {
    const created = new Date(s.created_at).getTime();
    if (now - created > days * 86400000) continue;
    const d = new Date(s.created_at);
    const key = days <= 7
      ? d.toLocaleDateString("en-US", { weekday: "short" })
      : days <= 30
      ? `${d.getMonth() + 1}/${d.getDate()}`
      : d.toLocaleDateString("en-US", { month: "short" });
    map[key] = (map[key] || 0) + 1;
  }

  return Object.entries(map).map(([day, pipelines]) => ({ day, pipelines }));
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="px-3 py-2 rounded-lg text-xs"
      style={{
        background: "var(--surface2)",
        border: "1px solid var(--border2)",
        fontFamily: "var(--font-mono)",
      }}
    >
      <div style={{ color: "var(--text3)" }}>{label}</div>
      <div style={{ color: "var(--purple2)" }}>
        {payload[0].value} pipeline{payload[0].value !== 1 ? "s" : ""}
      </div>
    </div>
  );
}

const PERIODS = [
  { key: "7d", label: "7d", days: 7 },
  { key: "30d", label: "30d", days: 30 },
  { key: "all", label: "All", days: 365 },
];

export function PipelineChart() {
  const [period, setPeriod] = useState("7d");
  const [sessions, setSessions] = useState<Array<{ created_at: string; status: string }>>([]);

  useEffect(() => {
    async function fetchSessions() {
      try {
        const res = await fetch("/api/pipelines/sessions");
        if (res.ok) {
          const data = await res.json();
          setSessions(data);
        }
      } catch {
        setSessions([]);
      }
    }
    fetchSessions();
    const interval = setInterval(fetchSessions, 15000);
    return () => clearInterval(interval);
  }, []);

  const activePeriod = PERIODS.find((p) => p.key === period)!;
  const chartData = buildChartData(sessions, activePeriod.days);
  const total = sessions.length;

  return (
    <div
      className="rounded-xl p-5"
      style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
    >
      <div className="flex items-start justify-between mb-5">
        <div>
          <div className="text-sm font-medium mb-1">Pipelines Generated</div>
          <div
            className="text-3xl font-bold tracking-tight"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {total}
          </div>
          <div
            className="text-xs mt-1"
            style={{ color: total > 0 ? "var(--green)" : "var(--text3)", fontFamily: "var(--font-mono)" }}
          >
            {total === 0 ? "No pipelines yet" : `${total} total session${total !== 1 ? "s" : ""}`}
          </div>
        </div>

        {/* Period selector */}
        <div
          className="flex gap-0.5 p-1 rounded-lg"
          style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
        >
          {PERIODS.map((p) => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className="px-3 py-1 rounded-md text-xs transition-all"
              style={{
                fontFamily: "var(--font-mono)",
                background: period === p.key ? "var(--surface2)" : "transparent",
                color: period === p.key ? "var(--text)" : "var(--text3)",
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={100}>
        <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
          <defs>
            <linearGradient id="purpleGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="day"
            tick={{ fill: "var(--text3)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis hide />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="pipelines"
            stroke="#8b5cf6"
            strokeWidth={2}
            fill="url(#purpleGrad)"
            dot={{ fill: "#8b5cf6", r: 3 }}
            activeDot={{ fill: "#a78bfa", r: 4 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
