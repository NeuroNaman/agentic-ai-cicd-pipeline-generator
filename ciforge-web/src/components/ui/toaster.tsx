"use client";

import { useEffect, useState } from "react";
import { X, CheckCircle, AlertCircle, Info } from "lucide-react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

// Simple global toast store
const listeners: ((toasts: Toast[]) => void)[] = [];
let toasts: Toast[] = [];

export function toast(type: ToastType, title: string, message?: string) {
  const id = Math.random().toString(36).slice(2);
  toasts = [...toasts, { id, type, title, message }];
  listeners.forEach((l) => l(toasts));
  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id);
    listeners.forEach((l) => l(toasts));
  }, 4000);
}

const ICONS = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
};

const COLORS = {
  success: { bg: "rgba(16,185,129,0.1)", border: "rgba(16,185,129,0.25)", icon: "#10b981" },
  error: { bg: "rgba(239,68,68,0.1)", border: "rgba(239,68,68,0.25)", icon: "#ef4444" },
  info: { bg: "rgba(139,92,246,0.1)", border: "rgba(139,92,246,0.25)", icon: "#a78bfa" },
};

export function Toaster() {
  const [items, setItems] = useState<Toast[]>([]);

  useEffect(() => {
    listeners.push(setItems);
    return () => {
      const idx = listeners.indexOf(setItems);
      if (idx > -1) listeners.splice(idx, 1);
    };
  }, []);

  if (items.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-[500] flex flex-col gap-2.5">
      {items.map((t) => {
        const Icon = ICONS[t.type];
        const colors = COLORS[t.type];
        return (
          <div
            key={t.id}
            className="flex items-start gap-3 px-4 py-3.5 rounded-xl min-w-[300px] max-w-[400px]"
            style={{
              background: "var(--surface)",
              border: `1px solid ${colors.border}`,
              boxShadow: "0 8px 30px rgba(0,0,0,0.3)",
              animation: "fade-up 0.3s ease forwards",
            }}
          >
            <Icon size={18} style={{ color: colors.icon, flexShrink: 0, marginTop: 1 }} />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium">{t.title}</div>
              {t.message && (
                <div className="text-xs mt-0.5 font-light" style={{ color: "var(--text2)" }}>
                  {t.message}
                </div>
              )}
            </div>
            <button
              onClick={() => {
                toasts = toasts.filter((x) => x.id !== t.id);
                listeners.forEach((l) => l(toasts));
              }}
              style={{ color: "var(--text3)", flexShrink: 0 }}
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
