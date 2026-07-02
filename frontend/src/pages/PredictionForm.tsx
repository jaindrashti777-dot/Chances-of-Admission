import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useNavigate } from "react-router-dom"
import { usePredictAdmission } from "../api/queries"

import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card"

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
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">JEE Rank</label>
              <Input type="number" {...register("user_rank", { valueAsNumber: true })} placeholder="e.g. 1500" />
              {errors.user_rank && <p className="text-sm text-destructive mt-1">{errors.user_rank.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">College Name</label>
                <Input {...register("college_name")} placeholder="e.g. NIT Trichy" />
                {errors.college_name && <p className="text-sm text-destructive mt-1">{errors.college_name.message}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Branch Name</label>
                <Input {...register("branch_name")} placeholder="e.g. Computer Science" />
                {errors.branch_name && <p className="text-sm text-destructive mt-1">{errors.branch_name.message}</p>}
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Category</label>
                <Input {...register("category")} placeholder="e.g. OPEN" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Quota</label>
                <Input {...register("quota")} placeholder="e.g. OS" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Institute</label>
                <Input {...register("institute_type")} placeholder="e.g. NIT" />
              </div>
            </div>

            {error && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                Prediction failed. Please check your inputs or try again later.
              </div>
            )}
            
            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? "Calculating..." : "Predict Probability"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
