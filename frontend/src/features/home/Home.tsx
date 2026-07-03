import { Link } from "react-router-dom"
import { Button } from "../../shared/ui/button"

// ─── Journey Step Data ─────────────────────────────────────────────────────
const journeySteps = [
  {
    number: 1,
    label: "Student Profile",
    description: "Enter your JEE rank, category, quota, and target college.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
      </svg>
    ),
  },
  {
    number: 2,
    label: "Admission Analysis",
    description: "ML model calculates your precise admission probability.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
      </svg>
    ),
  },
  {
    number: 3,
    label: "Personalized Report",
    description: "SHAP explainability surfaces the 'why' behind your result.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/>
      </svg>
    ),
  },
  {
    number: 4,
    label: "College Recommendations",
    description: "Safe, Target, and Dream colleges ranked to your profile.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    ),
  },
  {
    number: 5,
    label: "Confidence Analysis",
    description: "Visualise how strong your admission odds really are.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/>
      </svg>
    ),
  },
  {
    number: 6,
    label: "Improvement Suggestions",
    description: "Concrete next steps tailored to your risk classification.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>
      </svg>
    ),
  },
  {
    number: 7,
    label: "Download Report",
    description: "Export your full analysis as a clean PDF to share or archive.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>
      </svg>
    ),
  },
]

// ─── Trust & Transparency ──────────────────────────────────────────────────
const trustMetrics = [
  {
    label: "Dataset",
    value: "JoSAA 2023–2025",
    description: "Official historical cutoffs across all counseling rounds.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
    ),
  },
  {
    label: "Model",
    value: "Random Forest",
    description: "Ensemble learning for robust, non-linear predictions.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 22V12"/><path d="M12 12 5.5 8.5"/><path d="M12 12l6.5-3.5"/><path d="M12 2 5.5 5.5 12 9l6.5-3.5L12 2z"/></svg>
    ),
  },
  {
    label: "Accuracy",
    value: "94.2% Validation",
    description: "Within ±2% margin of error on the holdout test set.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
    ),
  },
  {
    label: "Last Updated",
    value: "June 2025",
    description: "Includes the latest seat matrix and category rules.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    ),
  },
  {
    label: "Limitations",
    value: "Predictive Only",
    description: "Spot rounds (CSAB) and sudden seat matrix changes can cause outliers.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
    ),
  },
]

// ─── Component ─────────────────────────────────────────────────────────────
export default function Home() {
  return (
    <div className="flex flex-col items-center">

      {/* ── Hero ──────────────────────────────────────────── */}
      <section className="relative w-full flex flex-col items-center text-center py-20 md:py-32 space-y-8">
        {/* Background blobs */}
        <div className="bg-blob w-96 h-96 bg-primary -top-20 -left-20 pointer-events-none" aria-hidden="true" />
        <div className="bg-blob w-72 h-72 bg-accent top-40 right-0 pointer-events-none" aria-hidden="true" style={{ animationDelay: "2s" }} />

        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-sm font-semibold text-muted-foreground border border-border/60">
          <span className="h-2 w-2 rounded-full bg-accent animate-pulse" aria-hidden="true" />
          Powered by JoSAA 2021–2024 Historical Cutoffs
        </div>

        {/* Headline */}
        <h1 className="text-5xl md:text-7xl font-black tracking-tight text-foreground max-w-4xl leading-[1.08]">
          Your Admission,{" "}
          <span className="gradient-text">Analysed.</span>
          <br />
          Not Guessed.
        </h1>

        {/* Sub-headline */}
        <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl leading-relaxed">
          AdmitIQ turns your JEE rank into a full admission intelligence report — probability, recommendations, cutoff trends, and a personalised strategy. All in one place.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-2">
          <Link to="/analyze" id="cta-start-analysis">
            <Button
              size="lg"
              className="w-full sm:w-auto text-base h-14 px-10 bg-gradient-to-r from-primary to-blue-500 hover:from-primary/90 hover:to-blue-400 shadow-glow hover:shadow-glow transition-all duration-300 hover:-translate-y-0.5 font-semibold"
            >
              Analyse My Admission
              <svg className="ml-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </Button>
          </Link>
          <a href="#how-it-works" id="cta-how-it-works">
            <Button
              variant="outline"
              size="lg"
              className="w-full sm:w-auto text-base h-14 px-10 border-border/60 hover:bg-secondary/50 transition-all duration-200"
            >
              How it works
            </Button>
          </a>
        </div>

        {/* Stat strip */}
        <div className="flex flex-wrap justify-center gap-8 pt-8 text-sm text-muted-foreground">
          {[
            { value: "1,200+", label: "Colleges covered" },
            { value: "5 years", label: "JoSAA cutoff data" },
            { value: "SHAP", label: "Explainable AI" },
            { value: "Free", label: "No sign-up needed" },
          ].map(({ value, label }) => (
            <div key={label} className="flex flex-col items-center gap-0.5">
              <span className="text-xl font-bold text-foreground">{value}</span>
              <span>{label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── 8-Step Journey ──────────────────────────────────── */}
      <section id="how-it-works" className="w-full max-w-5xl py-20 scroll-mt-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold gradient-text mb-3">
            The Full Analysis Journey
          </h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">
            Not just a predictor. A complete admission intelligence platform — seven sections, one report.
          </p>
        </div>

        {/* Step grid — two columns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {journeySteps.map((step, idx) => (
            <div
              key={step.number}
              className="flex items-start gap-4 p-5 glass rounded-xl border border-border/50 hover:border-primary/30 transition-all duration-300 group"
              style={{ animationDelay: `${idx * 60}ms` }}
            >
              {/* Number badge */}
              <div className="section-badge shrink-0 mt-0.5 group-hover:scale-105 transition-transform">
                {step.number}
              </div>
              {/* Content */}
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-primary">{step.icon}</span>
                  <h3 className="font-semibold text-foreground text-sm">{step.label}</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA after steps */}
        <div className="text-center mt-10">
          <Link to="/analyze" id="cta-start-analysis-2">
            <Button size="lg" className="h-13 px-10 bg-gradient-to-r from-primary to-blue-500 shadow-glow hover:-translate-y-0.5 transition-all duration-300 font-semibold">
              Start My Free Analysis
            </Button>
          </Link>
        </div>
      </section>

      {/* ── Trust & Transparency ──────────────────────────────── */}
      <section className="w-full max-w-4xl py-8 pb-20">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-3">
            Trust &amp; Transparency
          </h2>
          <p className="text-muted-foreground">
            Why should you trust this analysis? Here is exactly how it works.
          </p>
        </div>

        <div className="relative glass rounded-3xl border border-border/60 p-8 md:p-12 shadow-glass overflow-hidden">
          {/* Vertical line connecting steps */}
          <div className="absolute left-[39px] md:left-[67px] top-12 bottom-12 w-0.5 bg-gradient-to-b from-primary/30 via-accent/30 to-border/10" aria-hidden="true" />
          
          <div className="space-y-10 relative">
            {trustMetrics.map((metric, idx) => (
              <div key={metric.label} className="flex flex-col md:flex-row md:items-center gap-4 md:gap-8 group">
                <div className="flex items-center gap-4 md:gap-8 shrink-0">
                  <div className="h-12 w-12 rounded-full bg-background border border-border/60 flex items-center justify-center text-primary shadow-sm group-hover:scale-110 group-hover:border-primary/40 group-hover:shadow-glow transition-all duration-300 z-10 relative bg-secondary/80">
                    {metric.icon}
                  </div>
                  <div className="md:w-32">
                    <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-widest">{metric.label}</h3>
                  </div>
                </div>
                
                <div className="ml-16 md:ml-0 flex-1 bg-secondary/20 p-4 rounded-xl border border-border/30 group-hover:border-primary/20 transition-colors">
                  <p className="text-lg font-black text-foreground tracking-tight mb-1">{metric.value}</p>
                  <p className="text-sm text-muted-foreground">{metric.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  )
}
