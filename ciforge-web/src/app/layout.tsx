import type { Metadata } from "next";
import { Syne, Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/toaster";

const syne = Syne({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600", "700", "800"],
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["300", "400", "500", "600"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["300", "400", "500"],
});

export const metadata: Metadata = {
  title: {
    default: "CIForge — AI-Powered CI/CD Pipeline Engineer",
    template: "%s — CIForge",
  },
  description:
    "CIForge analyzes any GitHub repository and generates production-ready CI/CD pipelines in seconds. No DevOps expertise required.",
  keywords: ["CI/CD", "DevOps", "AI", "GitHub Actions", "Jenkins", "GitLab CI", "pipeline generator"],
  authors: [{ name: "CIForge" }],
  creator: "CIForge",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ciforge.dev",
    title: "CIForge — AI-Powered CI/CD Pipeline Engineer",
    description: "Generate production-ready CI/CD pipelines in seconds with AI.",
    siteName: "CIForge",
  },
  twitter: {
    card: "summary_large_image",
    title: "CIForge — AI-Powered CI/CD Pipeline Engineer",
    description: "Generate production-ready CI/CD pipelines in seconds with AI.",
    creator: "@ciforge",
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${syne.variable} ${outfit.variable} ${jetbrainsMono.variable} font-body bg-bg text-white antialiased`}
      >
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
