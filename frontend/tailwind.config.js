/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#3B82F6",
          dark: "#2563EB",
          light: "#93C5FD"
        },
        secondary: {
          DEFAULT: "#10B981", 
          dark: "#059669",
          light: "#6EE7B7"
        },
        background: {
          DEFAULT: "#F9FAFB",
          dark: "#1F2937"
        },
        surface: {
          DEFAULT: "#FFFFFF",
          dark: "#374151"
        },
        error: "#EF4444",
        warning: "#F59E0B",
        success: "#10B981",
        info: "#3B82F6"
      },
      fontFamily: {
        sans: ["Inter var", "Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Liberation Mono", "Courier New", "monospace"]
      },
      borderRadius: {
        none: "0",
        sm: "0.25rem",
        DEFAULT: "0.375rem",
        md: "0.5rem",
        lg: "0.75rem",
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
        full: "9999px"
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        DEFAULT: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
        md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
        lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
        xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
        "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        inner: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)",
        none: "none"
      },
      spacing: {
        72: "18rem",
        80: "20rem",
        96: "24rem",
        112: "28rem",
        128: "32rem",
        144: "36rem",
        160: "40rem"
      },
      animation: {
        "spin-slow": "spin 3s linear infinite",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "bounce-slow": "bounce 3s infinite",
        "fade-in": "fadeIn 0.5s ease-in forwards",
        "fade-out": "fadeOut 0.5s ease-out forwards"
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" }
        },
        fadeOut: {
          "0%": { opacity: "1" },
          "100%": { opacity: "0" }
        }
      }
    }
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
    require("@tailwindcss/line-clamp")
  ],
  darkMode: "class"
}