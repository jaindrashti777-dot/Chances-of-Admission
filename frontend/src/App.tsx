import { createBrowserRouter, RouterProvider } from "react-router-dom"
import Layout from "./components/layout/Layout"
import Home from "./pages/Home"
import PredictionForm from "./pages/PredictionForm"
import Results from "./pages/Results"

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
