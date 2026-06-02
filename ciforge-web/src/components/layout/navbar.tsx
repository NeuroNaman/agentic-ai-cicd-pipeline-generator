"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { Menu, X } from "lucide-react";

const NAV_LINKS = [
  { href: "#how-it-works", label: "How it works" },
  { href: "#features", label: "Features" },
  { href: "#agents", label: "Agents" },
  { href: "#demo", label: "Demo" },
  {
    href: "https://github.com/NeuroNaman",
    label: "GitHub",
    external: true,
  },
];

export function Navbar() {
  const { data: session } = useSession();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-[100] transition-all duration-300"
      style={{
        padding: scrolled ? "12px 0" : "20px 0",
        background: scrolled ? "rgba(5,5,8,0.85)" : "transparent",
        backdropFilter: scrolled ? "blur(20px)" : "none",
        borderBottom: scrolled ? "1px solid var(--border)" : "none",
      }}
    >
      <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 no-underline">
          <div
            className="w-[34px] h-[34px] rounded-[8px] flex items-center justify-center text-base"
            style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
          >
            ⚡
          </div>
          <span
            className="text-[20px] font-bold tracking-tight text-white"
            style={{ fontFamily: "var(--font-display)" }}
          >
            CIForge
          </span>
        </Link>

        {/* Desktop nav */}
        <ul className="hidden md:flex items-center gap-8 list-none">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                className="text-sm no-underline transition-colors"
                style={{ color: "var(--text2)" }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text)")
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)")
                }
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Actions */}
        <div className="hidden md:flex items-center gap-3">
          {session ? (
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium text-white no-underline transition-all"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
            >
              Dashboard →
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="px-4 py-2 rounded-lg text-sm no-underline transition-all"
                style={{
                  background: "none",
                  border: "1px solid var(--border2)",
                  color: "var(--text2)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.color = "var(--text)";
                  (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--purple)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)";
                  (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--border2)";
                }}
              >
                Sign in
              </Link>
              <Link
                href="/login"
                className="px-5 py-2 rounded-lg text-sm font-medium text-white no-underline transition-all"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
              >
                Get started free
              </Link>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden flex items-center justify-center w-9 h-9 rounded-lg transition-all"
          style={{ border: "1px solid var(--border2)", color: "var(--text)", background: "none" }}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X size={16} /> : <Menu size={16} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div
          className="md:hidden mt-2 mx-4 rounded-xl p-4"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              target={link.external ? "_blank" : undefined}
              className="block py-3 text-sm no-underline transition-colors"
              style={{
                color: "var(--text2)",
                borderBottom: "1px solid var(--border)",
              }}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <div className="pt-3 flex flex-col gap-2">
            <Link
              href="/login"
              className="block py-2.5 text-center rounded-lg text-sm no-underline"
              style={{ border: "1px solid var(--border2)", color: "var(--text2)" }}
            >
              Sign in
            </Link>
            <Link
              href="/login"
              className="block py-2.5 text-center rounded-lg text-sm font-medium text-white no-underline"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
            >
              Get started free
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
