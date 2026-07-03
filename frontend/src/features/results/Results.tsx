import { useLocation, Link, Navigate } from "react-router-dom"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts"
import { useRecommendations, useHistoricalTrend } from "../../services/api/queries"
import SectionHeader from "../../shared/ui/section-header"

// ─── Types ─────────────────────────────────────────────────────────────────
interface Recommendation {
  college_name: string
  branch_name: string
  institute_type: string
  predicted_closing_rank: number
  match_type: "Safe" | "Target" | "Dream"
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function getRiskColor(risk: string) {
  switch (risk) {
    case "Safe":     return { text: "text-success", bg: "bg-success/15", border: "border-success/30", hex: "#34d399", label: "Safe" }
    case "Target":   return { text: "text-primary", bg: "bg-primary/15", border: "border-primary/30", hex: "#6366f1", label: "Target" }
    case "Reach":    return { text: "text-warning",  bg: "bg-warning/15",  border: "border-warning/30",  hex: "#f59e0b", label: "Reach" }
    case "Unlikely": return { text: "text-destructive", bg: "bg-destructive/15", border: "border-destructive/30", hex: "#ef4444", label: "Unlikely" }
    default:         return { text: "text-muted-foreground", bg: "bg-muted/15", border: "border-muted/30", hex: "#64748b", label: "Unknown" }
  }
}

// ─── Sub-components ────────────────────────────────────────────────────────

/** Section 1 — Executive Summary Grid */
function ExecutiveSummarySection({
  riskLevel,
  confidenceScore,
  closingRank,
  userRank,
}: {
  riskLevel: string
  confidenceScore: number
  closingRank: number
  userRank: number
}) {
  const riskColors = getRiskColor(riskLevel)
  const isHighConfidence = confidenceScore >= 0.75
  const confidenceText = isHighConfidence ? "High Confidence" : confidenceScore >= 0.5 ? "Moderate Confidence" : "Low Confidence"
  const confidenceColor = isHighConfidence ? "text-success" : confidenceScore >= 0.5 ? "text-primary" : "text-warning"
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Assessment */}
      <div className="glass rounded-2xl border border-border/60 p-6 flex flex-col justify-center items-center text-center">
        <div className="w-12 h-12 rounded-full bg-secondary/80 flex items-center justify-center mb-4 border border-border/40">
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={confidenceColor}><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/></svg>
        </div>
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">Admission Assessment</h3>
        <p className={`text-2xl font-black tracking-tight ${confidenceColor}`}>{confidenceText}</p>
        <p className="text-xs text-muted-foreground mt-2">Based on SHAP model confidence score: {Math.round(confidenceScore * 100)}%</p>
      </div>

      {/* Likely Admission Category */}
      <div className="glass rounded-2xl border border-border/60 p-6 flex flex-col justify-center items-center text-center relative overflow-hidden">
        <div className={`absolute top-0 left-0 w-full h-1`} style={{ background: riskColors.hex }} />
        <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 border ${riskColors.border} ${riskColors.bg}`}>
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={riskColors.text}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">Likely Admission Category</h3>
        <p className={`text-3xl font-black tracking-tight`} style={{ color: riskColors.hex }}>{riskLevel}</p>
        <p className="text-xs text-muted-foreground mt-2">Your rank {userRank.toLocaleString()} vs predicted cutoff</p>
      </div>

      {/* Estimated Closing Rank */}
      <div className="glass rounded-2xl border border-border/60 p-6 flex flex-col justify-center items-center text-center">
        <div className="w-12 h-12 rounded-full bg-secondary/80 flex items-center justify-center mb-4 border border-border/40">
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
        </div>
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">Estimated Closing Rank</h3>
        <p className="text-3xl font-black tracking-tight tabular-nums text-foreground">{closingRank.toLocaleString()}</p>
        <p className="text-xs text-muted-foreground mt-2">Predicted for final JoSAA round</p>
      </div>
    </div>
  )
}

/** Section 2 — Historical Trend */
function HistoricalTrendSection({
  collegeName,
  branchName,
  category,
  quota,
  predictedRank
}: {
  collegeName: string
  branchName: string
  category: string
  quota: string
  predictedRank: number
}) {
  const { data, isLoading, isError } = useHistoricalTrend(collegeName, branchName, category, quota)
  const trendData = data?.trend ?? []

  // Add the prediction as a final point if we have historical data
  const chartData = [...trendData]
  if (chartData.length > 0) {
     chartData.push({ year: 2024, closing_rank: predictedRank, isPrediction: true })
  }

  return (
    <div className="glass rounded-2xl border border-border/60 p-8">
      <SectionHeader
        number={2}
        title="Historical Trend"
        subtitle="Closing rank trajectory over recent years with predicted cutoff"
      />
      
      {isLoading && (
        <div className="h-64 w-full flex items-center justify-center">
           <div className="shimmer w-full h-full rounded-xl" />
        </div>
      )}

      {isError && (
        <div className="h-64 w-full flex items-center justify-center p-5 rounded-xl bg-muted/30 border border-border/40 text-sm text-muted-foreground">
          ⚠️ Historical trend data is currently unavailable.
        </div>
      )}

      {!isLoading && !isError && chartData.length > 0 && (
        <div className="h-[300px] w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
              <XAxis 
                dataKey="year" 
                stroke="#64748b" 
                tick={{ fill: '#64748b', fontSize: 12 }} 
                tickLine={false} 
                axisLine={false} 
              />
              <YAxis 
                stroke="#64748b" 
                tick={{ fill: '#64748b', fontSize: 12 }} 
                tickLine={false} 
                axisLine={false} 
                domain={['auto', 'auto']}
                reversed={true} // Lower rank is better, so it goes up
              />
              <Tooltip
                contentStyle={{
                  background: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                labelStyle={{ color: "hsl(var(--foreground))", fontWeight: "bold" }}
                itemStyle={{ color: "hsl(var(--primary))" }}
                formatter={(val: number, name: string, props: any) => [
                  val.toLocaleString(), 
                  props.payload.isPrediction ? "Predicted Rank" : "Closing Rank"
                ]}
              />
              <ReferenceLine x={2023} stroke="rgba(255,255,255,0.2)" strokeDasharray="3 3" />
              <Line 
                type="monotone" 
                dataKey="closing_rank" 
                stroke="hsl(var(--primary))" 
                strokeWidth={3}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.isPrediction) {
                    return <circle cx={cx} cy={cy} r={6} fill="hsl(var(--primary))" stroke="hsl(var(--background))" strokeWidth={2} />;
                  }
                  return <circle cx={cx} cy={cy} r={4} fill="hsl(var(--card))" stroke="hsl(var(--primary))" strokeWidth={2} />;
                }}
                activeDot={{ r: 8, fill: "hsl(var(--primary))", stroke: "hsl(var(--background))", strokeWidth: 2 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      {!isLoading && !isError && chartData.length === 0 && (
         <div className="p-5 rounded-xl bg-muted/30 border border-border/40 text-sm text-muted-foreground text-center">
            Not enough historical data available to plot a trend.
         </div>
      )}
    </div>
  )
}

/** Section 3 — Key Factors & Why this prediction? */
function PredictionInsightSection({
  explanation,
}: {
  explanation?: { 
     human_summary?: string
     top_positive_features?: Record<string, number>
     top_negative_features?: Record<string, number>
  }
}) {
  if (!explanation) return null;

  const posFeatures = Object.entries(explanation.top_positive_features || {});
  const negFeatures = Object.entries(explanation.top_negative_features || {});

  return (
    <div className="glass rounded-2xl border border-border/60 p-8">
      <SectionHeader
        number={3}
        title="Why this analysis?"
        subtitle="Key factors driving your estimated closing rank"
        accent="accent"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
         {/* Summary text */}
         <div className="p-6 rounded-xl bg-secondary/30 border border-border/40 flex flex-col justify-center">
           <div className="flex items-center gap-2 mb-4">
             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary shrink-0" aria-hidden="true">
               <path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
             </svg>
             <h4 className="text-base font-semibold text-foreground">Model Insight</h4>
           </div>
           <p className="text-sm text-foreground/85 leading-relaxed">
             {explanation.human_summary || "Our SHAP-based explainability model has analyzed the historical data and your profile to provide this estimate."}
           </p>
         </div>

         {/* Factors */}
         <div className="space-y-6">
            <div>
               <h5 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-3">Key Factors Supporting Admission</h5>
               {posFeatures.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                     {posFeatures.map(([feature, _weight]) => (
                        <div key={feature} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-success/10 border border-success/20 text-success text-xs font-medium">
                           <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                           {feature.replace(/_/g, ' ')}
                        </div>
                     ))}
                  </div>
               ) : (
                  <p className="text-xs text-muted-foreground italic">None significant</p>
               )}
            </div>

            <div>
               <h5 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-3">Key Factors Reducing Chances</h5>
               {negFeatures.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                     {negFeatures.map(([feature, _weight]) => (
                        <div key={feature} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium">
                           <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/></svg>
                           {feature.replace(/_/g, ' ')}
                        </div>
                     ))}
                  </div>
               ) : (
                  <p className="text-xs text-muted-foreground italic">None significant</p>
               )}
            </div>
         </div>
      </div>
    </div>
  )
}

/** Section 4 — Suggested Alternatives & Recommended Colleges */
function CollegeRecommendationsSection({
  userRank,
  category,
  quota,
}: {
  userRank: number
  category: string
  quota: string
}) {
  const { data, isLoading, isError } = useRecommendations(userRank, category, quota)
  const safe = data?.safe_colleges ?? []
  const target = data?.target_colleges ?? []
  const dream = data?.dream_colleges ?? []

  return (
    <div className="glass rounded-2xl border border-border/60 p-8">
      <SectionHeader
        number={4}
        title="Suggested Alternatives & Recommended Colleges"
        subtitle="Discover colleges tailored to your rank across Safe, Target, and Dream categories"
        accent="success"
      />

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-64 rounded-xl shimmer" />
          ))}
        </div>
      )}

      {isError && (
        <div className="p-5 rounded-xl bg-muted/30 border border-border/40 text-sm text-muted-foreground text-center">
          ⚠️ Could not load recommendations right now. The recommendations API may be unavailable.
        </div>
      )}

      {!isLoading && !isError && safe.length === 0 && target.length === 0 && dream.length === 0 && (
        <div className="p-5 rounded-xl bg-muted/30 border border-border/40 text-sm text-muted-foreground text-center">
          No recommendations returned. Try adjusting your rank or quota.
        </div>
      )}

      {!isLoading && (safe.length > 0 || target.length > 0 || dream.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Safe */}
          <div className="flex flex-col space-y-3">
            <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 text-success flex items-center gap-2`}>
              <span className="w-2 h-2 rounded-full bg-success"></span> Safe Colleges
            </h3>
            {safe.slice(0, 4).map((rec: Recommendation, i: number) => (
              <div key={i} className={`flex flex-col justify-between p-4 rounded-xl border border-success/30 bg-success/5 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-success/10 group h-full`}>
                <div>
                  <p className="text-sm font-semibold text-foreground leading-tight mb-1 group-hover:text-success transition-colors">{rec.college_name}</p>
                  <p className="text-xs text-muted-foreground">{rec.branch_name}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-success/10 flex justify-between items-end">
                  <span className="text-[10px] uppercase font-bold text-success/70 tracking-widest">{rec.institute_type}</span>
                  <div className="text-right">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest mb-0.5">Cutoff</p>
                    <p className="text-sm font-black tabular-nums text-foreground">{rec.predicted_closing_rank.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Target */}
          <div className="flex flex-col space-y-3">
            <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 text-primary flex items-center gap-2`}>
              <span className="w-2 h-2 rounded-full bg-primary"></span> Target Colleges
            </h3>
            {target.slice(0, 4).map((rec: Recommendation, i: number) => (
              <div key={i} className={`flex flex-col justify-between p-4 rounded-xl border border-primary/30 bg-primary/5 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-primary/10 group h-full`}>
                <div>
                  <p className="text-sm font-semibold text-foreground leading-tight mb-1 group-hover:text-primary transition-colors">{rec.college_name}</p>
                  <p className="text-xs text-muted-foreground">{rec.branch_name}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-primary/10 flex justify-between items-end">
                  <span className="text-[10px] uppercase font-bold text-primary/70 tracking-widest">{rec.institute_type}</span>
                  <div className="text-right">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest mb-0.5">Cutoff</p>
                    <p className="text-sm font-black tabular-nums text-foreground">{rec.predicted_closing_rank.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Dream / Reach */}
          <div className="flex flex-col space-y-3">
            <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 text-warning flex items-center gap-2`}>
              <span className="w-2 h-2 rounded-full bg-warning"></span> Dream Colleges
            </h3>
            {dream.slice(0, 4).map((rec: Recommendation, i: number) => (
              <div key={i} className={`flex flex-col justify-between p-4 rounded-xl border border-warning/30 bg-warning/5 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-warning/10 group h-full`}>
                <div>
                  <p className="text-sm font-semibold text-foreground leading-tight mb-1 group-hover:text-warning transition-colors">{rec.college_name}</p>
                  <p className="text-xs text-muted-foreground">{rec.branch_name}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-warning/10 flex justify-between items-end">
                  <span className="text-[10px] uppercase font-bold text-warning/70 tracking-widest">{rec.institute_type}</span>
                  <div className="text-right">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest mb-0.5">Cutoff</p>
                    <p className="text-sm font-black tabular-nums text-foreground">{rec.predicted_closing_rank.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  )
}

/** Section 5 — Download Report */
function DownloadReportSection() {
  const handlePrint = () => window.print()

  return (
    <div className="glass rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/8 to-accent/5 p-8 text-center mt-12 mb-20">
      <h3 className="text-xl font-bold text-foreground mb-2">Save your comprehensive report</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
        Your complete analysis report is ready. Click below to open your browser's print dialog — choose "Save as PDF" to export a clean A4 document.
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          id="btn-download-report"
          onClick={handlePrint}
          className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-primary to-blue-500 text-white shadow-glow hover:shadow-glow transition-all duration-300 hover:-translate-y-0.5 no-print"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          Download Report (PDF)
        </button>
        <Link
          to="/analyze"
          className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl text-sm font-medium border border-border/60 hover:bg-secondary/50 transition-colors no-print"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
          Analyse Another College
        </Link>
      </div>
    </div>
  )
}

// ─── Main Results Page ──────────────────────────────────────────────────────
export default function Results() {
  const location = useLocation()
  const prediction = location.state?.prediction
  const profile    = location.state?.profile

  if (!prediction) {
    return <Navigate to="/analyze" replace />
  }

  const { risk_level, predicted_closing_rank, user_rank, explanation, confidence_score } = prediction

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-8 animate-fade-in px-4 md:px-0">

      {/* ── Report Header ───────────────────────────────── */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-border/50">
        <div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
            <span className="gradient-text font-semibold">AdmitIQ</span>
            <span>›</span>
            <span>Admission Workspace</span>
          </div>
          <h1 className="text-3xl font-black tracking-tight">
            Analysis <span className="gradient-text">Report</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {profile?.college_name && profile?.branch_name
              ? `${profile.college_name} · ${profile.branch_name}`
              : "Based on JoSAA historical cutoffs and ML model inference"}
          </p>
        </div>
        <div className="flex items-center gap-3 no-print shrink-0">
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border border-border/60 hover:bg-secondary/50 transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
            New Analysis
          </Link>
        </div>
      </div>

      {/* ── Grid Sections ──────────────────────────────── */}
      
      <ExecutiveSummarySection 
        riskLevel={risk_level}
        confidenceScore={confidence_score ?? 0.8}
        closingRank={predicted_closing_rank}
        userRank={user_rank}
      />

      <PredictionInsightSection 
        explanation={explanation} 
      />

      {profile?.college_name && profile?.branch_name && (
        <HistoricalTrendSection 
          collegeName={profile.college_name}
          branchName={profile.branch_name}
          category={profile.category ?? "OPEN"}
          quota={profile.quota ?? "OS"}
          predictedRank={predicted_closing_rank}
        />
      )}

      <CollegeRecommendationsSection
        userRank={user_rank}
        category={profile?.category ?? "OPEN"}
        quota={profile?.quota ?? "OS"}
      />

      <DownloadReportSection />
    </div>
  )
}
