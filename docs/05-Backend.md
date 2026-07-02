# Prediction API & Recommendation Engine

## Overview
This document describes the Prediction API design, the ML Model lifecycle integration, and the Recommendation Engine logic.

## ML Model Lifecycle
- **Startup (`lifespan`)**: FastAPI uses a context manager during startup to invoke `model_manager.load_model()`. The model `.joblib` is loaded into memory as a singleton to guarantee fast inference.
- **Graceful Degradation**: If the model artifact is missing, the service logs a warning but continues running. Any request to `/predict` will return a `503 Service Unavailable` instead of crashing.

## Endpoints

### 1. `POST /api/v1/prediction/`
Generates an admission probability for a single college and branch combination.
**Input (PredictionRequest)**:
- `user_rank` (int)
- `college_name` (str)
- `branch_name` (str)
- `category` (str)
- `quota` (str)
- etc.

**Output (PredictionResponse)**:
- `predicted_closing_rank` (int)
- `admission_probability` (float)
- `risk_level` ("Safe", "Target", "Reach", "Unlikely")
- `explanation`: Embedded SHAP explanations for top positive/negative factors.

### 2. `POST /api/v1/prediction/batch`
Accepts a list of `PredictionRequest` objects (up to 50) and processes them sequentially or via bulk inference depending on the optimization strategy.

### 3. `GET /api/v1/prediction/recommendations`
Queries the database historical cutoffs and uses a heuristic against the `user_rank` to return three lists:
- **Safe Colleges**: `user_rank` is significantly lower (better) than the closing rank (e.g., < 80%).
- **Target Colleges**: `user_rank` is close to the closing rank.
- **Dream Colleges**: `user_rank` is slightly higher (worse) than the closing rank (e.g., within 120%).

## Heuristic & Explainability
- **Probabilities**: Mapped from the distance between `user_rank` and `predicted_closing_rank`.
- **SHAP**: Extracts feature contributions from the model's tree explainer, returning human-readable factors (e.g., "Category Match: +120 Rank").
