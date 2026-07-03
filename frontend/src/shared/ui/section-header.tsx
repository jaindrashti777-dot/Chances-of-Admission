interface SectionHeaderProps {
  number: number
  title: string
  subtitle?: string
  accent?: "primary" | "accent" | "success" | "warning"
}

const accentMap = {
  primary: "from-primary to-blue-400",
  accent:  "from-accent to-cyan-300",
  success: "from-success to-emerald-400",
  warning: "from-warning to-yellow-300",
}

export default function SectionHeader({
  number,
  title,
  subtitle,
  accent = "primary",
}: SectionHeaderProps) {
  return (
    <div className="flex items-start gap-4 mb-6">
      <div
        className={`section-badge bg-gradient-to-br ${accentMap[accent]} shrink-0 mt-0.5`}
      >
        {number}
      </div>
      <div>
        <h2 className="text-xl font-bold text-foreground tracking-tight leading-snug">
          {title}
        </h2>
        {subtitle && (
          <p className="text-sm text-muted-foreground mt-0.5">{subtitle}</p>
        )}
      </div>
    </div>
  )
}
