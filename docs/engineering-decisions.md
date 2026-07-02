# Engineering Decisions & Trade-Offs

This document outlines the core architectural and technology choices made during the development of Chances of Admission, focusing on *why* specific tools were chosen and their trade-offs.

## Backend Framework

### Why FastAPI?
- **Speed & Asynchrony:** Our prediction endpoints involve loading a serialized ML model into memory and doing numerical processing. FastAPI's native async capabilities ensure the server remains highly concurrent without blocking the event loop on network I/O.
- **Pydantic Validation:** Strict validation of user data (ranks, quotas, categories) is critical for our model. Pydantic guarantees that bad inputs never reach the ML inference layer.
- **Auto-Documentation:** Built-in OpenAPI swagger docs reduce the friction between frontend development and backend updates.

### Why not Django or Flask?
- **Django:** Too "batteries-included." We don't need Django's built-in auth, admin panels, or monolithic ORM. The API needs to be lightweight and stateless.
- **Flask:** Lacks native async support and requires third-party plugins for type validation and documentation, whereas FastAPI provides these out of the box.

## Database

### Why PostgreSQL?
- **Relational Integrity:** The historical cutoffs data is strictly tabular and relational (Colleges → Branches → Cutoffs → Categories). A SQL database is the perfect fit.
- **Performance:** Complex queries to filter "Safe, Target, Dream" colleges based on closing ranks are highly optimized in Postgres.

## Machine Learning

### Why XGBoost?
- **Tabular Data Mastery:** XGBoost significantly outperforms deep learning approaches (like Neural Networks) on structured, tabular datasets like historical closing ranks.
- **Interpretability:** XGBoost natively supports SHAP (SHapley Additive exPlanations), allowing us to explain *exactly* why a prediction was made to the user.

## Frontend Architecture

### Why React & Vite?
- **React:** The frontend relies on dynamic, state-driven interfaces (interactive forms predicting live data, dynamic SVG charts for probabilities). React's component model fits this perfectly.
- **Vite:** Replaces Create React App (CRA) or Webpack due to fundamentally faster Hot Module Replacement (HMR) and native ES modules during development. It builds significantly faster and has a much leaner footprint.
