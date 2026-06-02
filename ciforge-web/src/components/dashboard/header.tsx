"use client";

import { usePathname } from "next/navigation";
import { Bell, Plus, Search } from "lucide-react";
import { GenerateModal } from "./generate-modal";
import { useState } from "react";

export function DashboardHeader({ user }: { user: any }) {
  const pathname = usePathname();
  const [modalOpen, setModalOpen] = useState(false);

  const crumbs = pathname
    .split("/")
    .filter(Boolean)
    .map((c) => c.replace(/-/g, " "));

  return (
    <>
      <header
        className="h-[60px] flex items-center px-7 gap-4 sticky top-0 z-40 flex-shrink-0"
        style={{
          background: "rgba(5,5,8,0.85)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        {/* Breadcrumb */}
        <div
          className="flex items-center gap-2 text-xs"
          style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
        >
          {crumbs.map((c, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <span style={{ color: "var(--border2)" }}>/</span>}
              <span style={{ color: i === crumbs.length - 1 ? "var(--text2)" : "var(--text3)" }}>
                {c}
              </span>
            </span>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2.5">
          {/* Search */}
          <div
            className="hidden md:flex items-center gap-2 px-3 py-2 rounded-lg text-xs cursor-pointer transition-all min-w-[200px]"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--text3)",
              fontFamily: "var(--font-mono)",
            }}
          >
            <Search size={13} />
            <span className="flex-1">Search pipelines...</span>
            <span
              className="px-1.5 py-0.5 rounded text-[10px]"
              style={{ background: "var(--surface2)", border: "1px solid var(--border)" }}
            >
              ⌘K
            </span>
          </div>

          {/* Notifications */}
          <button
            className="relative w-[34px] h-[34px] rounded-lg flex items-center justify-center transition-all"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--text2)",
            }}
          >
            <Bell size={15} />
            <span
              className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full"
              style={{ background: "var(--purple)" }}
            />
          </button>

          {/* New pipeline */}
          <button
            onClick={() => setModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-[13px] font-medium text-white transition-all"
            style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
          >
            <Plus size={14} />
            New Pipeline
          </button>
        </div>
      </header>

      <GenerateModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </>
  );
}
