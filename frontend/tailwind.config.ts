import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#080B12",
        panel: "#0F172A",
        muted: "#94A3B8",
        border: "#1E293B"
      }
    }
  },
  plugins: []
};

export default config;
