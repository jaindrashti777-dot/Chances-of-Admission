import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useNavigate } from "react-router-dom"
import { usePredictAdmission } from "../../services/api/queries"
import { Button } from "../../shared/ui/button"
import { Input } from "../../shared/ui/input"

// ─── Validation Schema ─────────────────────────────────────────────────────
const schema = z.object({
  user_rank:        z.number({ invalid_type_error: "Enter a valid rank" }).min(1, "Rank must be at least 1"),
  college_name:     z.string().min(2, "College name is required"),
  branch_name:      z.string().min(2, "Branch / programme is required"),
  institute_type:   z.string().min(1),
  category:         z.string().min(1),
  quota:            z.string().min(1),
  seat_pool:        z.string().min(1),
  counselling_body: z.string(),
  year:             z.number(),
  round_number:     z.number(),
})

type FormData = z.infer<typeof schema>

// ─── Styled Select ─────────────────────────────────────────────────────────
const selectCls =
  "flex h-12 w-full rounded-lg border border-input bg-secondary/40 px-3 py-2 text-sm text-foreground " +
  "ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 " +
  "hover:border-primary/40 transition-colors duration-200"

// ─── Component ─────────────────────────────────────────────────────────────
export default function PredictionForm() {
  const navigate = useNavigate()
  const { mutate, isPending, error } = usePredictAdmission()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      institute_type:   "NIT",
      category:         "OPEN",
      quota:            "OS",
      seat_pool:        "Gender-Neutral",
      counselling_body: "JoSAA",
      year:             2024,
      round_number:     6,
    },
  })

  const onSubmit = (data: FormData) => {
    mutate(data, {
      onSuccess: (res) => {
        navigate("/results", { state: { prediction: res, profile: data } })
      },
    })
  }

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center py-12">
      {/* ── Page Header ───────────────────────────────────── */}
      <div className="text-center mb-10 max-w-xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass text-xs font-semibold text-muted-foreground border border-border/60 mb-4">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />
          Step 1 of 1 — Student Profile
        </div>
        <h1 className="text-4xl font-black tracking-tight text-foreground mb-3">
          Build Your <span className="gradient-text">Student Profile</span>
        </h1>
        <p className="text-muted-foreground leading-relaxed">
          Tell us your rank, target college, and eligibility — AdmitIQ will generate your complete admission analysis in seconds.
        </p>
      </div>

      {/* ── Form Card ─────────────────────────────────────── */}
      <div className="w-full max-w-2xl glass rounded-2xl border border-border/60 shadow-glass p-8 md:p-10">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8" noValidate>

          {/* ── Rank ──────────────────────────────────────── */}
          <div>
            <label htmlFor="user_rank" className="text-sm font-semibold mb-2 block text-foreground">
              JEE Main Rank
              <span className="text-muted-foreground font-normal ml-1">(CRL / Category rank as applicable)</span>
            </label>
            <Input
              id="user_rank"
              type="number"
              {...register("user_rank", { valueAsNumber: true })}
              placeholder="e.g. 15000"
              className="h-13 text-base bg-secondary/40 border-input hover:border-primary/40 transition-colors"
            />
            {errors.user_rank && (
              <p className="text-sm text-destructive mt-1.5 flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-7v2h2v-2h-2zm0-8v6h2V7h-2z"/></svg>
                {errors.user_rank.message}
              </p>
            )}
          </div>

          {/* ── College + Branch ──────────────────────────── */}
          <div>
            <p className="text-sm font-semibold mb-3 text-foreground">Target College & Programme</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="college_name" className="text-xs text-muted-foreground mb-1.5 block">College Name</label>
                <Input
                  id="college_name"
                  {...register("college_name")}
                  placeholder="e.g. NIT Trichy"
                  className="h-12 bg-secondary/40 border-input hover:border-primary/40 transition-colors"
                />
                {errors.college_name && (
                  <p className="text-xs text-destructive mt-1">{errors.college_name.message}</p>
                )}
              </div>
              <div>
                <label htmlFor="branch_name" className="text-xs text-muted-foreground mb-1.5 block">Branch / Programme</label>
                <Input
                  id="branch_name"
                  {...register("branch_name")}
                  placeholder="e.g. Computer Science"
                  className="h-12 bg-secondary/40 border-input hover:border-primary/40 transition-colors"
                />
                {errors.branch_name && (
                  <p className="text-xs text-destructive mt-1">{errors.branch_name.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* ── Eligibility ───────────────────────────────── */}
          <div>
            <p className="text-sm font-semibold mb-3 text-foreground">Eligibility Details</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="category" className="text-xs text-muted-foreground mb-1.5 block">Category</label>
                <select id="category" {...register("category")} className={selectCls}>
                  <option value="OPEN">OPEN (General)</option>
                  <option value="OBC-NCL">OBC-NCL</option>
                  <option value="SC">SC</option>
                  <option value="ST">ST</option>
                  <option value="EWS">EWS</option>
                </select>
              </div>
              <div>
                <label htmlFor="quota" className="text-xs text-muted-foreground mb-1.5 block">State Quota</label>
                <select id="quota" {...register("quota")} className={selectCls}>
                  <option value="OS">Other State (OS)</option>
                  <option value="HS">Home State (HS)</option>
                  <option value="AI">All India (AI)</option>
                </select>
              </div>
              <div>
                <label htmlFor="institute_type" className="text-xs text-muted-foreground mb-1.5 block">Institute Type</label>
                <select id="institute_type" {...register("institute_type")} className={selectCls}>
                  <option value="NIT">NIT</option>
                  <option value="IIIT">IIIT</option>
                  <option value="GFTI">GFTI</option>
                  <option value="IIT">IIT</option>
                </select>
              </div>
            </div>
          </div>

          {/* ── Error Alert ───────────────────────────────── */}
          {error && (
            <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/30 text-destructive text-sm font-medium flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-7v2h2v-2h-2zm0-8v6h2V7h-2z"/></svg>
              Analysis failed. Please verify your inputs and try again.
            </div>
          )}

          {/* ── Submit ────────────────────────────────────── */}
          <Button
            id="btn-run-analysis"
            type="submit"
            disabled={isPending}
            className="w-full h-14 text-base font-semibold bg-gradient-to-r from-primary to-blue-500 hover:from-primary/90 hover:to-blue-400 shadow-glow hover:shadow-glow transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          >
            {isPending ? (
              <span className="flex items-center gap-3">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                Running Admission Analysis…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Run Admission Analysis
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </span>
            )}
          </Button>

          <p className="text-center text-xs text-muted-foreground">
            No account needed · Analysis runs instantly · Free forever
          </p>
        </form>
      </div>
    </div>
  )
}
