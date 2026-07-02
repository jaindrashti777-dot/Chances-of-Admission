# Engineering Decisions & Trade-Offs

This document outlines the core architectural and technology choices made during the development of Chances of Admission. It details *why* specific tools were chosen, what alternatives were considered, and the inherent trade-offs of those decisions.

## 1. Backend Framework

**Decision:**
Use FastAPI.

**Alternatives:**
Flask, Django.

**Reason:**
Automatic OpenAPI documentation (Swagger UI) significantly reduces API communication friction. Pydantic provides strict type validation for the complex prediction schemas. Native async support ensures the server remains highly concurrent without blocking the event loop on network I/O.

**Trade-off:**
Smaller ecosystem than Django (no built-in admin panel or monolithic ORM), requiring more manual wiring of SQLAlchemy and Alembic.

---

## 2. Database

**Decision:**
Use PostgreSQL.

**Alternatives:**
MongoDB, MySQL, SQLite.

**Reason:**
The historical JoSAA cutoffs data is strictly tabular and highly relational (Colleges → Branches → Cutoffs → Categories). PostgreSQL is the industry standard for robust relational integrity and handles complex `JOIN` queries across multiple dimension tables highly efficiently.

**Trade-off:**
Requires rigid schema definitions and migrations (Alembic) compared to the flexibility of NoSQL databases like MongoDB. Slower to prototype with initially.

---

## 3. Machine Learning Model

**Decision:**
Use XGBoost Regressor.

**Alternatives:**
Linear Regression, Random Forest, Deep Neural Networks.

**Reason:**
XGBoost significantly outperforms deep learning approaches and standard Random Forests on structured, tabular datasets like historical closing ranks. It handles complex, non-linear interactions between categories, quotas, and college tiers exceptionally well. It also natively supports SHAP (SHapley Additive exPlanations) for model interpretability.

**Trade-off:**
More susceptible to overfitting than simpler linear models if hyperparameters (`max_depth`, `learning_rate`) are not rigorously tuned. Training takes longer than Random Forest.

---

## 4. Frontend Framework

**Decision:**
Use React with Vite.

**Alternatives:**
Next.js, Vue.js, Create React App (CRA).

**Reason:**
The frontend relies heavily on dynamic, state-driven interfaces (interactive forms, dynamic SVG charts). React's component model fits this perfectly. Vite was chosen over CRA for fundamentally faster Hot Module Replacement (HMR) and a leaner build footprint.

**Trade-off:**
React is a library, not a framework, requiring third-party libraries for routing (React Router) and data fetching (TanStack Query). Next.js would have provided Server-Side Rendering (SSR), but SSR is unnecessary for this highly interactive, behind-the-form dashboard.

---

## 5. Deployment

**Decision:**
Containerized backend (Docker + Render) and static frontend (Vercel).

**Alternatives:**
Monolith deployment on AWS EC2, Heroku.

**Reason:**
Vercel provides edge caching and instantaneous CI/CD for the React frontend out of the box. Dockerizing the FastAPI backend ensures the environment (Python 3.12, scikit-learn, joblib) is exactly the same in production as on the developer's machine, preventing "it works on my machine" ML dependency hell.

**Trade-off:**
Operating a distributed system (Vercel frontend calling a Render backend) introduces Cross-Origin Resource Sharing (CORS) complexity and potential network latency between the two cloud providers.

---

## 6. Recommendation Logic

**Decision:**
SQL-based heuristic for College Recommendations (Safe/Target/Dream).

**Alternatives:**
Running batch ML inference across all 3000+ college/branch combinations in real-time.

**Reason:**
Passing 3000+ permutations through the XGBoost model during a single web request would cause a massive latency bottleneck (seconds instead of milliseconds). By using the PostgreSQL database to quickly query and categorize colleges based on the previous year's cutoffs ± variance, we maintain <50ms response times.

**Trade-off:**
Slightly lower predictive precision for the broad recommendations compared to a full ML pass. The exact probability is only calculated precisely when a user explicitly predicts a *single* specific college and branch combination.
