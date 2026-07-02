# Internship Project Report
## Chances Of Admission (India)

**Date**: July 2026
**Course**: Python Programming for AI & Data Science

---

### 1. Introduction
The college admission process in India, particularly for engineering seats via the Joint Seat Allocation Authority (JoSAA), is complex. Students must navigate historical cutoffs across multiple institutes, branches, categories, and quotas. The objective of this project was to build a system that simplifies this process by predicting admission probabilities and recommending suitable colleges using supervised machine learning.

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

### 7. Machine Learning Architecture Review
To ensure the machine learning component is fully defensible and thoroughly engineered, the following design decisions were explicitly made:

- **Why this dataset?** JoSAA historical cutoff data is the definitive, official source of truth for engineering admissions in India. It contains millions of historical assignments that perfectly represent actual supply and demand. Using real historical closing ranks rather than synthetic data ensures the predictions directly map to real-world outcomes.
- **Why these features?** Categorical features like `institute_type`, `category`, and `quota` strictly segment the applicant pool, acting as hard filters. High-cardinality features like `college_name` and `branch_name` capture the specific prestige and demand of a degree. `year` and `round_number` capture temporal trends and the systematic tightening of seat availability over successive counselling rounds.
- **Why this algorithm?** The system evaluates Linear Regression, Random Forest, and XGBoost. XGBoost was chosen because regression on closing ranks involves highly non-linear interactions between categories, quotas, and college tiers. Tree-based gradient boosting models handle these complex, non-linear categorical splits exceptionally well and consistently outperform linear models and standard Random Forests on tabular data.
- **How was it evaluated?** The data was split using an 80/20 train-test split. The pipeline evaluates models using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R² Score. A `GridSearchCV` was used for rigorous hyperparameter tuning on the XGBoost model (optimizing `n_estimators`, `max_depth`, and `learning_rate`) with 3-fold cross-validation.
- **What are its limitations?** The model assumes future trends will largely mirror historical trends. Sudden structural shifts—such as a new IIT opening, abrupt changes in seat matrix quotas, or an unpredictable surge in popularity for AI branches—cannot be perfectly anticipated by the model. Furthermore, ordinal encoding of college names does not inherently capture semantic similarity between colleges of the same tier.
- **How would you retrain it?** The pipeline is entirely automated. To retrain, an engineer simply drops the new year's JoSAA cutoff CSV into `ml/data/raw/` and executes `python -m ml.src.models.train_model`. The script will automatically trigger data cleaning (`make_dataset.py`), re-run the `GridSearchCV`, export the newly optimized `best_model.joblib` to `ml/artifacts/`, and generate a fresh JSON metrics report in `ml/reports/`.

### 8. Results
The XGBoost regressor achieved an R² score of 0.89 on the test set, demonstrating strong predictive capabilities. The application seamlessly integrates the prediction API into the React frontend, calculating a user's probability in real-time while providing personalized Safe, Target, and Dream recommendations.

### 9. Conclusion & Future Scope
The project successfully bridges the gap between raw data and actionable student insights. It serves as a comprehensive demonstration of full-stack engineering, machine learning pipelines, and modern DevOps practices. Future scope includes integrating JEE Advanced data, adding real-time seat availability during counselling, and implementing a Chatbot Assistant using Large Language Models (LLMs) to guide students through the interface.
