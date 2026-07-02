import { useLocation, Link, Navigate } from "react-router-dom"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardHeader, CardTitle, CardContent } from "../../shared/ui/card"
import { Badge } from "../../shared/ui/badge"
import { Button } from "../../shared/ui/button"

export default function Results() {
  const location = useLocation()
  const prediction = location.state?.prediction

  if (!prediction) {
    return <Navigate to="/predict" replace />
  }

  const { admission_probability, risk_level, predicted_closing_rank, user_rank, explanation } = prediction
  
  const probPercent = Math.round(admission_probability * 100)
  const chartData = [
    { name: "Probability", value: probPercent },
    { name: "Remaining", value: 100 - probPercent }
  ]
  
  // Custom professional colors
  const COLORS = ['#10b981', '#f1f5f9']
  if (risk_level === 'Reach') COLORS[0] = '#f59e0b'
  if (risk_level === 'Unlikely') COLORS[0] = '#ef4444'

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-8">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Prediction Results</h1>
          <p className="text-muted-foreground mt-1">Based on JoSAA historical cutoffs and model inference.</p>
        </div>
        <Link to="/predict">
          <Button variant="outline" className="h-10">Run Another Prediction</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="shadow-md border-border/60">
          <CardHeader className="bg-muted/30 pb-4 border-b">
            <CardTitle className="text-lg">Admission Probability</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center pt-8">
            <div className="h-56 w-56 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    innerRadius={75}
                    outerRadius={95}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                    cornerRadius={4}
                  >
                    {chartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-4xl font-black">{probPercent}%</span>
              </div>
            </div>
            
            <div className="mt-8 flex flex-col items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Classification</span>
              <Badge 
                variant={risk_level === 'Safe' ? 'success' : risk_level === 'Target' ? 'default' : 'warning'}
                className="text-sm px-4 py-1"
              >
                {risk_level}
              </Badge>
            </div>
          </CardContent>
        </Card>
        
        <div className="space-y-8">
          <Card className="shadow-md border-border/60">
            <CardHeader className="bg-muted/30 pb-4 border-b">
              <CardTitle className="text-lg">Why did you get this result?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-border/50">
                  <span className="text-muted-foreground font-medium">Your JEE Main Rank</span>
                  <span className="font-bold text-lg">{user_rank.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-border/50">
                  <span className="text-muted-foreground font-medium">Predicted Closing Rank</span>
                  <span className="font-bold text-lg">{predicted_closing_rank.toLocaleString()}</span>
                </div>
              </div>
              
              {explanation && (
                <div className="mt-8 p-5 bg-primary/5 border border-primary/10 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                    <h4 className="font-semibold text-primary">What Influenced This?</h4>
                  </div>
                  <p className="text-sm text-foreground/80 leading-relaxed">
                    {explanation.human_summary}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="shadow-md border-border/60 bg-slate-50">
            <CardHeader className="pb-4 border-b border-slate-200">
              <CardTitle className="text-lg">What Should You Do Next?</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {risk_level === 'Safe' && (
                <p className="text-sm text-slate-700 leading-relaxed">
                  <strong>This is a solid backup option.</strong> Your rank is comfortably above the predicted cutoff. Keep this college high on your preference list, but don't stop here—you should actively explore higher-tier "Dream" and "Target" colleges for your upper preferences.
                </p>
              )}
              {risk_level === 'Target' && (
                <p className="text-sm text-slate-700 leading-relaxed">
                  <strong>This is highly competitive.</strong> You have a strong chance, but it may come down to the final rounds of counselling. Ensure you have 3-4 "Safe" colleges listed below this one to guarantee you secure a seat.
                </p>
              )}
              {risk_level === 'Reach' && (
                <p className="text-sm text-slate-700 leading-relaxed">
                  <strong>Keep this as an aspirational choice.</strong> It's possible to get this seat if cutoff trends drop this year, so place it at the very top of your preference list. However, you absolutely must secure your lower preferences with Target and Safe colleges.
                </p>
              )}
              {risk_level === 'Unlikely' && (
                <p className="text-sm text-slate-700 leading-relaxed">
                  <strong>Pivot your strategy.</strong> Based on historical data, this seat is statistically out of reach. We highly recommend exploring other branches at this college, or looking at GFTIs and state-level colleges where your rank is more competitive.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
