import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        heading: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        forge: {
          bg: "#070B14",
          surface: "#0D1422",
          card: "#111B2E",
          cardHover: "#162238",
          border: "#1E293B",
          borderHover: "#2E3F57",
          cyan: "#00D9FF",
          cyanGlow: "rgba(0, 217, 255, 0.15)",
          purple: "#7C3AED",
          purpleGlow: "rgba(124, 58, 237, 0.15)",
          text: "#F8FAFC",
          muted: "#94A3B8",
          subtle: "#64748B",
          success: "#22C55E",
          warning: "#F59E0B",
          error: "#EF4444",
          insane: "#A855F7",
        },
      },
      boxShadow: {
        cyan: "0 0 20px rgba(0, 217, 255, 0.25)",
        "cyan-sm": "0 0 10px rgba(0, 217, 255, 0.15)",
        purple: "0 0 20px rgba(124, 58, 237, 0.25)",
        card: "0 4px 20px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [],
} satisfies Config;
