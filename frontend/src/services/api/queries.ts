import { useMutation, useQuery } from "@tanstack/react-query"
import { apiClient } from "./client"

export interface PredictionRequest {
  user_rank: number
  college_name: string
  branch_name: string
  institute_type: string
  category: string
  quota: string
  seat_pool: string
  counselling_body: string
  year: number
  round_number: number
}

export const usePredictAdmission = () => {
  return useMutation({
    mutationFn: async (data: PredictionRequest) => {
      const response = await apiClient.post("/prediction/", data)
      return response.data
    },
  })
}

export const useRecommendations = (user_rank: number, category: string, quota: string) => {
  return useQuery({
    queryKey: ["recommendations", user_rank, category, quota],
    queryFn: async () => {
      const response = await apiClient.get("/prediction/recommendations", {
        params: { user_rank, category, quota },
      })
      return response.data
    },
    enabled: !!user_rank && !!category && !!quota,
  })
}

export const useHistoricalTrend = (college_name: string, branch_name: string, category: string, quota: string) => {
  return useQuery({
    queryKey: ["trend", college_name, branch_name, category, quota],
    queryFn: async () => {
      const response = await apiClient.get("/prediction/trend", {
        params: { college_name, branch_name, category, quota },
      })
      return response.data
    },
    enabled: !!college_name && !!branch_name && !!category && !!quota,
  })
}
