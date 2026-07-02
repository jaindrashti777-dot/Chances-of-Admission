import { Link } from "react-router-dom"
import { Button } from "../components/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col items-center text-center space-y-8 py-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
          Predict Your Engineering Admission Chances
        </h1>
        <p className="text-xl text-muted-foreground">
          Leverage historical counselling data and AI to estimate your probability of securing a seat in top NITs, IIITs, and GFTIs.
        </p>
      </div>
      <div className="flex gap-4">
        <Link to="/predict">
          <Button size="lg">Start Prediction</Button>
        </Link>
        <Link to="/about">
          <Button variant="outline" size="lg">Learn More</Button>
        </Link>
      </div>
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl text-left">
        <div className="p-6 border rounded-lg bg-card">
          <h3 className="font-semibold text-lg mb-2">Data-Driven</h3>
          <p className="text-muted-foreground">Based on years of JoSAA closing ranks to provide accurate estimates.</p>
        </div>
        <div className="p-6 border rounded-lg bg-card">
          <h3 className="font-semibold text-lg mb-2">AI Explainability</h3>
          <p className="text-muted-foreground">Understand exactly why a college is a Safe or Reach option.</p>
        </div>
        <div className="p-6 border rounded-lg bg-card">
          <h3 className="font-semibold text-lg mb-2">Smart Recommendations</h3>
          <p className="text-muted-foreground">Discover colleges you might not have considered based on your profile.</p>
        </div>
      </div>
    </div>
  )
}
