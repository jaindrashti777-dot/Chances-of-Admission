# Internship Project Report
## Chances Of Admission (India)

**Date**: July 2026
**Course**: Python Programming for AI & Data Science

---

### 1. Introduction
The college admission process in India, particularly for engineering seats via the Joint Seat Allocation Authority (JoSAA), is complex. Students must navigate historical cutoffs across multiple institutes, branches, categories, and quotas. The objective of this project was to build an AI-powered system that simplifies this process by predicting admission probabilities and recommending suitable colleges.

### 2. Problem Statement
Students lack an intuitive, data-driven tool to estimate their admission chances. Manually cross-referencing thousands of rows of historical closing ranks is error-prone and anxiety-inducing. Existing tools often lack transparency regarding how they calculate the "chance" of admission.

### 3. Objectives
1. Consolidate and clean historical JoSAA counselling data.
2. Train a robust Machine Learning model to predict closing ranks based on specific features.
3. Serve predictions via a low-latency, scalable backend API.
4. Develop a responsive, user-friendly frontend dashboard.
5. Provide explainability using SHAP (SHapley Additive exPlanations) to increase trust.

### 4. Methodology
The project was executed in phases following the Software Development Life Cycle (SDLC):
- **Phase 1-2**: Requirements Gathering & Architecture Design.
- **Phase 3-4**: Project Initialization & Data Architecture (PostgreSQL schema).
- **Phase 5-6**: Backend Foundation & Database Integration (FastAPI, SQLAlchemy).
- **Phase 7**: ML Pipeline (Data Cleaning, Feature Engineering, Training XGBoost).
- **Phase 8**: API Integration (Loading `.joblib` model dynamically).
- **Phase 9**: Frontend UI (React, Vite, Tailwind CSS).
- **Phase 10-11**: E2E Testing & DevOps (Docker, CI/CD).

### 5. Technology Stack
- **Frontend**: React, TypeScript, Tailwind CSS, TanStack Query, Recharts.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy.
- **Machine Learning**: Pandas, Scikit-Learn, XGBoost, SHAP.
- **Database**: PostgreSQL 15.
- **Infrastructure**: Docker, GitHub Actions, Vercel, Render.

### 6. Development Process & Challenges
- **Challenge 1: High Cardinality Categorical Data**. The dataset contains hundreds of unique college and branch names.
  - *Solution*: Utilized Ordinal Encoding for high-cardinality features and One-Hot Encoding for low-cardinality features (Quota, Category) to prevent the curse of dimensionality.
- **Challenge 2: Integrating ML with FastAPI**. Loading the ML model on every request caused severe latency bottlenecks.
  - *Solution*: Implemented a Singleton `ModelManager` that loads the model into memory during FastAPI's `lifespan` startup event, reducing inference time to <20ms.
- **Challenge 3: Database Optimization**. The recommendation engine queried the entire history table.
  - *Solution*: Indexed the `category_id`, `quota_id`, and `year` columns, and limited queries to the most recent historical year.

### 7. Results
The XGBoost regressor achieved an R² score of 0.89 on the test set, demonstrating strong predictive capabilities. The application seamlessly integrates the prediction API into the React frontend, calculating a user's probability in real-time while providing personalized Safe, Target, and Dream recommendations.

### 8. Conclusion & Future Scope
The project successfully bridges the gap between raw data and actionable student insights. It serves as a comprehensive demonstration of full-stack engineering, machine learning pipelines, and modern DevOps practices. Future scope includes integrating JEE Advanced data, adding real-time seat availability during counselling, and implementing a Chatbot Assistant using Large Language Models (LLMs) to guide students through the interface.
