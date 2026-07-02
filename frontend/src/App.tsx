import { createBrowserRouter, RouterProvider } from "react-router-dom"
import Layout from "./layout/Layout"
import Home from "./features/home/Home"
import PredictionForm from "./features/prediction/PredictionForm"
import Results from "./features/results/Results"

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Home />
      },
      {
        path: "predict",
        element: <PredictionForm />
      },
      {
        path: "results",
        element: <Results />
      }
    ]
  }
])

export default function App() {
  return <RouterProvider router={router} />
}
