import { useLocation, Link, Navigate } from "react-router-dom"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card"
import { Badge } from "../components/ui/badge"
import { Button } from "../components/ui/button"

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
  const COLORS = ['#10b981', '#f3f4f6']
  
  if (risk_level === 'Reach') COLORS[0] = '#f59e0b'
  if (risk_level === 'Unlikely') COLORS[0] = '#ef4444'

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Prediction Results</h1>
        <Link to="/predict"><Button variant="outline">New Prediction</Button></Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Admission Probability</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <div className="h-48 w-48 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {chartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-3xl font-bold">{probPercent}%</span>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <Badge variant={risk_level === 'Safe' ? 'success' : risk_level === 'Target' ? 'default' : 'warning'}>
                {risk_level}
              </Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Rank Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-muted-foreground">Your Rank</span>
              <span className="font-semibold">{user_rank}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-muted-foreground">Predicted Closing</span>
              <span className="font-semibold">{predicted_closing_rank}</span>
            </div>
            
            {explanation && (
              <div className="mt-6 p-4 bg-muted rounded-lg">
                <h4 className="font-semibold mb-2">AI Explanation</h4>
                <p className="text-sm text-muted-foreground">{explanation.human_summary}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
