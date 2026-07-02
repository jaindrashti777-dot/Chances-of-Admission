# Frontend Architecture

## Tech Stack
- **Framework**: React (Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, Class Variance Authority (CVA), `clsx`, `tailwind-merge`
- **State/Data Fetching**: TanStack React Query
- **Routing**: React Router DOM (v6 Data Router)
- **Forms**: React Hook Form with Zod validation
- **Visualization**: Recharts

## Design System
We implemented a minimalistic, scalable design system in `src/components/ui/`.
- **Button**: Handles primary, secondary, outline, and ghost variants.
- **Input**: Standardized text input with focus rings and error states.
- **Card**: Used for layout structures (Prediction Form, Result Visualizations).
- **Badge**: Indicates status (Safe, Target, Reach).

## Folder Structure
- `src/components/ui`: Reusable primitive components.
- `src/components/layout`: Shared layout wrappers (Navbar, Main Layout).
- `src/pages`: Top-level route components (Home, PredictionForm, Results).
- `src/api`: Axios client and TanStack query hooks.
- `src/utils`: Helper functions like the `cn` utility for Tailwind class merging.

## API Integration
The `apiClient` is an Axios instance configured in `src/api/client.ts`. TanStack query is used to manage asynchronous state (loading, error, success) gracefully, caching results to prevent redundant calls.

## Performance
- Global refetching on window focus is disabled in the QueryClient.
- Recharts is used for lightweight SVG-based data visualization.
- Tailwind ensures minimal CSS bundle sizes.
