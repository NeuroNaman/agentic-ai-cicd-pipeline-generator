"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { Save, Key, User, Bell, Shield, Trash2 } from "lucide-react";
import { toast } from "@/components/ui/toaster";

const TABS = [
  { id: "profile", label: "Profile", icon: User },
  { id: "api", label: "API Keys", icon: Key },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "security", label: "Security", icon: Shield },
];

export default function SettingsPage() {
  const { data: session } = useSession();
  const [activeTab, setActiveTab] = useState("profile");
  const [name, setName] = useState(session?.user?.name || "");
  const [email, setEmail] = useState(session?.user?.email || "");
  const [apiKeys] = useState([
    { id: "1", name: "Production key", key: "cfk_prod_••••••••••••3f9a", created: "May 1, 2025" },
    { id: "2", name: "Development key", key: "cfk_dev_••••••••••••7b2c", created: "Apr 28, 2025" },
  ]);

  function handleSave() {
    toast("success", "Settings saved", "Your profile has been updated.");
  }

  return (
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1
          className="text-[26px] font-bold tracking-tight mb-1"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Settings
        </h1>
        <p className="text-sm font-light" style={{ color: "var(--text2)" }}>
          Manage your account and preferences
        </p>
      </div>

      <div className="flex gap-6">
        {/* Tab nav */}
        <div className="flex flex-col gap-1 w-44 flex-shrink-0">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm text-left transition-all"
                style={{
                  background: activeTab === tab.id ? "rgba(139,92,246,0.1)" : "transparent",
                  color: activeTab === tab.id ? "var(--purple2)" : "var(--text2)",
                  border: activeTab === tab.id ? "1px solid rgba(139,92,246,0.2)" : "1px solid transparent",
                }}
              >
                <Icon size={15} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab content */}
        <div className="flex-1">
          {activeTab === "profile" && (
            <div
              className="rounded-xl p-6"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              <h2
                className="text-base font-semibold mb-6 tracking-tight"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Profile
              </h2>

              {/* Avatar */}
              <div className="flex items-center gap-4 mb-6 pb-6" style={{ borderBottom: "1px solid var(--border)" }}>
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold text-white"
                  style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
                >
                  {name.slice(0, 2).toUpperCase() || "U"}
                </div>
                <div>
                  <div className="text-sm font-medium mb-1">{name || "Your Name"}</div>
                  <div className="text-xs" style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
                    {email}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-4 mb-6">
                <div>
                  <label className="block text-xs mb-2" style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}>
                    Display name
                  </label>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg text-sm outline-none transition-all"
                    style={{ background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text)" }}
                    onFocus={(e) => { e.currentTarget.style.borderColor = "var(--purple)"; }}
                    onBlur={(e) => { e.currentTarget.style.borderColor = "var(--border)"; }}
                  />
                </div>
                <div>
                  <label className="block text-xs mb-2" style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}>
                    Email address
                  </label>
                  <input
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    type="email"
                    className="w-full px-4 py-2.5 rounded-lg text-sm outline-none transition-all"
                    style={{ background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text)" }}
                    onFocus={(e) => { e.currentTarget.style.borderColor = "var(--purple)"; }}
                    onBlur={(e) => { e.currentTarget.style.borderColor = "var(--border)"; }}
                  />
                </div>
              </div>

              <button
                onClick={handleSave}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white transition-all"
                style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
              >
                <Save size={14} />
                Save changes
              </button>
            </div>
          )}

          {activeTab === "api" && (
            <div
              className="rounded-xl p-6"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2
                  className="text-base font-semibold tracking-tight"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  API Keys
                </h2>
                <button
                  onClick={() => toast("info", "Coming soon", "API key creation coming soon.")}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium text-white"
                  style={{ background: "linear-gradient(135deg, var(--purple), var(--indigo))" }}
                >
                  + New Key
                </button>
              </div>

              <div className="flex flex-col gap-3">
                {apiKeys.map((key) => (
                  <div
                    key={key.id}
                    className="flex items-center justify-between p-4 rounded-xl"
                    style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
                  >
                    <div>
                      <div className="text-sm font-medium mb-1">{key.name}</div>
                      <div className="text-xs" style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
                        {key.key}
                      </div>
                      <div className="text-xs mt-1" style={{ color: "var(--text3)" }}>
                        Created {key.created}
                      </div>
                    </div>
                    <button
                      onClick={() => toast("success", "Key revoked", `${key.name} has been revoked.`)}
                      className="p-2 rounded-lg transition-all"
                      style={{ color: "var(--red)", background: "rgba(239,68,68,0.1)" }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>

              <p className="text-xs mt-4" style={{ color: "var(--text3)" }}>
                API keys allow you to access CIForge programmatically. Keep them secret.
              </p>
            </div>
          )}

          {activeTab === "notifications" && (
            <div
              className="rounded-xl p-6"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              <h2
                className="text-base font-semibold mb-6 tracking-tight"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Notifications
              </h2>
              {[
                { label: "Pipeline generated", desc: "When a pipeline is successfully generated" },
                { label: "Validation failed", desc: "When a pipeline fails validation" },
                { label: "Self-healing triggered", desc: "When the self-healing agent runs" },
              ].map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between py-4"
                  style={{ borderBottom: i < 2 ? "1px solid var(--border)" : "none" }}
                >
                  <div>
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className="text-xs mt-0.5 font-light" style={{ color: "var(--text2)" }}>{item.desc}</div>
                  </div>
                  <div
                    className="w-10 h-6 rounded-full relative cursor-pointer transition-all"
                    style={{ background: i === 0 ? "var(--purple)" : "var(--surface2)", border: "1px solid var(--border2)" }}
                    onClick={() => toast("info", "Coming soon")}
                  >
                    <div
                      className="absolute top-0.5 w-5 h-5 rounded-full transition-all"
                      style={{
                        background: "white",
                        left: i === 0 ? "calc(100% - 22px)" : "2px",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "security" && (
            <div
              className="rounded-xl p-6"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            >
              <h2
                className="text-base font-semibold mb-6 tracking-tight"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Security
              </h2>
              <div
                className="p-4 rounded-xl mb-4"
                style={{ background: "rgba(16,185,129,0.05)", border: "1px solid rgba(16,185,129,0.2)" }}
              >
                <div className="text-sm font-medium" style={{ color: "var(--green)" }}>
                  ✓ Signed in with GitHub
                </div>
                <div className="text-xs mt-1 font-light" style={{ color: "var(--text2)" }}>
                  Your account is secured with GitHub OAuth
                </div>
              </div>
              <button
                onClick={() => toast("info", "Coming soon", "2FA setup coming soon.")}
                className="text-sm px-4 py-2.5 rounded-lg transition-all"
                style={{ background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text2)" }}
              >
                Enable two-factor authentication
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
