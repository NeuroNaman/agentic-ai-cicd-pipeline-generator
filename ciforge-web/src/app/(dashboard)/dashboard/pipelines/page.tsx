"use client";

import { useState } from "react";
import { PipelineList } from "@/components/dashboard/pipeline-list";
import { GenerateModal } from "@/components/dashboard/generate-modal";
import { Plus, Filter, Search } from "lucide-react";

const PLATFORMS = ["All", "GitHub Actions", "GitLab CI", "Jenkins"];
const STATUSES = ["All", "passed", "running", "failed", "pending"];

export default function PipelinesPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [platform, setPlatform] = useState("All");
  const [status, setStatus] = useState("All");

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-7">
        <div>
          <h1
            className="text-[26px] font-bold tracking-tight mb-1"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Pipelines
          </h1>
          <p className="text-sm font-light" style={{ color: "var(--text2)" }}>
            All generated CI/CD pipeline configurations
          </p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all"
          style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
        >
          <Plus size={15} />
          Generate New
        </button>
      </div>

      {/* Filters bar */}
      <div
        className="flex items-center gap-3 p-3 rounded-xl mb-5"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        {/* Search */}
        <div
          className="flex items-center gap-2 flex-1 px-3 py-2 rounded-lg"
          style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
        >
          <Search size={14} style={{ color: "var(--text3)" }} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search repositories..."
            className="flex-1 bg-transparent text-sm outline-none"
            style={{ color: "var(--text)", fontFamily: "var(--font-mono)" }}
          />
        </div>

        {/* Platform filter */}
        <div className="flex items-center gap-1">
          {PLATFORMS.map((p) => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className="px-3 py-1.5 rounded-lg text-xs transition-all"
              style={{
                fontFamily: "var(--font-mono)",
                background:
                  platform === p ? "rgba(139,92,246,0.15)" : "transparent",
                color: platform === p ? "var(--purple2)" : "var(--text3)",
                border:
                  platform === p
                    ? "1px solid rgba(139,92,246,0.3)"
                    : "1px solid transparent",
              }}
            >
              {p}
            </button>
          ))}
        </div>

        <div
          className="w-px h-5"
          style={{ background: "var(--border)" }}
        />

        {/* Status filter */}
        <div className="flex items-center gap-1">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className="px-3 py-1.5 rounded-lg text-xs capitalize transition-all"
              style={{
                fontFamily: "var(--font-mono)",
                background:
                  status === s ? "rgba(139,92,246,0.15)" : "transparent",
                color: status === s ? "var(--purple2)" : "var(--text3)",
                border:
                  status === s
                    ? "1px solid rgba(139,92,246,0.3)"
                    : "1px solid transparent",
              }}
            >
              {s}
            </button>
          ))}
        </div>

        <button
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all ml-auto"
          style={{
            background: "var(--bg)",
            border: "1px solid var(--border)",
            color: "var(--text2)",
            fontFamily: "var(--font-mono)",
          }}
        >
          <Filter size={12} />
          More filters
        </button>
      </div>

      {/* Pipeline list */}
      <PipelineList search={search} platform={platform} status={status} />

      {/* Modal */}
      <GenerateModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
