import { Link, Outlet, useLocation } from "react-router-dom"

function BrainIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {/* Stylised IQ-bolt / brain hybrid */}
      <path d="M12 2C8.5 2 6 4.5 6 7.5c0 1.5.5 2.8 1.4 3.8C5.5 12.4 4 14.2 4 16.5 4 19.5 6.5 22 10 22h4c3.5 0 6-2.5 6-5.5 0-2.3-1.5-4.1-3.4-5.2C17.5 10.3 18 9 18 7.5 18 4.5 15.5 2 12 2z" />
      <path d="M9 12h6M12 8v8" />
    </svg>
  )
}

const navLinks = [
  { to: "/",        label: "Home" },
  { to: "/analyze", label: "Analyze" },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 w-full glass border-b border-border/50">
        <div className="container flex h-14 items-center px-4 md:px-6 max-w-7xl mx-auto">
          {/* Brand */}
          <Link
            to="/"
            className="flex items-center gap-2 group"
            aria-label="AdmitIQ — Home"
          >
            <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-accent text-white shadow-glow group-hover:shadow-glow-accent transition-shadow duration-300">
              <BrainIcon />
            </div>
            <span className="font-bold text-lg tracking-tight">
              Admit<span className="gradient-text">IQ</span>
            </span>
          </Link>

          {/* Nav */}
          <nav className="ml-auto flex items-center gap-1" aria-label="Main navigation">
            {navLinks.map(({ to, label }) => {
              const isActive =
                to === "/"
                  ? location.pathname === "/"
                  : location.pathname.startsWith(to)
              return (
                <Link
                  key={to}
                  to={to}
                  className={[
                    "px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-primary/15 text-primary"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/60",
                  ].join(" ")}
                >
                  {label}
                </Link>
              )
            })}
          </nav>
        </div>
      </header>

      {/* ── Page Content ───────────────────────────────────── */}
      <main className="flex-1 flex flex-col">
        <div className="w-full max-w-7xl mx-auto px-4 md:px-6 py-8">
          <Outlet />
        </div>
      </main>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer className="border-t border-border/50 py-6 mt-auto no-print">
        <div className="container max-w-7xl mx-auto px-4 md:px-6 flex flex-col md:flex-row items-center justify-between gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-semibold gradient-text">AdmitIQ</span>
            <span>— India's Admission Analysis Platform</span>
          </div>
          <p>
            © {new Date().getFullYear()} AdmitIQ · Powered by JoSAA Historical Data · Internship Project
          </p>
        </div>
      </footer>
    </div>
  )
}
