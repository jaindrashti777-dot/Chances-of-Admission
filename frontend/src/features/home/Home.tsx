import { Link } from "react-router-dom"
import { Button } from "../../shared/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-6 max-w-4xl mx-auto">
        <div className="inline-flex items-center rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
          Powered by JoSAA Historical Cutoffs
        </div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground">
          Navigate Engineering Admissions <span className="text-primary">Without Guessing.</span>
        </h1>
        <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Stop relying on manual cutoff PDFs. Use our prediction engine to calculate your exact probability of securing a seat in top NITs, IIITs, and GFTIs.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <Link to="/predict">
            <Button size="lg" className="w-full sm:w-auto text-lg h-14 px-8 shadow-lg transition-transform hover:-translate-y-1">
              Start Free Prediction
            </Button>
          </Link>
          <Link to="/about">
            <Button variant="outline" size="lg" className="w-full sm:w-auto text-lg h-14 px-8">
              How it works
            </Button>
          </Link>
        </div>
      </div>

      {/* Feature Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl mt-20 text-left">
        <div className="p-8 border rounded-2xl bg-card shadow-sm hover:shadow-md transition-shadow">
          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
          </div>
          <h3 className="text-xl font-bold mb-3">Precision Analytics</h3>
          <p className="text-muted-foreground leading-relaxed">
            Our engine ingests thousands of past admission rounds to formulate highly accurate probability thresholds for your rank.
          </p>
        </div>
        
        <div className="p-8 border rounded-2xl bg-card shadow-sm hover:shadow-md transition-shadow">
          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <h3 className="text-xl font-bold mb-3">SHAP Explainability</h3>
          <p className="text-muted-foreground leading-relaxed">
            We don't just give you a percentage. We explain exactly which factors (Quota, Category, Year) influenced your chances.
          </p>
        </div>

        <div className="p-8 border rounded-2xl bg-card shadow-sm hover:shadow-md transition-shadow">
          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <h3 className="text-xl font-bold mb-3">Smart Discovery</h3>
          <p className="text-muted-foreground leading-relaxed">
            Input your rank and let our system automatically discover Safe, Target, and Dream colleges tailored to your profile.
          </p>
        </div>
      </div>
    </div>
  )
}
