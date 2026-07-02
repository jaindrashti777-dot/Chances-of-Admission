# System Architecture & Technical Design
## Chances of Admission (India)

---

| Document Attribute | Detail |
|---|---|
| **Project Name** | Chances of Admission (India) |
| **Document Version** | 1.0 |
| **Document Status** | Approved — Final Blueprint |
| **Category** | Industrial Training Project |
| **Course** | Python Programming for AI & Data Science |
| **Document Type** | System Architecture & Technical Design |
| **Prepared By** | Lead Software Architect |
| **Phase** | Phase 2 — System Architecture & Technical Design |

---

## 1. Overall System Architecture

The "Chances of Admission (India)" system is designed as a decoupled, multi-tier Client-Server application. It strictly separates the user interface from business logic and data persistence. 

The system comprises three primary tiers:
1.  **Client Tier (Frontend):** A Single Page Application (SPA) running in the user's web browser, responsible for all user interactions, input collection, and data visualization.
2.  **Application Tier (Backend API & ML Inference):** A stateless RESTful API server that handles business logic, data validation, authentication, and machine learning inference. The ML engine is integrated into this tier to provide low-latency predictions.
3.  **Data Tier (Database):** A relational database system responsible for persistent, secure, and structured storage of user profiles, historical counselling data, and system configurations.

This architecture ensures that the frontend and backend can evolve independently, be scaled based on their specific resource needs, and be maintained by specialized developers.

---

## 2. Architecture Pattern

**Recommended Pattern:** Clean Architecture (Domain-Centric Design)

**Why this is recommended:**
Clean Architecture organizes the system into concentric layers, prioritizing the core business domain over external frameworks or tools. The fundamental rule is the **Dependency Rule**: source code dependencies must point only inward, toward the core business logic.

-   **Framework Independence:** The core prediction and recommendation logic will not depend on FastAPI or PostgreSQL. If the web framework changes, the core logic remains untouched.
-   **Testability:** Business rules can be tested completely in isolation without requiring a web server, a database, or a UI. This is critical for validating ML pipelines and prediction accuracy.
-   **Maintainability:** By strictly separating concerns (e.g., routing, business logic, data access), the codebase remains readable and easy to navigate, which is essential for a high-quality portfolio project.

---

## 3. High-Level Component Diagram

The system consists of the following major logical components:

*   **Frontend Client (React SPA):** Handles routing, state management, UI rendering, and API communication. Contains modules for the Dashboard, Prediction Form, Data Visualization, and Admin Interface.
*   **API Gateway / Router (FastAPI):** The entry point for all frontend requests. Routes HTTP requests to the appropriate internal services, handles cross-origin resource sharing (CORS), and enforces rate limiting.
*   **Authentication Provider:** Manages user identity, password hashing, and issues JSON Web Tokens (JWT) for secure session management.
*   **Prediction Engine (ML Component):** Houses the loaded machine learning model and inference logic. Accepts cleaned user parameters and returns admission probability scores.
*   **Recommendation Engine:** Analyzes the prediction outputs alongside historical data to categorize and rank colleges into "Safe," "Moderate," and "Ambitious" buckets.
*   **Data Access Layer (ORM):** Manages all interactions with the PostgreSQL database, translating Python objects into SQL queries and abstracting database specifics.
*   **Analytics & Monitoring Logger:** Captures system events, API performance metrics, and application errors for observability.

---

## 4. Application Layers

The backend application will be structured into the following distinct layers to enforce Separation of Concerns:

*   **Presentation / API Layer:** Responsible for receiving HTTP requests, parsing parameters, validating incoming JSON payloads against schemas, and returning formatted HTTP responses. It knows *nothing* about business rules.
*   **Service Layer (Application Logic):** Coordinates tasks. It receives validated data from the API layer, requests data from the Data layer, passes data to the ML layer for processing, and applies overarching application logic (e.g., checking if a user has exceeded prediction limits).
*   **Business / Domain Layer:** Contains the core rules of the admission domain. For example, the logic that dictates how home-state quota differs from other-state quota belongs here.
*   **Machine Learning Layer:** Dedicated purely to feature transformation and model inference. It takes raw domain data, converts it into the format expected by the ML model, and returns the statistical prediction.
*   **Data / Repository Layer:** The *only* layer allowed to communicate with the database. It provides an interface (e.g., `get_college_by_id`) so the Service layer doesn't need to write SQL.
*   **Infrastructure Layer:** Handles external concerns like email sending (if implemented), third-party logging services, or cloud storage interactions.

---

## 5. Module Breakdown

The software will be divided into the following cohesive modules:

*   **Auth Module:** Manages user registration, login, token generation, token verification, and password recovery.
*   **Colleges & Data Module:** Manages the retrieval, filtering, and searching of historical cutoffs, college details, and branch information.
*   **Prediction Module:** Encapsulates the ML inference pipeline. Translates user rank and category into a probability percentage for specific colleges.
*   **Recommendation Module:** Evaluates the user's profile against the entire dataset to generate the Safe/Moderate/Ambitious lists based on the Prediction Module's outputs.
*   **User Profile Module:** Manages saving and retrieving user preferences, demographic data, and historical prediction results.
*   **Admin / ETL Module:** Responsible for ingesting new raw CSV/PDF data, cleaning it, validating it, and updating the master database without downtime.
*   **Core / Shared Module:** Contains global configurations, custom exception definitions, logging setup, and database connection management.

---

## 6. Data Flow

**Scenario: User requests an admission prediction.**

1.  **User Input:** The user enters their JEE Rank, Category, and preferred branches into the Frontend UI.
2.  **Frontend Dispatch:** The React application validates the input locally (e.g., rank must be > 0), packages it into a JSON payload, and sends an authenticated HTTP POST request to the Backend.
3.  **API Layer Validation:** FastAPI receives the request. Pydantic schemas validate the data types and constraints. If invalid, a 422 HTTP error is returned immediately.
4.  **Service Layer Orchestration:** The Prediction Service receives the validated data. It requests relevant historical data (e.g., last year's cutoffs for the user's category) from the Repository Layer.
5.  **Data Retrieval:** The Repository Layer queries the PostgreSQL database and returns the historical context to the Service Layer.
6.  **ML Inference:** The Service Layer passes the user input and historical context to the ML Layer. The model evaluates the features and returns a probability score (e.g., 85%).
7.  **Response Formatting:** The Service Layer structures the response (Probability, Confidence Level, Disclaimers) and passes it back to the API Layer.
8.  **Client Rendering:** The API Layer sends a 200 OK JSON response. The Frontend parses this JSON and dynamically updates the UI to display the result using charts and badges.

---

## 7. Technology Justification

*   **Backend - Python & FastAPI:** Python is the undisputed industry standard for Data Science and ML integration. FastAPI is chosen over Django/Flask because it offers native asynchronous support (high performance), automatic OpenAPI documentation, and strict type-hinting via Pydantic, which drastically reduces runtime bugs.
*   **Machine Learning - Scikit-learn:** For tabular, historical cutoff data, classical ML algorithms (like Random Forests or Gradient Boosting) provided by Scikit-learn are highly efficient, interpretable, and lightweight compared to deep learning frameworks (TensorFlow/PyTorch), aligning perfectly with deployment constraints.
*   **Database - PostgreSQL:** A robust, open-source relational database. Historical counselling data is highly structured and relational (Colleges have Branches, Branches have Categories, Categories have Cutoffs). NoSQL (like MongoDB) is inappropriate here because maintaining data integrity and complex joins is critical.
*   **Frontend - React & TypeScript:** React offers unparalleled component reusability. TypeScript is mandated because strict typing prevents entire classes of frontend bugs and aligns with the robust backend API typing, creating a safer end-to-end data pipeline.
*   **Styling - Tailwind CSS:** A utility-first CSS framework that allows for rapid UI development without context switching, ensuring a consistent and professional design system.
*   **Deployment - Render (Backend/DB) & Vercel (Frontend):** PaaS (Platform as a Service) providers allow the team to focus on code rather than Linux server configuration. They offer excellent free/hobby tiers suitable for an internship project with automated CI/CD directly from GitHub.

---

## 8. Communication Design

*   **Protocol:** All client-server communication will occur over HTTP/1.1 (and HTTP/2 where supported by infrastructure), exclusively encrypted via TLS (HTTPS).
*   **Style:** RESTful architecture. URLs will represent resources (e.g., `GET /api/v1/colleges`, `POST /api/v1/predictions`).
*   **Data Format:** JSON (JavaScript Object Notation) for both request payloads and response bodies.
*   **Authentication:** Stateless JSON Web Tokens (JWT) transmitted via the `Authorization: Bearer <token>` HTTP header.
*   **Standardized Responses:** Every API response will follow a consistent envelope structure to simplify frontend parsing, differentiating cleanly between data payloads and error metadata.

---

## 9. Scalability Strategy

While this is a training project, it is architected for production scale:
*   **Stateless Backend:** Because no session data is stored in the API server's memory (thanks to JWT), the backend can be horizontally scaled (multiple instances behind a load balancer) seamlessly during high-traffic counselling periods.
*   **Database Indexing:** The database schema will include B-Tree indexes on frequently queried columns (e.g., `college_id`, `category`, `round_number`) to ensure query times remain low even as the dataset grows across years.
*   **Asynchronous I/O:** FastAPI's async capabilities allow the server to handle thousands of concurrent connections efficiently, especially while waiting for database queries to resolve.

---

## 10. Security Architecture

*   **Authentication:** JWT-based auth with explicit expiration times.
*   **Authorization:** Role-Based Access Control (RBAC). A simple `is_admin` flag in the token payload dictates whether a user can access endpoints like `/api/v1/admin/upload-data`.
*   **Input Validation:** Strict server-side validation using Pydantic. Malformed payloads are rejected before they touch business logic or database queries.
*   **SQL Injection Prevention:** Utilization of an Object-Relational Mapper (ORM - SQLAlchemy). Raw SQL string concatenation is strictly forbidden.
*   **Cross-Site Scripting (XSS) Prevention:** React inherently escapes dynamic content before rendering, mitigating standard XSS attacks.
*   **Secrets Management:** API keys, database credentials, and JWT secret keys will be stored in `.env` files locally and secure environment variables in production. They will *never* be committed to version control.
*   **CORS (Cross-Origin Resource Sharing):** The backend will explicitly restrict API access only to the recognized frontend domain.

---

## 11. Logging Strategy

*   **What to Log:**
    *   Application startup and shutdown events.
    *   Database connection successes and failures.
    *   All warnings and errors (with stack traces for 5xx errors).
    *   Security events (e.g., failed login attempts, unauthorized access attempts).
    *   Performance metrics (e.g., queries taking longer than 500ms).
*   **What NEVER to Log:**
    *   Passwords (plaintext or hashed).
    *   JWTs or Session Tokens.
    *   Personally Identifiable Information (PII) beyond user IDs.
    *   Specific user ranks combined with identifying data.
*   **Format:** Structured JSON logging is recommended over plaintext strings. This allows log aggregation tools to easily search and filter logs by severity or module.

---

## 12. Error Handling Strategy

*   **Global Exception Handler:** The API will implement a global exception handler. If an unhandled error occurs anywhere in the code, it is caught here, logged securely, and a sanitized, generic `500 Internal Server Error` is returned to the user, ensuring stack traces are never leaked to the client.
*   **Domain Exceptions:** Custom Python exceptions (e.g., `CollegeNotFoundError`, `InvalidRankError`) will be raised by the business layer and mapped to appropriate HTTP status codes (e.g., 404, 400) by the API layer.
*   **Validation Errors:** Pydantic validation errors will automatically return a `422 Unprocessable Entity` response, detailing exactly which fields failed and why, providing excellent Developer Experience (DX) for the frontend team.

---

## 13. Performance Strategy

*   **Pagination:** Endpoints returning lists (e.g., college search results) will enforce offset/limit pagination to prevent massive database reads and network payload bloat.
*   **Model Loading:** The ML model (`.pkl` or `.joblib` file) will be loaded into application memory *once* during application startup, not per-request, ensuring inference latency is minimized.
*   **Caching (Future-proofing):** The architecture allows for HTTP cache-control headers on static endpoints (like lists of states or branches). Highly queried, static historical data can be cached at the service layer in the future without changing the API contract.
*   **Lazy Loading:** The React frontend will utilize code splitting and lazy loading for routes (e.g., the Admin dashboard code is only downloaded by the browser if a user navigates to it).

---

## 14. Project Folder Philosophy

**Philosophy:** Feature-Based / Domain-Driven Organization

Rather than grouping files by their technical type (e.g., a folder for all `controllers`, a folder for all `models`), the project should group files by their **Domain Concept**.

*   **Why?** If a developer needs to fix a bug in the "Prediction" feature, they shouldn't have to open files across five different unrelated directories. All routing, logic, and schemas related to predictions should live in a `predictions/` module.
*   **Structure Blueprint:**
    *   `api/` (API layer, endpoints)
    *   `core/` (Security, Config, DB connection)
    *   `domain/` (Business models and interfaces)
    *   `services/` (Business logic implementations)
    *   `ml/` (Model loading, feature engineering pipelines)
    *   `data/` (Repositories, DB models, migrations)
*   This approach heavily favors maintainability, readability, and scale.

---

## 15. Dependency Strategy

*   **Python (Backend/ML):** Dependencies will be managed using `requirements.txt` (or a modern equivalent like `poetry` / `pipenv`). Dependencies must be pinned to specific versions (e.g., `fastapi==0.100.0`) to guarantee reproducible builds across dev, staging, and production environments.
*   **Node.js (Frontend):** Dependencies will be managed via `package.json` and `npm` or `yarn`. A lockfile (`package-lock.json`) must be committed to version control.
*   **Separation:** ML training dependencies (like Jupyter, matplotlib) should be separated from API serving dependencies. The production API server should not download plotting libraries.

---

## 16. Future Expansion

The architecture is explicitly designed to absorb future requirements gracefully:
*   **Multiple Counselling Systems:** The database schema will decouple cutoffs from a hardcoded JoSAA structure, allowing the addition of MHT-CET or TNEA data via a simple `counselling_authority` identifier.
*   **Multiple ML Models:** The ML Layer will define a standard `Predictor` interface. Swapping the Random Forest model for a Neural Network later requires only changing the implementation behind the interface, without touching the API.
*   **AI Chatbot:** The modular backend allows a new `/api/v1/chatbot` router to be added, leveraging the existing data repositories without interfering with the prediction flow.

---

## 17. Development Standards

To maintain professional rigor and portfolio quality, the team will adhere to:
*   **Naming Conventions:** `snake_case` for Python variables/functions, `PascalCase` for Python Classes and React Components, `camelCase` for TypeScript variables/functions.
*   **Git Workflow:** Feature Branching model. `main` is stable. All development happens on branches (`feat/auth`, `fix/prediction-bug`) and is merged via Pull Requests.
*   **Commit Conventions:** Adoption of Conventional Commits (e.g., `feat: add college recommendation engine`, `docs: update API schema`) to generate clean, readable project histories.
*   **Documentation:** All public API endpoints must have descriptions and parameter definitions in the FastAPI Swagger UI. Complex algorithmic logic in the ML or Recommendation engines must include inline comments explaining *why*, not just *what*.

---

## 18. Architect Recommendations

As the Lead Software Architect, I provide the following mandates to ensure this project acts as an elite internship portfolio piece:

1.  **Prioritize Clean Interfaces over Fast Hacks:** If you find yourself writing raw SQL inside a FastAPI router, stop. Move it to the repository layer. The goal is to demonstrate software engineering maturity, not just to get the code working.
2.  **Make the ML Pipeline Reproducible:** Do not train the model in a messy Jupyter notebook and magically produce a `.pkl` file. Write a clean Python script (`train.py`) that anyone can run to process the data and output the exact same model.
3.  **Invest heavily in the OpenAPI Docs:** Recruiters and evaluators will judge the backend by its API documentation. FastAPI generates this automatically, but you must enrich it with descriptions, example payloads, and clear response schemas.
4.  **Embrace TypeScript Strictness:** Do not use `any` in the frontend code. Define precise interfaces for all data objects. This demonstrates to employers that you understand professional frontend development.
5.  **Focus on the "Empty States" and "Error States":** A professional application handles failure gracefully. If the database is empty, or a search returns no colleges, the UI should guide the user, not show a blank screen or a raw error string.

---

**Phase 2 completed successfully. Awaiting Phase 3: Project Structure & Development Environment.**
