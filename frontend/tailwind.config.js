/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border:      "hsl(var(--border))",
        input:       "hsl(var(--input))",
        ring:        "hsl(var(--ring))",
        background:  "hsl(var(--background))",
        foreground:  "hsl(var(--foreground))",
        primary: {
          DEFAULT:    "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT:    "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT:    "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT:    "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT:    "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT:    "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
      },
      borderRadius: {
        lg:  "var(--radius)",
        md:  "calc(var(--radius) - 2px)",
        sm:  "calc(var(--radius) - 4px)",
        xl:  "calc(var(--radius) + 4px)",
        "2xl": "calc(var(--radius) + 8px)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-brand":  "linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--accent)) 100%)",
        "gradient-card":   "linear-gradient(135deg, hsl(var(--card)) 0%, hsl(var(--secondary)) 100%)",
      },
      boxShadow: {
        glass:   "0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(99,102,241,0.1)",
        glow:    "0 0 40px rgba(99, 102, 241, 0.25)",
        "glow-accent": "0 0 40px rgba(6, 182, 212, 0.2)",
        "glow-success": "0 0 30px rgba(52, 211, 153, 0.2)",
      },
      animation: {
        "fade-in":    "fade-in 0.6s ease forwards",
        "slide-up":   "slide-up 0.5s ease forwards",
        "pulse-glow": "pulse-glow 3s ease-in-out infinite",
        "spin-slow":  "spin-slow 20s linear infinite",
        "blob-drift": "blob-drift 8s ease-in-out infinite alternate",
        shimmer:      "shimmer 1.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
}
