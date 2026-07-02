# Software Requirements Specification (SRS)

## Chances of Admission (India)

---

| Document Attribute | Detail |
|---|---|
| **Project Name** | Chances of Admission (India) |
| **Document Version** | 1.0 |
| **Document Status** | Draft — Awaiting Stakeholder Review |
| **Category** | Industrial Training Project |
| **Course** | Python Programming for AI & Data Science |
| **Document Type** | Software Requirements Specification (SRS) |
| **Prepared By** | Software Architecture Team |
| **Date** | July 2026 |
| **Phase** | Phase 1 — Project Planning |

---

## Table of Contents

1. Executive Summary
2. Project Vision
3. Problem Statement
4. Business Objectives
5. Project Goals
6. Target Audience
7. Stakeholders
8. Project Scope
9. Functional Requirements
10. Non-Functional Requirements
11. Constraints
12. Assumptions
13. Risks
14. Success Criteria
15. Development Methodology
16. Milestone Roadmap
17. Questions That Must Be Answered Before Development
18. Final Recommendations

---

## 1. Executive Summary

**Chances of Admission (India)** is an AI-powered web application designed to assist Indian engineering aspirants in making informed, data-driven decisions during the college admission process. The system leverages machine learning trained on multi-year historical counselling data to estimate the probability of a student securing admission to a specific college and branch, based on their rank, category, and quota.

The Indian engineering admission process — governed by bodies such as the Joint Seat Allocation Authority (JoSAA), MHT-CET, TNEA, KCET, and others — is opaque, high-stakes, and time-pressured. Students currently rely on informal peer networks, paid consultants, or intuition to make life-defining choices in a matter of hours during counselling rounds. This application exists to replace guesswork with analytical intelligence.

Beyond prediction, the system is designed to evolve into a complete **Admission Decision Support System (ADSS)** — incorporating college and branch recommendations, historical trend visualisations, personalised dashboards, and an analytics layer that benefits students, parents, school counsellors, and guidance organisations.

This SRS defines the requirements, boundaries, constraints, risks, and strategic direction for the project. It is the primary reference document for all subsequent technical and design decisions. No implementation has begun; this document governs what will be built and why, before a single line of code is written.

---

## 2. Project Vision

> **To become the most trusted, transparent, and accessible AI-powered admission guidance platform for Indian engineering aspirants — empowering every student, regardless of socioeconomic background, to make their best possible college choice with confidence and data.**

### Vision Elaboration

The vision has three pillars:

**Trust** — Predictions must be explainable. Students should understand why a result was produced, not simply receive a probability score. The system should never overstate its confidence.

**Transparency** — The underlying data (historical cutoffs, seat matrices) must be visible to users. The system earns credibility by showing its work, not hiding behind a black box.

**Accessibility** — The application must work on low-end Android devices over 4G connections, be available in English (and potentially regional languages in future phases), and remain free for core features, ensuring no student is disadvantaged by economic barriers.

### Long-Term Vision

Over successive development phases, this platform should evolve from a prediction tool into a **comprehensive decision-support ecosystem** that integrates counselling strategy, branch exploration, career pathway information, and peer benchmarking — making it indispensable during the annual admission season.

---

## 3. Problem Statement

### 3.1 The Context

Every year, approximately **1.2 million students** appear for JEE Main in India. Of these, roughly 50,000 qualify for JEE Advanced (IIT counselling), while the remainder compete for seats in NITs, IIITs, GFTIs, and state-level institutions through parallel counselling systems. Students have typically 48–72 hours per counselling round to submit their choice lists — often comprising hundreds of college-branch-category combinations.

### 3.2 The Core Problem

Despite this being one of the most consequential decisions of a young person's life, the decision-making process is severely handicapped by:

**Information Asymmetry** — Historical cutoff data exists but is scattered across year-specific PDFs, unofficial portals, and paywalled coaching resources. There is no single, structured, machine-readable repository of multi-year cutoff trends.

**Complexity of Variables** — Cutoffs are not simple thresholds. They vary by college, branch, category (General, OBC-NCL, SC, ST, EWS), sub-category (PWD, Defence, Kashmiri Migrants), quota (home state vs. other state), and counselling round (Round 1 through Round 6). A student must simultaneously evaluate hundreds of permutations.

**Time Pressure** — Counselling rounds operate on strict deadlines. Students do not have the luxury of extended analysis.

**Guidance Gap** — Access to quality counselling is unevenly distributed. Students from tier-2/tier-3 cities and rural backgrounds, who cannot afford private counsellors or coaching institutes with dedicated counselling support, are disproportionately disadvantaged.

**Emotional Decision-Making** — Without objective data, students default to brand recognition, peer pressure, or parental preference — often choosing suboptimally between a "safe" lower-ranked college and a realistic "reach" college they could have obtained.

### 3.3 The Consequence of Inaction

Students who make suboptimal choices during counselling either:
- Accept a college/branch they did not want, impacting academic motivation and career trajectory.
- Participate in upgrade rounds without a clear strategy, risking their already-secured seat.
- Drop a year to reappear, losing 12 months of productive time.

### 3.4 The Solution Space

A well-designed data-driven platform that consolidates historical cutoff data, applies machine learning to detect trends, and presents probability-based recommendations can dramatically reduce decision uncertainty — even if it cannot eliminate it entirely. The value is not in predicting the future with certainty, but in providing a structured, evidence-based framework that replaces guesswork.

---

## 4. Business Objectives

| ID | Objective | Priority |
|----|-----------|----------|
| BO-01 | Demonstrate practical application of Python, Data Science, and ML in a socially relevant domain | High |
| BO-02 | Build a production-ready portfolio artifact that reflects senior engineering practices | High |
| BO-03 | Deliver a functional MVP that can be demonstrated, hosted, and evaluated by faculty and industry professionals | High |
| BO-04 | Design a system that is genuinely useful to real Indian students, not a toy demo | High |
| BO-05 | Establish an architecture that supports future commercial expansion without requiring a rewrite | Medium |
| BO-06 | Demonstrate proficiency in the full software development lifecycle — from requirements to deployment | High |
| BO-07 | Produce documentation of sufficient quality to be included in a professional engineering portfolio | Medium |

---

## 5. Project Goals

### 5.1 Primary Goals

- **G-01** — Build a working ML-powered prediction engine that estimates admission probability for JoSAA counselling based on historical cutoff data.
- **G-02** — Develop a production-grade REST API using FastAPI that serves predictions and data to the frontend.
- **G-03** — Create a responsive, accessible, and visually professional frontend using React, TypeScript, and Tailwind CSS.
- **G-04** — Design and implement a normalised PostgreSQL database that stores multi-year historical counselling data at scale.
- **G-05** — Deploy the full-stack application to a publicly accessible URL using Vercel (frontend) and Render (backend).

### 5.2 Secondary Goals

- **G-06** — Implement user authentication so students can save their profiles and prediction history.
- **G-07** — Build a college and branch recommendation engine that classifies options into Safe, Moderate, and Ambitious tiers.
- **G-08** — Provide a historical cutoff trend visualisation feature for any college-branch-category combination.
- **G-09** — Develop an admin interface for dataset management and system monitoring.

### 5.3 Educational Goals

- **G-10** — Demonstrate the supervised ML lifecycle: data collection → cleaning → feature engineering → training → evaluation → serialisation → serving.
- **G-11** — Apply professional software engineering practices: version control, structured logging, error handling, testing, and documentation.

---

## 6. Target Audience

### 6.1 Primary Users — Students

**Profile:** Indian engineering aspirants aged 17–20 who have appeared for JEE Main and/or JEE Advanced and are preparing for or actively participating in counselling.

**Technical Literacy:** Variable. Many will access the application on mobile devices. The interface must require zero technical knowledge to use.

**Emotional Context:** High stress. Low time availability. Seeking reassurance and clarity. Any friction in the user experience will cause abandonment.

**Core Need:** "Given my rank and category, which colleges can I realistically get? What are my actual chances?"

**Secondary Need:** "What has the trend been for this college over the last 5 years? Is it getting more competitive or less?"

### 6.2 Secondary Users — Parents

**Profile:** Parents of students, aged 40–55, often less technically literate than their children. May use the application independently or alongside their child.

**Core Need:** Validation. They want confidence that the recommendations are credible and that their child is not missing a college they could have obtained.

**Design Implication:** The application must present data clearly and authoritatively, without technical jargon.

### 6.3 Future Users — Counsellors and Guidance Organisations

**Profile:** School counsellors, career guidance NGOs, and coaching institutes that advise large groups of students.

**Core Need:** Bulk analysis capabilities, exportable reports, and the ability to model scenarios for multiple student profiles.

**Design Implication:** The architecture must support future API access, bulk processing, and role-based access without requiring a rewrite.

---

## 7. Stakeholders

| Stakeholder | Role | Interest | Influence |
|-------------|------|----------|-----------|
| **Students (End Users)** | Primary consumers of prediction and recommendation features | Accurate, fast, and easy-to-use admission guidance | High (adoption drives value) |
| **Parents** | Secondary consumers; may influence student's platform use | Trustworthy, credible predictions | Medium |
| **Internship Supervisors / Faculty** | Evaluators of the project for academic and training purposes | Code quality, documentation, architecture, and ML outcomes | High (direct evaluation authority) |
| **Developer / Engineer Team** | Architects and builders of the system | Clean, maintainable codebase; demonstration of skills | High |
| **Future Investors / Stakeholders** | Potential commercial sponsors (post-training) | Scalability, market potential, production readiness | Low (current phase) |
| **Data Providers** | JoSAA, NIC (National Informatics Centre), state counselling bodies | Accurate representation of their published data | Medium (data availability dependency) |

---

## 8. Project Scope

### 8.1 In Scope (Version 1.0)

- **Data Pipeline** — Collection, cleaning, normalisation, and storage of historical JoSAA counselling data (minimum 5 years).
- **ML Prediction Engine** — A trained model that accepts student rank, category, and college-branch as inputs and outputs an admission probability score.
- **College Recommendation** — A ranked list of options categorised as Safe, Moderate, and Ambitious.
- **Historical Cutoff Viewer** — Year-over-year cutoff trend visualisation for any valid college-branch-category combination.
- **Student Profile and Authentication** — Registration, login, and persistent storage of student profiles and saved predictions.
- **REST API** — A versioned, documented FastAPI backend serving all data and ML inferences.
- **Frontend Application** — A fully responsive React + TypeScript + Tailwind CSS web application.
- **Admin Panel** — Basic interface for uploading new yearly datasets and monitoring data integrity.
- **Deployment** — Live, publicly accessible deployment on Vercel and Render.
- **Documentation** — API documentation (OpenAPI), user guide, and developer documentation.

### 8.2 Out of Scope (Version 1.0)

- State-level counselling data (MHT-CET, TNEA, KCET, WBJEE, etc.) — JoSAA only in v1.
- JEE Advanced / IIT predictions — JEE Main / NIT-IIIT-GFTI counselling only in v1.
- Mobile native applications (iOS / Android).
- Multi-language support (regional languages).
- Integration with official JoSAA or NIC systems.
- Real-time seat availability during live counselling rounds.
- Peer comparison or social features.
- Payment processing or subscription tiers.
- Bulk API access for institutional users.
- Automated retraining pipeline triggered by new data ingestion.

### 8.3 Future Scope (Post v1.0)

- State-level counselling integration (MHT-CET, TNEA, KCET, WBJEE, etc.)
- IIT / JEE Advanced prediction module
- Mobile application (React Native or Flutter)
- Regional language localisation
- Counselling strategy simulation
- Career path integration (placement data, graduate outcomes)
- Institutional API for counsellors and schools
- Automated ML model retraining pipeline
- Explainable AI (XAI) layer for prediction transparency

> [!IMPORTANT]
> Even though future-scope features are excluded from v1, the database schema, API design, and frontend architecture must be designed with extensibility in mind. Future features must require only additive development — not architectural rewrites.

---

## 9. Functional Requirements

> These are high-level functional requirements. They describe **what** the system must do, not **how** it will do it. Implementation details are deferred to the System Architecture phase.

### FR-01: Student Profile Management
The system shall allow users to create and manage a profile containing their JEE Main rank, category (General/OBC-NCL/SC/ST/EWS), sub-category (if applicable), home state, and branch preferences.

### FR-02: Admission Probability Prediction
Given a student's rank, category, and a specific college-branch combination, the system shall compute and return the estimated probability of admission as a numerical percentage, accompanied by a confidence qualifier.

### FR-03: College Recommendation Engine
The system shall generate a personalised, ranked list of college-branch recommendations segmented into three tiers: **Safe** (high probability), **Moderate** (medium probability), and **Ambitious** (low but non-zero probability), based on the student's complete profile.

### FR-04: Branch Recommendation
The system shall allow filtering and ranking recommendations by branch preference, enabling a student to identify the best colleges for a specific branch of engineering.

### FR-05: Historical Cutoff Analysis
The system shall display multi-year historical opening rank and closing rank data for any valid college-branch-category combination, enabling users to assess trend direction (tightening or loosening cutoffs).

### FR-06: Search and Filter
The system shall provide robust search and filtering capabilities for colleges by name, state, institute type (NIT / IIIT / GFTI), branch, category, and quota.

### FR-07: User Authentication and Authorisation
The system shall support secure user registration and login. Authenticated users shall have access to saved predictions, personalised dashboards, and profile management. The system shall enforce role-based access (Student, Admin).

### FR-08: Prediction History
The system shall allow authenticated users to view, name, and revisit their previous prediction queries and results.

### FR-09: Analytics Dashboard (Student)
The system shall provide a student-facing dashboard summarising: recent searches, top recommended colleges, cutoff trend summaries, and saved shortlists.

### FR-10: Admin — Dataset Management
The system shall provide an authenticated admin interface enabling authorised personnel to upload new yearly counselling datasets, validate data integrity before ingestion, and review ingestion logs.

### FR-11: Admin — System Monitoring
The system shall expose a basic admin view of system health indicators: API uptime, prediction request volumes, error rates, and dataset currency.

### FR-12: Responsive and Accessible UI
The system's frontend shall render correctly and be fully usable across devices from a 320px mobile viewport to a 1920px desktop monitor, with no loss of core functionality.

### FR-13: Dark Mode
The system shall support a user-toggleable dark mode that persists across sessions.

### FR-14: Public API (Read-Only)
The system shall expose a read-only subset of its API (college listings, cutoff data) without requiring authentication, enabling future integration and easy demonstration.

---

## 10. Non-Functional Requirements

### 10.1 Performance

- **NFR-P01** — API endpoints serving prediction results shall respond in under **500 milliseconds** at the 95th percentile under normal load.
- **NFR-P02** — Frontend pages shall achieve a Largest Contentful Paint (LCP) of under **2.5 seconds** on a standard 4G mobile connection.
- **NFR-P03** — ML model inference shall complete within **200 milliseconds** as a contribution to the total API response budget.
- **NFR-P04** — Database queries for historical cutoff data shall execute within **100 milliseconds** via appropriate indexing.

*Rationale: Students use this application under time pressure during counselling rounds. Any perceptible lag degrades trust and increases anxiety.*

### 10.2 Scalability

- **NFR-S01** — The backend shall be stateless, enabling horizontal scaling without session persistence complications.
- **NFR-S02** — The database schema shall accommodate 10× growth in data volume without structural changes.
- **NFR-S03** — The ML prediction layer shall be isolated as an independent service boundary, enabling future extraction into a dedicated microservice.

*Rationale: Counselling season creates highly concentrated usage spikes (typically June–July and December–January). The system must handle surge traffic without degradation.*

### 10.3 Reliability

- **NFR-R01** — The system shall target **99.5% uptime** during peak counselling periods (June–July).
- **NFR-R02** — All API endpoints shall implement graceful degradation — if the ML service fails, the system shall return historical cutoff data with appropriate messaging rather than a generic error.
- **NFR-R03** — The system shall implement idempotent prediction requests, ensuring repeated identical requests return consistent results.
- **NFR-R04** — Database transactions involving data ingestion shall be atomic — partial failures must not corrupt existing data.

### 10.4 Security

- **NFR-SEC01** — All client-server communication shall occur exclusively over HTTPS/TLS.
- **NFR-SEC02** — User passwords shall be hashed using a modern, adaptive hashing algorithm (e.g., bcrypt or Argon2). Plaintext passwords shall never be stored or logged.
- **NFR-SEC03** — Authentication tokens shall be short-lived JWTs with refresh token rotation. Tokens shall be invalidated on logout.
- **NFR-SEC04** — All user inputs shall be validated and sanitised on the server side. Client-side validation is supplementary, never authoritative.
- **NFR-SEC05** — The API shall implement rate limiting to prevent abuse and brute-force attacks.
- **NFR-SEC06** — The system shall not log personally identifiable information (PII) in application logs.
- **NFR-SEC07** — SQL queries shall be parameterised exclusively. Raw string interpolation into SQL is prohibited.
- **NFR-SEC08** — The system shall comply with the principles of India's Digital Personal Data Protection (DPDP) Act, 2023 — minimal data collection, explicit consent, and right to erasure.

*Rationale: A student's rank and category is sensitive personal information. A breach could cause significant reputational harm to both the student and the platform.*

### 10.5 Usability

- **NFR-U01** — A new user shall receive their first admission probability estimate within **3 user interactions** from landing, without creating an account.
- **NFR-U02** — Error states, loading states, and empty states shall be explicitly handled and communicated with clear, non-technical, actionable messaging.
- **NFR-U03** — The application shall never present raw probability scores without contextual framing (e.g., "High chance", "Moderate chance").
- **NFR-U04** — Form validation messages shall appear inline, immediately adjacent to the field in error, without page reload.

### 10.6 Maintainability

- **NFR-M01** — All backend services, functions, and API endpoints shall include docstrings and inline documentation.
- **NFR-M02** — The backend shall achieve a minimum of **80% test coverage** on the service layer and ML inference layer.
- **NFR-M03** — The codebase shall enforce consistent code style via automated linting and formatting tools.
- **NFR-M04** — Database schema changes shall be managed exclusively via versioned migration scripts. Direct schema modification in production is prohibited.
- **NFR-M05** — All configuration (database URLs, secret keys, model paths) shall be externalised via environment variables. No secrets shall appear in source code or version control.

### 10.7 Availability

- **NFR-A01** — The system shall implement a `/health` endpoint returning system status, database connectivity, and model availability — enabling automated uptime monitoring.
- **NFR-A02** — Scheduled dataset updates shall be performed without system downtime.

### 10.8 Accessibility

- **NFR-ACC01** — The frontend shall conform to **WCAG 2.1 Level AA** accessibility standards.
- **NFR-ACC02** — All interactive elements shall be keyboard navigable with visible focus indicators.
- **NFR-ACC03** — All meaningful images and charts shall include appropriate alternative text descriptions.
- **NFR-ACC04** — Colour shall not be the sole means of conveying information (probability tier colour must be accompanied by a text label).

*Rationale: First-generation college students, who may rely on assistive technologies, are among the most important users this platform can serve.*

### 10.9 Portability

- **NFR-PORT01** — The backend application shall run identically in any POSIX-compliant environment and in containerised form, avoiding OS-specific dependencies.
- **NFR-PORT02** — The frontend shall be deployable to any static hosting provider, not coupled to any specific CDN or hosting service.
- **NFR-PORT03** — The database shall use standard PostgreSQL-compliant SQL, avoiding vendor-specific extensions that would create provider lock-in.

### 10.10 Compatibility

- **NFR-COMPAT01** — The frontend shall function correctly on the two most recent stable versions of Chrome, Firefox, Safari, and Edge.
- **NFR-COMPAT02** — The API shall be versioned (e.g., `/api/v1/`) from inception, enabling future breaking changes under a new version without disrupting existing consumers.
- **NFR-COMPAT03** — The ML model shall be serialised in a format that is version-pinned, ensuring model reproducibility independent of library updates.

---

## 11. Constraints

### 11.1 Technical Constraints

- **TC-01** — The technology stack is fixed: FastAPI (backend), React + TypeScript + Tailwind CSS + Vite (frontend), PostgreSQL (database), Scikit-learn (ML), Render + Vercel (deployment). Deviations require documented justification and stakeholder approval.
- **TC-02** — The ML model must be trainable on commodity hardware without requiring GPU compute. Model architecture choices must reflect this constraint.
- **TC-03** — The system must be deployable on Render's free or starter tier, which imposes memory limits (~512 MB RAM) and introduces cold-start latency (~30 seconds). The architecture must account for this.
- **TC-04** — The frontend must be deployable on Vercel's free tier, which limits serverless function execution time and request volume.
- **TC-05** — The PostgreSQL instance will be hosted on a cloud service. Connection pooling must be implemented to work within connection count limits on free tiers.

### 11.2 Time Constraints

- **TC-06** — This is an industrial training project with an implicit deadline tied to the training programme duration. Development phases must be sequenced to ensure a demonstrable MVP is available before the submission deadline.
- **TC-07** — Counselling season data (new yearly JoSAA results) becomes available annually in July. If the project spans this window, plans for integrating newly released data must be considered.

### 11.3 Data Constraints

- **TC-08** — Historical JoSAA data is published as PDF documents and unofficial data portals. There is no official machine-readable API. Data collection requires parsing, normalisation, and validation — this is a significant effort and a primary project risk.
- **TC-09** — Data collection is limited to publicly available historical data. No proprietary or paywalled datasets will be used.
- **TC-10** — The ML model will be trained exclusively on JoSAA data in v1. Predictions are valid only for NIT/IIIT/GFTI counselling and must be clearly labelled as such.
- **TC-11** — Historical data availability may be inconsistent across years (different formats, missing rounds, renamed institutes). The ETL pipeline must handle these inconsistencies gracefully.

### 11.4 Project Constraints

- **TC-12** — This project is developed within an educational/internship context. Architecture must reflect a small team — avoid over-engineering that creates an unsustainable maintenance burden.
- **TC-13** — There is no dedicated QA team. Testing must be designed as part of the development workflow, not a separate phase requiring specialist resources.
- **TC-14** — There is no budget for paid cloud services, licensed datasets, or commercial tooling. The entire stack must be viable on free tiers and open-source tools.

---

## 12. Assumptions

> Every assumption listed here must be revisited before Phase 2 begins. If any assumption proves incorrect, its downstream requirements must be re-evaluated.

| ID | Assumption | Impact if Incorrect |
|----|------------|---------------------|
| A-01 | Historical JoSAA cutoff data for at least 5 years (2019–2024) is publicly available and collectible without legal restriction | Fundamental threat to the project's data foundation |
| A-02 | The data, once collected, can be normalised into a consistent schema despite format variations across years | Significant ETL development effort increase |
| A-03 | JoSAA Round-wise data (opening rank/closing rank per round) is the primary and sufficient signal for ML prediction | Model accuracy may be lower if additional signals are needed |
| A-04 | The project focuses exclusively on JEE Main rank for NITs, IIITs, and GFTIs — not JEE Advanced for IITs | Scope change required if IIT counselling is included |
| A-05 | Users will self-declare their category and quota — no document verification is required | Prediction accuracy depends entirely on user honesty |
| A-06 | A classical ML approach (regression, gradient boosting) will achieve sufficient predictive accuracy without deep learning | Training infrastructure assumption changes if classical ML proves insufficient |
| A-07 | The ML model will be trained offline and served as a serialised artefact. Online/incremental learning is not required in v1 | Retraining workflow complexity increases if incremental learning is needed |
| A-08 | PostgreSQL hosted on a free cloud tier is sufficient for the data volume and query patterns of v1 | May require a paid tier if query performance degrades under load |
| A-09 | A single developer (or very small team) will build this project sequentially through defined phases | Parallelisation of frontend and backend work may not be possible |
| A-10 | User authentication will be email-password based in v1. OAuth is a future enhancement | Some users may prefer OAuth and resist email registration |
| A-11 | The frontend will be a Single Page Application (SPA). Server-Side Rendering (SSR) is not required for v1 | SEO considerations may require SSR if organic search traffic is a priority |
| A-12 | The application will be accessed primarily via web browser. Native app development is not in scope | User acquisition may be limited if a significant portion of target users are app-only |
| A-13 | The internship evaluation criteria prioritise code quality, architecture, and documentation over feature completeness | If feature count is the primary evaluation metric, scope priorities must be adjusted |
| A-14 | The Render free tier's cold-start latency is acceptable during the project demonstration phase | A keep-alive mechanism or paid tier may be needed for a smooth demonstration |
| A-15 | No real-time data integration with JoSAA systems is required or legally permitted | If real-time data becomes available, significant architectural changes would be needed |

---

## 13. Risks

### Risk Register

| ID | Risk | Category | Probability | Impact | Severity |
|----|------|----------|-------------|--------|----------|
| R-01 | Historical data is incomplete, inconsistent, or in formats that are prohibitively difficult to parse | Dataset Quality | High | High | **Critical** |
| R-02 | ML model achieves insufficient accuracy due to small dataset, high variance in cutoffs, or missing features | ML Limitations | Medium | High | **High** |
| R-03 | Render free tier cold-start makes the live demo appear broken or unresponsive | Deployment | High | Medium | **High** |
| R-04 | Scope creep driven by adding state counselling data or IIT predictions before the core is stable | Project Management | High | Medium | **High** |
| R-05 | Security vulnerabilities introduced through improper input validation or JWT implementation | Security | Medium | High | **High** |
| R-06 | Database connection pool exhaustion on free-tier PostgreSQL during demonstration | Performance | Medium | Medium | **Medium** |
| R-07 | Students treat ML probability as a guarantee, leading to poor decisions and loss of trust | User Adoption | Low | High | **Medium** |
| R-08 | JoSAA changes its cutoff data format or publication process, breaking the ETL pipeline | Maintenance | Low | High | **Medium** |
| R-09 | The project is difficult to evaluate by faculty unfamiliar with the Indian counselling domain | Stakeholder | Medium | Medium | **Medium** |
| R-10 | Technical debt accumulates from rushed implementation, making the codebase unmaintainable | Maintainability | Medium | Medium | **Medium** |

### Mitigation Strategies

**R-01 — Data Quality**
Treat data collection and cleaning as a formal project phase with explicit acceptance criteria. Build a validation layer that flags anomalies before ingestion. Maintain a canonical registry of college names. Document all data transformation decisions. Begin data collection immediately and fail fast — if clean data cannot be obtained, scope must be adjusted before any ML or backend work begins.

**R-02 — ML Accuracy**
Start with a strong baseline (rule-based threshold comparison: does the student's rank fall between historical opening and closing ranks?). Use this baseline as a benchmark. Apply cross-validation rigorously. Communicate prediction uncertainty through confidence bands, not just point estimates. Never deploy a model whose validation metrics have not been explicitly documented.

**R-03 — Deployment Cold Start**
Implement a keep-alive pinging mechanism (a cron-based HTTP GET to the health endpoint every 14 minutes). Document this limitation in the README. For live demonstrations, warm the server immediately before presenting. Consider Render's starter tier ($7/month) for evaluation periods.

**R-04 — Scope Creep**
Strictly enforce the phased development plan. Any scope change must be evaluated against the current phase's acceptance criteria. The product scope table (Section 8) serves as the contractual boundary for v1.

**R-05 — Security**
Follow OWASP Top 10 mitigation practices from the first line of backend code. Implement input validation at the Pydantic schema layer before any business logic executes. Use well-established libraries for JWT and password hashing rather than custom implementations. Conduct a security review checklist before deployment.

**R-06 — Database Exhaustion**
Implement SQLAlchemy connection pooling with conservative limits tuned to the free-tier maximum. Implement a health check that reports current pool utilisation. Monitor query performance during load testing.

**R-07 — User Misinterpretation**
Design the UX to consistently and prominently display a disclaimer: "This prediction is based on historical trends and is not a guarantee of admission." Use language like "historically, students with similar ranks had a 78% chance" rather than "you have a 78% chance of admission."

**R-08 — ETL Fragility**
Decouple the ETL pipeline from the core application. Store raw source data in an immutable archive before transformation. Build the ETL pipeline to be re-runnable and idempotent. Document the data source format for each year.

**R-09 — Evaluation Gap**
Include a concise "Domain Context" section in the project documentation that explains the Indian counselling system to evaluators unfamiliar with it. Prepare a demonstration script that explains the problem being solved before showing the solution.

**R-10 — Technical Debt**
Enforce code review practices even as a solo developer. Maintain a living TODO list of known shortcuts. Allocate explicit time in the Quality phase for refactoring.

---

## 14. Success Criteria

Success for this project is evaluated across four dimensions: **Technical Quality**, **Product Functionality**, **Educational Demonstration**, and **Portfolio Value**.

### 14.1 Technical Quality — Must Meet All

| Criterion | Measurable Target |
|-----------|------------------|
| ML Model Accuracy | ≥ 85% accuracy on a held-out test set; documented with precision, recall, and F1 metrics |
| API Response Time | P95 latency ≤ 500 ms for prediction endpoints under simulated load |
| Test Coverage | ≥ 80% test coverage on backend service layer and ML inference layer |
| Security | Zero critical vulnerabilities per OWASP Top 10 checklist; all inputs validated; no hardcoded secrets |
| Code Quality | Zero PEP8 violations on automated lint check; all public functions documented |
| Database Integrity | All schema changes managed via Alembic migrations; no direct DDL in production |

### 14.2 Product Functionality — Must Meet All

| Criterion | Measurable Target |
|-----------|------------------|
| Core Prediction Flow | A student receives an admission probability estimate within 3 user interactions, without registration |
| Recommendation Coverage | Covers all JoSAA-listed NITs, IIITs, and GFTIs with at least 5 years of data |
| Category Coverage | All 6 primary categories (GEN, OBC-NCL, SC, ST, EWS, PWD) are correctly handled |
| Historical Data | Minimum 5 years of JoSAA round-wise cutoff data available in the system |
| Cross-Device Usability | Core prediction flow works without horizontal scrolling on a 375px wide mobile viewport |
| Dark Mode | Dark mode toggle persists across page refreshes via localStorage |
| Authentication | User can register, log in, save a prediction, log out, and retrieve it on next login |

### 14.3 Educational Demonstration — Must Meet All

| Criterion | Measurable Target |
|-----------|------------------|
| Full Stack Coverage | Evidence of proficiency in: Python, ML, REST API, React/TypeScript, PostgreSQL, and deployment |
| Documentation Quality | API documented via OpenAPI/Swagger; README adequate for a new developer to run the project locally within 30 minutes |
| Deployment | Application accessible at a public URL; no manual steps required post-CI |
| Version Control | Git history reflects meaningful, atomic commits; no single "initial commit" with all code |

### 14.4 Portfolio Value — Should Meet All

| Criterion | Target |
|-----------|--------|
| Genuine Utility | The application solves a real problem for real users — it is not a toy or demo |
| Professional Appearance | The UI is visually polished, not a default-styled prototype |
| Explainability | The developer can clearly explain every architectural decision made in the project |
| Extensibility | A senior engineer can identify clear extension points for future scope items in the codebase |

---

## 15. Development Methodology

### Recommended Methodology: Phased Iterative Development with Milestone Gates

This project recommends a **lightweight, phased iterative methodology** — a pragmatic adaptation of Agile principles calibrated for a small team working on a time-bounded educational project.

### Rationale for This Choice

**Why not pure Waterfall?**
Waterfall requires complete requirements before development begins. The ML component introduces too much uncertainty in data quality and model performance to commit to a fixed implementation plan at the outset. Waterfall would lead to wasted effort if, for example, data quality proves insufficient for the initially planned model approach.

**Why not pure Agile/Scrum?**
Full Scrum — with sprints, standups, sprint reviews, and retrospectives — is operationally heavy for a solo or very small team. The overhead of Scrum ceremonies is not justified at this scale.

**Why Phased Iterative?**
- Each phase has clear entry criteria (what must be completed before it begins) and exit criteria (what must be demonstrated before moving on).
- Phases are not perfectly sequential — some overlap is expected and acceptable.
- Each phase ends with a demonstrable, reviewable output — preventing the risk of "90% done for months."
- The phased structure maps directly to academic evaluation points, making progress visible to supervisors.

### Working Practices

**Version Control Discipline** — Every feature is developed on a named branch. Commits are atomic and descriptive. The main branch always reflects the last stable, tested state.

**Documentation-as-You-Build** — Documentation is written concurrently with implementation, not as a final step.

**Test-First for Critical Paths** — The ML prediction logic and authentication system shall be developed with tests written before or alongside implementation.

**Review Gates** — Before beginning any new phase, a self-review checklist must confirm that the previous phase's exit criteria are met. No phase begins on an unstable foundation.

**Explicit TODO Management** — Known shortcuts and deferred quality improvements are logged explicitly rather than ignored.

---

## 16. Milestone Roadmap

> Milestones are high-level checkpoints only. They do not prescribe implementation tasks, file structures, or technical decisions. Those are defined in Phase 2.

| Milestone | Name | Key Deliverables | Gate Criteria |
|-----------|------|-----------------|---------------|
| **M0** | Project Foundation | This SRS document; Technology stack confirmation; Repository initialisation | Stakeholder sign-off on SRS |
| **M1** | System Architecture & Technical Design | Database schema design; API contract design; ML model selection rationale; Deployment architecture diagram | Architecture reviewed and approved |
| **M2** | Data Foundation | ETL pipeline; Cleaned and normalised historical dataset (≥5 years JoSAA); Database seeded and queryable | Data queries return correct results; Data validation report produced |
| **M3** | ML Core | Trained and evaluated prediction model; Model serialised and loadable; Evaluation metrics documented | Model achieves ≥85% accuracy on test set |
| **M4** | Backend API — Core | FastAPI application; Auth endpoints; Prediction endpoint; College/cutoff query endpoints | All endpoints return correct responses; Pydantic validation active |
| **M5** | Backend API — Complete | Recommendation engine; Admin endpoints; Analytics endpoints; OpenAPI documentation complete | API fully documented; Integration tests passing |
| **M6** | Frontend — Core | Project scaffolded; Design system established; Prediction form functional end-to-end | User can submit rank, receive probability score |
| **M7** | Frontend — Complete | Dashboard; Cutoff trend charts; Recommendations UI; Authentication flow; Dark mode | All FR1–FR14 have at least v1 implementations |
| **M8** | Integration | End-to-end integration verified; Error handling tested; Loading/empty states implemented | No integration failures on critical user paths |
| **M9** | Quality & Security | Test suite complete; Security checklist passed; Performance benchmarks met; Linting passes | All success criteria in Section 14.1 are met |
| **M10** | Deployment | Live frontend on Vercel; Live backend on Render; Live PostgreSQL on cloud; CI/CD pipeline configured | Application accessible at public URL without manual steps |
| **M11** | Documentation & Portfolio | README complete; API docs live; User guide written; Developer onboarding guide complete | New developer can run project locally within 30 minutes using only the README |

---

## 17. Questions That Must Be Answered Before Development

> These questions must be resolved before Phase 2 begins. Answers will directly shape technical decisions that are difficult to reverse once implementation starts.

### Data Questions

**DQ-01** — Is a clean, machine-readable dataset of JoSAA historical cutoffs (2019–2024) already available, or must it be built from scratch by parsing PDFs and unofficial sources? This is the single most important question because it determines the scope and risk of Phase 2.

**DQ-02** — Will the project use data from Round 1 only (most conservative opening cutoff), all 6 rounds (full closing rank picture), or a synthesised view? This decision directly affects model feature design.

**DQ-03** — How will inconsistencies in institute naming across years be handled? (Example: "NIT Trichy" vs. "National Institute of Technology, Tiruchirappalli") A canonical name registry must be defined before ingestion begins.

**DQ-04** — Are Special Round and Preparatory Round data (for SC/ST) included or excluded from v1?

**DQ-05** — What is the policy for handling institutes that were added or removed from JoSAA counselling mid-dataset period? (e.g., new IIITs added in 2022)

### Domain Questions

**DQ-06** — Should the prediction engine treat **home-state quota** and **other-state quota** as separate prediction tracks? (Home-state quotas have significantly different closing ranks.) This is a critical modelling decision.

**DQ-07** — Will **PWD (Persons with Disabilities)** sub-categories be modelled separately? Their cutoffs behave very differently and require dedicated data handling.

**DQ-08** — Is the scope limited to **JEE Main** rank (NITs/IIITs/GFTIs) or does it also include **JEE Advanced** rank (IITs)? Including IITs dramatically increases data and modelling complexity.

**DQ-09** — Should **branch preference ordering** be a model input? (A student's willingness to trade college rank for branch quality is a highly relevant but complex signal.)

**DQ-10** — Will the system model counselling round strategy (i.e., "should I upgrade in Round 3?"), or strictly predict whether a student will be allocated a specific college-branch?

### Product & UX Questions

**DQ-11** — Should **unauthenticated (guest) users** be able to receive predictions? If yes, how many predictions per session before a registration prompt appears? This affects the authentication architecture.

**DQ-12** — Should prediction results be **shareable via URL** (e.g., for a student to share results with parents)? This has architectural implications for how results are stored.

**DQ-13** — Is a **comparison view** (side-by-side comparison of 2–3 colleges) needed in v1, or is this future scope?

**DQ-14** — What is the preferred mechanism for displaying **prediction uncertainty** to non-technical users? (Options: confidence intervals, verbal qualifiers, colour-coded tiers, a combination)

### Technical Questions

**DQ-15** — Which **cloud PostgreSQL provider** will be used: Render Postgres, Supabase, or Neon? Each has different connection limits, free-tier constraints, and PostgreSQL version support.

**DQ-16** — Is **OAuth (Google login)** required in v1, or is email-password authentication sufficient for the initial release?

**DQ-17** — Should the **ML model** be embedded directly in the FastAPI process, or served as a separate endpoint? (Separate service adds resilience but increases deployment complexity.)

**DQ-18** — Will **Celery** be used for background task processing (e.g., dataset ingestion), or are FastAPI BackgroundTasks sufficient for v1 given free-tier deployment constraints?

**DQ-19** — What is the **model retraining strategy** when new yearly data becomes available? Manual trigger by admin, or automated pipeline?

### Project & Evaluation Questions

**DQ-20** — What are the **evaluation rubrics** used by the industrial training supervisors? Understanding whether the assessment prioritises feature completeness, code quality, documentation, or originality will directly influence phase sequencing.

**DQ-21** — Is there a **fixed submission date**? If yes, what is it? This determines whether the full milestone roadmap (M0–M11) is achievable or whether certain milestones must be descoped.

**DQ-22** — Should this project be **open source** (public GitHub repository)? This has implications for secret management, licensing, and whether production database credentials are ever committed to version control.

**DQ-23** — Is a **project demonstration video** required as part of the submission? If yes, this must be planned as a deliverable in the documentation phase.

**DQ-24** — Will any **domain expert** (someone with direct JoSAA counselling experience) be available to review the domain logic assumptions before the ML model is trained?

**DQ-25** — Are there any **institutional or legal restrictions** on hosting, processing, or displaying JoSAA data that must be investigated before data collection begins?

---

## 18. Final Recommendations

*Written in the voice of the Lead Software Architect.*

---

### Recommendation 1: Treat Data as the Highest Risk — Validate It First

The most dangerous assumption in this project is that clean, structured historical data is available and parseable. Every subsequent decision — the ML model, the database schema, the API design — depends on this assumption being true. Before any code is written, invest time in manually collecting, inspecting, and understanding the raw data. If the data is messier than expected, discover this in Week 1, not Week 6.

**Practical Action:** Before Phase 2 begins, manually download JoSAA cutoff data for two years (e.g., 2022 and 2023) and attempt to load it into a spreadsheet in a consistent format. This exercise will reveal every normalisation challenge the ETL pipeline must handle.

---

### Recommendation 2: Build a Credible Baseline Before a Complex Model

A common mistake in educational ML projects is jumping directly to the most sophisticated model available before establishing what a simple model can achieve. For this problem, a strong baseline is: *"Does the student's rank fall within the historical opening and closing rank range for this college-branch-category?"* This rule-based approach requires no ML and may already produce 80%+ accuracy. The ML model's job is to improve on this baseline — not to replace common sense.

**Practical Action:** Implement and document the baseline before training any ML model. Report both baseline and model performance. The gap between them is the ML model's demonstrable value-add.

---

### Recommendation 3: Design the API Contract Before Writing Any Code

Before writing the first line of FastAPI code, define the complete API contract: every endpoint, its URL, HTTP method, request schema, success response schema, and error response schema. This document becomes the integration contract between frontend and backend, and the basis for test cases. It prevents the scenario where the backend is built to one set of assumptions while the frontend is built to another.

**Practical Action:** In Phase 2, produce an OpenAPI YAML file that defines the complete API surface. Both frontend and backend development must validate against this contract.

---

### Recommendation 4: Make the Architecture Extensible Without Over-Engineering It

There is a tension between designing for future scope (state counselling, IITs, mobile apps) and keeping v1 simple enough to build and maintain. The resolution is: **design for extensibility at the data model and API layer, but not at the implementation layer.**

This means:
- The database schema should include a `counselling_body` field so state-level data can be added without schema migration.
- API URLs should be versioned from day one (`/api/v1/`).
- The ML prediction engine should be behind a service interface so the underlying model can be swapped without changing any API code.

It does **not** mean building a plugin system, a message queue, or a microservices architecture in v1. Those are premature at this scale.

---

### Recommendation 5: Version Control Discipline Is Non-Negotiable for Portfolio Projects

Recruiters and senior engineers evaluating an internship portfolio look at Git history. A single "initial commit" with all files, or commits like "fix stuff" and "changes", signals that the candidate does not understand professional software development. This project's Git history should tell the story of its evolution — feature by feature, phase by phase.

**Practical Action:** Establish a commit message convention before writing code. A format such as `feat(auth): implement JWT refresh token rotation` or `fix(etl): handle missing round data for pre-2021 years` is sufficient and professional.

---

### Recommendation 6: Document Decisions, Not Just Actions

The most valuable part of a portfolio project is not the code — it is evidence of engineering judgement. For every significant technical decision (choice of ML algorithm, database normalisation strategy, authentication approach), document: (1) what options were considered, (2) why the chosen option was selected, (3) what the tradeoffs are.

These decision records, maintained in a `docs/decisions/` directory or in an `ARCHITECTURE_DECISIONS.md` file, demonstrate the thinking process that separates an engineer from a code typist.

---

### Recommendation 7: Design the Disclaimer Strategy Before Launch

The prediction model will be wrong sometimes. Users must understand this before they rely on it. The interface must be designed from the beginning with transparent uncertainty communication — not as a legal afterthought. Every prediction output screen should include contextual language that frames the result as a probability derived from historical trends, not a guarantee, and should recommend users also consult official counselling resources.

---

### Recommendation 8: Build with Evaluation in Mind from Day One

This project will be demonstrated and evaluated. Before the final phase, identify exactly how evaluation will happen: Will the evaluator run the code locally? Access the deployed URL? Review the GitHub repository? Read the documentation? Each scenario has different preparation requirements. Design the demonstration flow as explicitly as any user flow.

---

> [!IMPORTANT]
> This document is the governing reference for all subsequent development decisions on the Chances of Admission (India) project. Any deviation from the scope, requirements, or constraints defined here must be documented with a rationale and reviewed before implementation proceeds. No implementation of any kind has been performed as part of this document.

---

**Phase 1 completed successfully. Awaiting Phase 2: System Architecture & Technical Design.**
