import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useNavigate } from "react-router-dom"
import { usePredictAdmission } from "../../services/api/queries"

import { Button } from "../../shared/ui/button"
import { Input } from "../../shared/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "../../shared/ui/card"

const schema = z.object({
  user_rank: z.number().min(1, "Rank must be greater than 0"),
  college_name: z.string().min(2, "College name is required"),
  branch_name: z.string().min(2, "Branch name is required"),
  institute_type: z.string().min(2, "Institute type is required"),
  category: z.string().min(1, "Category is required"),
  quota: z.string().min(1, "Quota is required"),
  seat_pool: z.string().min(1, "Seat pool is required"),
  counselling_body: z.string(),
  year: z.number(),
  round_number: z.number(),
})

type FormData = z.infer<typeof schema>

export default function PredictionForm() {
  const navigate = useNavigate()
  const { mutate, isPending, error } = usePredictAdmission()
  
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      institute_type: "NIT",
      category: "OPEN",
      quota: "OS",
      seat_pool: "Gender-Neutral",
      counselling_body: "JoSAA",
      year: 2024,
      round_number: 6
    }
  })

  const onSubmit = (data: FormData) => {
    mutate(data, {
      onSuccess: (res) => {
        navigate("/results", { state: { prediction: res } })
      }
    })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Enter Prediction Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label className="text-sm font-semibold mb-1.5 block">JEE Main Rank</label>
              <Input type="number" {...register("user_rank", { valueAsNumber: true })} placeholder="e.g. 1500" className="h-12" />
              {errors.user_rank && <p className="text-sm text-destructive mt-1.5">{errors.user_rank.message}</p>}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="text-sm font-semibold mb-1.5 block">College Name</label>
                <Input {...register("college_name")} placeholder="e.g. NIT Trichy" className="h-12" />
                {errors.college_name && <p className="text-sm text-destructive mt-1.5">{errors.college_name.message}</p>}
              </div>
              <div>
                <label className="text-sm font-semibold mb-1.5 block">Branch Name</label>
                <Input {...register("branch_name")} placeholder="e.g. Computer Science" className="h-12" />
                {errors.branch_name && <p className="text-sm text-destructive mt-1.5">{errors.branch_name.message}</p>}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div>
                <label className="text-sm font-semibold mb-1.5 block">Category</label>
                <select 
                  {...register("category")} 
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="OPEN">OPEN (General)</option>
                  <option value="OBC-NCL">OBC-NCL</option>
                  <option value="SC">SC</option>
                  <option value="ST">ST</option>
                  <option value="EWS">EWS</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-semibold mb-1.5 block">State Quota</label>
                <select 
                  {...register("quota")} 
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="OS">Other State (OS)</option>
                  <option value="HS">Home State (HS)</option>
                  <option value="AI">All India (AI)</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-semibold mb-1.5 block">Institute Type</label>
                <select 
                  {...register("institute_type")} 
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="NIT">NIT</option>
                  <option value="IIIT">IIIT</option>
                  <option value="GFTI">GFTI</option>
                  <option value="IIT">IIT</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-destructive/10 border border-destructive/20 text-destructive rounded-md text-sm font-medium">
                Prediction failed. Please check your inputs and try again.
              </div>
            )}
            
            <Button type="submit" className="w-full h-12 text-lg shadow-md" disabled={isPending}>
              {isPending ? "Running Prediction Model..." : "Calculate Probability"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
