import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b0f12",
        panel: "#11171b",
        panel2: "#151d22",
        line: "#263139",
        muted: "#8a9aa4",
        paper: "#e8f0ed",
        teal: { DEFAULT: "#54d6c2", deep: "#1c8d82" },
        amber: "#e9b949",
        coral: "#f07f6b",
        ice: "#7db8ff",
      },
      fontFamily: {
        display: ["var(--font-newsreader)", "Georgia", "serif"],
        sans: ["var(--font-geist)", "ui-sans-serif", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 22px 80px rgba(0,0,0,.24)",
        insetline: "inset 0 1px 0 rgba(255,255,255,.04)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(123,154,162,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(123,154,162,.08) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
