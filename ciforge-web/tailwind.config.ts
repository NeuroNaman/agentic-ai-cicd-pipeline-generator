import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#050508",
          secondary: "#080810",
          tertiary: "#0f0f18",
        },
        surface: {
          DEFAULT: "#0f0f18",
          secondary: "#141422",
          tertiary: "#1a1a2e",
        },
        purple: {
          DEFAULT: "#8b5cf6",
          light: "#a78bfa",
          dark: "#7c3aed",
        },
        indigo: {
          DEFAULT: "#6366f1",
        },
        cyan: {
          DEFAULT: "#06b6d4",
        },
        brand: {
          green: "#10b981",
          amber: "#f59e0b",
          red: "#ef4444",
        },
      },
      fontFamily: {
        display: ["Syne", "sans-serif"],
        body: ["Outfit", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderColor: {
        brand: "rgba(139,92,246,0.15)",
        "brand-hover": "rgba(139,92,246,0.35)",
      },
      animation: {
        "pulse-dot": "pulse-dot 2s infinite",
        "float": "float 3s ease-in-out infinite",
        "slide-in": "slide-in 0.5s forwards",
        "fade-up": "fade-up 0.6s ease forwards",
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        "pulse-dot": {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.5", transform: "scale(0.8)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        "slide-in": {
          to: { opacity: "1", transform: "translateX(0)" },
        },
        "fade-up": {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      backgroundImage: {
        "gradient-brand": "linear-gradient(135deg, #8b5cf6, #6366f1)",
        "gradient-brand-hover": "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "gradient-text": "linear-gradient(135deg, #a78bfa, #6366f1, #06b6d4)",
      },
    },
  },
  plugins: [],
};

export default config;
