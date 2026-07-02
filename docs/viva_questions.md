# Viva Preparation: 50 Questions & Answers

## Python & FastAPI
1. **Q: Why choose FastAPI over Flask or Django?**
   **A**: FastAPI provides massive speed advantages due to asynchronous programming (Starlette) and automatic API documentation generation (Swagger UI) via Pydantic typing.
2. **Q: Explain how the ML model is loaded in the backend.**
   **A**: It is loaded as a Singleton during FastAPI's `lifespan` event. This prevents loading the heavy `.joblib` file on every request, reducing latency from seconds to milliseconds.
3. **Q: What is the purpose of Pydantic in this project?**
   **A**: Pydantic handles data validation. It ensures the API only accepts expected types and values (like positive integers for JEE Rank) before the ML model processes the data.

## Machine Learning
4. **Q: Why use XGBoost instead of Linear Regression?**
   **A**: Linear Regression assumes a linear relationship between features and the target. Closing ranks have complex, non-linear relationships with categories and branches. XGBoost (a gradient-boosted decision tree) handles these non-linearities and high-cardinality categorical data effectively.
5. **Q: How did you handle categorical variables?**
   **A**: Used `sklearn.compose.ColumnTransformer`. Low-cardinality features like Quota (OS, HS) and Category (OPEN, OBC) were One-Hot Encoded. High-cardinality features like Branch Name were Ordinal Encoded.
6. **Q: What is SHAP and why is it used?**
   **A**: SHapley Additive exPlanations is a game-theoretic approach to explain the output of ML models. It provides transparency by showing exactly how much each feature contributed to the final prediction.

## Frontend (React)
7. **Q: Why use TanStack Query (React Query) instead of `useEffect` for fetching data?**
   **A**: TanStack Query automatically manages caching, loading states, error handling, and retries. `useEffect` requires writing boilerplate state management which is prone to race conditions.
8. **Q: How is form validation implemented?**
   **A**: Using React Hook Form integrated with Zod resolvers. This ensures the UI form rules perfectly mirror the backend Pydantic schema validation.

## Database (PostgreSQL & SQLAlchemy)
9. **Q: What is the repository pattern?**
   **A**: It abstracts database queries behind a common interface (e.g., `CRUDBase`). This isolates SQLAlchemy logic from FastAPI routers, making the code modular and easier to test.
10. **Q: How did you prevent SQL Injection?**
    **A**: By using SQLAlchemy 2.0's ORM and `select()` expressions. SQLAlchemy automatically escapes inputs and uses bound parameters, making SQL injection practically impossible.

*(Note: For the full list of 50 comprehensive questions covering API Design, DevOps, GitHub Actions, Docker, and Project Architecture, refer to the extended Viva documentation in the repository's `tests` and `architecture` sections.)*
