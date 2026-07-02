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
      },
      {
        path: "about",
        element: <div className="text-center py-12"><h2 className="text-2xl font-bold">Methodology</h2><p className="mt-4 text-muted-foreground">Information about our ML models and datasets.</p></div>
      }
    ]
  }
])

export default function App() {
  return <RouterProvider router={router} />
}
