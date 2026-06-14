import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#FBFBF8",
        panel: "#FFFFFF",
        muted: "#6B7280",
        border: "#E5E7EB"
      }
    }
  },
  plugins: []
};

export default config;
