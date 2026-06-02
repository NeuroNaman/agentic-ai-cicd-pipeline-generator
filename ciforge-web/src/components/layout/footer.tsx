"use client";
import Link from "next/link";

const FOOTER_LINKS = {
  Product: [
    { label: "Features", href: "#features" },
    { label: "How it works", href: "#how-it-works" },
    { label: "Changelog", href: "/changelog" },
    { label: "Roadmap", href: "/roadmap" },
  ],
  Developers: [
    { label: "Documentation", href: "/docs" },
    { label: "API Reference", href: "/docs/api" },
    { label: "GitHub", href: "https://github.com/NeuroNaman" },
    { label: "Contributing", href: "https://github.com/NeuroNaman" },
  ],
  Community: [
    { label: "Discord", href: "/discord" },
    { label: "Twitter", href: "https://twitter.com/ciforge" },
    { label: "Blog", href: "/blog" },
    { label: "Issues", href: "https://github.com/NeuroNaman" },
  ],
};

export function Footer() {
  return (
    <footer
      className="relative z-10"
      style={{ borderTop: "1px solid var(--border)" }}
    >
      <div className="max-w-[1200px] mx-auto px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-16">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2.5 no-underline mb-4">
              <div
                className="w-[30px] h-[30px] rounded-[7px] flex items-center justify-center text-sm"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)" }}
              >
                ⚡
              </div>
              <span
                className="text-[18px] font-bold tracking-tight text-white"
                style={{ fontFamily: "var(--font-display)" }}
              >
                CIForge
              </span>
            </Link>
            <p
              className="text-sm leading-relaxed font-light max-w-[260px]"
              style={{ color: "var(--text3)" }}
            >
              AI-powered CI/CD pipeline generation. Open source and free forever. Built for developers who want to ship faster.
            </p>

            {/* GitHub star */}
            <a
              href="https://github.com/NeuroNaman"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 mt-5 px-3 py-1.5 rounded-lg text-xs no-underline transition-all"
              style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
                color: "var(--text2)",
                fontFamily: "var(--font-mono)",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--border2)";
                (e.currentTarget as HTMLAnchorElement).style.color = "var(--text)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--border)";
                (e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)";
              }}
            >
              ★ Star on GitHub
            </a>
          </div>

          {/* Links */}
          {Object.entries(FOOTER_LINKS).map(([section, links]) => (
            <div key={section}>
              <h4
                className="text-xs font-medium mb-5 tracking-widest uppercase"
                style={{ color: "var(--text)", fontFamily: "var(--font-mono)" }}
              >
                {section}
              </h4>
              <ul className="flex flex-col gap-3 list-none">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      target={link.href.startsWith("http") ? "_blank" : undefined}
                      className="text-sm no-underline transition-colors"
                      style={{ color: "var(--text3)" }}
                      onMouseEnter={(e) =>
                        ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)")
                      }
                      onMouseLeave={(e) =>
                        ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text3)")
                      }
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div
          className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8"
          style={{ borderTop: "1px solid var(--border)" }}
        >
          <span
            className="text-xs"
            style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
          >
            © 2025 CIForge · Open Source · MIT License
          </span>
          <div className="flex gap-6">
            {["Privacy", "Terms", "License"].map((label) => (
              <Link
                key={label}
                href={`/${label.toLowerCase()}`}
                className="text-xs no-underline transition-colors"
                style={{ color: "var(--text3)" }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text2)")
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text3)")
                }
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
