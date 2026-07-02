import axios from "axios"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Optional: Interceptors for errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)
