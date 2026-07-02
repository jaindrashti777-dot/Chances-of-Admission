import { Link, Outlet } from "react-router-dom"
import { BarChart3 } from "lucide-react"

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center px-4">
          <div className="flex items-center gap-2 font-bold text-lg">
            <BarChart3 className="h-5 w-5 text-primary" />
            <Link to="/">Chances of Admission</Link>
          </div>
          <nav className="ml-auto flex gap-4 text-sm font-medium">
            <Link to="/" className="hover:text-primary transition-colors">Home</Link>
            <Link to="/predict" className="hover:text-primary transition-colors">Predict</Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 flex flex-col items-center p-4 md:p-8">
        <div className="w-full max-w-6xl">
          <Outlet />
        </div>
      </main>
      <footer className="border-t py-6">
        <div className="container px-4 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Chances of Admission (India). Internship Project.</p>
        </div>
      </footer>
    </div>
  )
}
