import * as React from "react"
import { cn } from "../../lib/cn"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "secondary"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const variants: Record<string, string> = {
      default:   "bg-primary text-primary-foreground hover:bg-primary/85",
      outline:   "border border-border/60 bg-transparent text-foreground hover:bg-secondary/60 hover:border-border",
      secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/70",
      ghost:     "bg-transparent text-foreground hover:bg-secondary/50",
    }

    const sizes: Record<string, string> = {
      default: "h-10 px-4 py-2",
      sm:      "h-8 rounded-md px-3 text-xs",
      lg:      "h-11 rounded-lg px-8",
      icon:    "h-10 w-10",
    }

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium",
          "transition-all duration-200",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          "disabled:pointer-events-none disabled:opacity-50",
          variants[variant],
          sizes[size],
          className,
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
