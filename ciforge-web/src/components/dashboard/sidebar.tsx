"use client";

import React from "react";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "next-auth/react";
import {
  LayoutDashboard, Zap, Plus, GitBranch, Clock,
  Key, Settings, Star, BookOpen, LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Explicit type so TypeScript knows badge is optional
type NavItem = {
  href: string;
  icon: React.ForwardRefExoticComponent<any>;
  label: string;
  external?: boolean;
  badge?: string;
};

type NavSection = {
  label: string;
  items: NavItem[];
};

const NAV: NavSection[] = [
  {
    label: "main",
    items: [
      { href: "/dashboard", icon: LayoutDashboard, label: "Overview" },
      { href: "/dashboard/pipelines", icon: Zap, label: "Pipelines" },
      { href: "/dashboard/pipelines/new", icon: Plus, label: "Generate New" },
    ],
  },
  {
    label: "analyze",
    items: [
      { href: "/dashboard/repositories", icon: GitBranch, label: "Repositories" },
      { href: "/dashboard/history", icon: Clock, label: "History" },
      { href: "/dashboard/api-keys", icon: Key, label: "API Keys" },
    ],
  },
  {
    label: "account",
    items: [
      { href: "/dashboard/settings", icon: Settings, label: "Settings" },
      { href: "https://github.com/NeuroNaman", icon: Star, label: "GitHub", external: true },
      { href: "/docs", icon: BookOpen, label: "Docs" },
    ],
  },
];

export function Sidebar({ user }: { user: any }) {
  const pathname = usePathname();

  return (
    <aside
      className="fixed top-0 left-0 w-[240px] h-screen flex flex-col z-50"
      style={{ background: "var(--surface)", borderRight: "1px solid var(--border)" }}
    >
      {/* Logo */}
      <Link
        href="/"
        className="flex items-center gap-2.5 px-5 h-[60px] flex-shrink-0"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <div
          className="w-[30px] h-[30px] rounded-[7px] flex items-center justify-center text-sm"
          style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
        >
          ⚡
        </div>
        <span
          className="text-[18px] font-bold tracking-tight"
          style={{ fontFamily: "var(--font-display)" }}
        >
          CIForge
        </span>
      </Link>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 flex flex-col gap-0.5">
        {NAV.map((section) => (
          <div key={section.label} className="mb-1">
            <div
              className="px-2 py-2 text-[10px] tracking-widest uppercase"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              {section.label}
            </div>
            {section.items.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  target={item.external ? "_blank" : undefined}
                  className={cn(
                    "flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13.5px] transition-all mb-0.5",
                    isActive
                      ? "font-medium"
                      : "font-normal"
                  )}
                  style={{
                    background: isActive ? "rgba(139,92,246,0.12)" : "transparent",
                    color: isActive ? "var(--purple2)" : "var(--text2)",
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      (e.currentTarget as HTMLAnchorElement).style.background = "var(--surface2)";
                      (e.currentTarget as HTMLAnchorElement).style.color = "var(--text)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      (e.currentTarget as HTMLAnchorElement).style.background = "transparent";
                      (e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)";
                    }
                  }}
                >
                  <Icon size={15} className="flex-shrink-0" />
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded-full"
                      style={{
                        background: "rgba(139,92,246,0.2)",
                        color: "var(--purple2)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="flex-shrink-0 p-3" style={{ borderTop: "1px solid var(--border)" }}>
        <div
          className="flex items-center gap-2.5 p-2.5 rounded-lg cursor-pointer transition-all group"
          style={{ background: "transparent" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLDivElement).style.background = "var(--surface2)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLDivElement).style.background = "transparent";
          }}
        >
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white flex-shrink-0"
            style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
          >
            {user?.name?.slice(0, 2).toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[13px] font-medium truncate">{user?.name || "User"}</div>
            <div
              className="text-[11px] truncate"
              style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
            >
              {user?.email || ""}
            </div>
          </div>
          <button
            onClick={() => signOut({ callbackUrl: "/login" })}
            className="opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ color: "var(--text3)" }}
            title="Sign out"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
}
