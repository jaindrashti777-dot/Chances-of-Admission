# Data Architecture & Database Design
## Chances of Admission (India)

---

| Document Attribute | Detail |
|---|---|
| **Project Name** | Chances of Admission (India) |
| **Document Version** | 1.0 |
| **Document Status** | Approved — Final Data Blueprint |
| **Category** | Industrial Training Project |
| **Course** | Python Programming for AI & Data Science |
| **Document Type** | Data Architecture & Database Design |
| **Prepared By** | Lead Data Architect & Database Engineer |
| **Phase** | Phase 4 — Data Architecture & Database Design |

---

## 1. Overall Data Architecture

The Data Architecture represents the flow of information across the entire system. It acts as the backbone, connecting offline raw data processing with online real-time inference.

**Information Flow Sequence:**
1.  **Dataset to Database (ETL):** Raw historical counselling data (PDFs/CSVs) undergoes Extraction, Transformation, and Loading (ETL). This offline script cleans the data, normalizes college and branch names, and securely loads it into the PostgreSQL Database.
2.  **Database to Machine Learning:** Historical cutoff data is extracted from the database by the ML Training pipeline. Feature engineering is applied, models are trained and serialized, and metadata about the model (version, accuracy) is written back to the database.
3.  **Frontend to Backend (User Input):** The student interacts with the UI, submitting their profile (Rank, Category, State, Branch preference).
4.  **Backend to Prediction Engine:** The Backend API validates this payload and passes it to the ML Prediction Engine, which loads the serialized model and processes the features.
5.  **Prediction Engine to Database:** The Backend fetches contextual data (e.g., college details, historical trends) from PostgreSQL to enrich the prediction result.
6.  **Backend to Frontend:** The final prediction and recommendation payload is formatted and served back to the user.
7.  **Backend to Database (Analytics/Storage):** Asynchronously, the backend stores the anonymous prediction event (and tied to a user profile if authenticated) into the database for future analytics.

---

## 2. Entity Identification

The following are the core entities that map the real-world domain of Indian Engineering Admissions into the system:

*   **College:** Represents an educational institution (e.g., NIT Trichy, IIIT Hyderabad). Contains metadata like name, state, type (NIT/IIIT/GFTI), and establishment year.
*   **Branch:** Represents an academic program (e.g., Computer Science, Mechanical Engineering).
*   **Counselling Body:** Represents the authority governing admissions (e.g., JoSAA, CSAB, MHT-CET).
*   **Category:** Represents social categories (General, OBC-NCL, SC, ST, EWS).
*   **Quota / Seat Type:** Represents the allocation pool (e.g., Home State (HS), Other State (OS), All India (AI), Gender-neutral vs. Female-only).
*   **Historical Cutoff Record:** The central transactional entity linking a College, Branch, Category, Quota, Round, and Year to specific Opening and Closing Ranks.
*   **Student Profile:** Represents a registered user's baseline data (Name, Email, Home State, Default Category).
*   **Prediction Query:** Represents a distinct search executed by a user, storing the parameters used (Rank, Category) and a reference to the results.
*   **ML Model Metadata:** Tracks different versions of trained models, their training dates, evaluation metrics (accuracy, F1-score), and the path to the serialized file.
*   **System Event / Analytics Log:** A read-heavy ledger tracking API usage, popular college searches, and system health.

---

## 3. Relationships

The system relies on a highly relational structure. 

*   **Counselling Body to College (One-to-Many):** One counselling body (like JoSAA) governs multiple colleges. (Future-proofs for adding state boards).
*   **College to Branch (Many-to-Many):** A college offers multiple branches, and a branch (like CSE) is offered by multiple colleges. This necessitates a junction entity (e.g., `CollegeBranchOfferings`).
*   **Historical Cutoff Record to College/Branch (Many-to-One):** Millions of cutoff records will point to a specific College and Branch offering.
*   **Historical Cutoff Record to Category/Quota (Many-to-One):** Each cutoff record strictly belongs to one Category and one Quota.
*   **Student Profile to Prediction Query (One-to-Many):** A registered student can perform and save multiple prediction searches over time.
*   **ML Model Metadata to Prediction Query (One-to-Many):** Every stored prediction should reference which model version generated it to ensure traceability.

---

## 4. Database Strategy

**Why PostgreSQL?**
PostgreSQL is selected because the data domain is heavily relational. Normalization is critical to avoid data anomalies (e.g., misspelling "NIT Surathkal" in thousands of cutoff rows). PostgreSQL offers robust ACID compliance, advanced indexing (B-Tree, Hash), and excellent support for complex JOIN operations required by the Recommendation Engine.

**Normalization Strategy:**
The schema will follow 3rd Normal Form (3NF). 
*   We will not store the string "Computer Science and Engineering" 50,000 times in the cutoffs table. Instead, the cutoff table will hold an integer `branch_id`.
*   This prevents update anomalies and heavily compresses the total database size.

**Indexing Philosophy:**
*   Primary Keys (IDs) are indexed automatically.
*   Foreign Keys will be indexed to speed up relational JOINs.
*   Composite Indexes will be created for common search patterns (e.g., an index on `[college_id, branch_id, year]` in the cutoff table).

**Future Scalability:**
By normalizing `Counselling Body` and `Quota`, the database can expand from JoSAA (NITs/IIITs) to state-level admissions (MHT-CET) simply by adding new rows to lookup tables, without altering the schema or core code.

---

## 5. Historical Dataset Strategy

*   **Origins:** Historical data typically originates from official JoSAA PDFs, CSAB archives, or scraped portals.
*   **Structure:** Expected to be tabular (Year, Round, Institute, Program, Seat Type, Gender, Opening Rank, Closing Rank).
*   **Cleaning Challenges:** 
    *   *Institute Renaming:* Colleges occasionally change names. A canonical mapping strategy must be implemented during ETL to map legacy names to standard `college_id`s.
    *   *Branch Restructuring:* "IT" might merge into "CSE". 
*   **Missing Values:** If an Opening Rank is present but Closing Rank is missing (or vice-versa), the ETL pipeline must flag it. Usually, rank '0' indicates no seats allocated.
*   **Duplicates:** The ETL script will enforce uniqueness on the composite key `(college, branch, category, quota, round, year)` and upsert/ignore duplicates.
*   **Versioning / Yearly Updates:** The ETL pipeline will be designed to accept a new CSV file every year (e.g., `josaa_2025.csv`). The data is append-only. Historical records are immutable.

---

## 6. Data Validation Strategy

Data integrity is enforced at the API boundary before hitting the database or ML model.

*   **Student Inputs (Rank):** Must be an integer > 0. (Cannot have rank 0 or negative).
*   **Categories & Quotas:** Must be validated against an allowed Enum list (e.g., `['GEN', 'OBC-NCL', 'SC', 'ST', 'EWS']`).
*   **States:** Must map strictly to standard ISO-3166-2:IN codes or official full string names.
*   **Percentages (Model Output):** Must be a float between `0.0` and `100.0`.
*   **Outliers:** If an input rank is highly improbable (e.g., Rank 1,500,000 for JoSAA), the system will flag a warning but may still process the request, returning a 0% probability.
*   **Missing Values (Nulls):** In historical data, null opening ranks indicate zero allocation. In API inputs, category and rank are strictly non-nullable.

---

## 7. Machine Learning Dataset Design

*   **Target Variable (y):** 
    *   *Approach 1 (Classification):* `is_admitted` (Boolean 1 or 0) based on whether the input rank is <= the historical Closing Rank.
    *   *Approach 2 (Regression):* Predicting the exact closing rank, then calculating probability based on input distance from the predicted rank.
*   **Features (X):**
    *   *Categorical:* College ID, Branch ID, Category, Quota, Gender.
    *   *Numerical:* Year (to track trend inflation), Target Rank.
*   **Encoding Strategy:** 
    *   Target Encoding or One-Hot Encoding for Categories and Quotas. 
    *   College and Branch IDs should be embedded or target-encoded, as One-Hot Encoding 100+ colleges will create a highly sparse, inefficient matrix.
*   **Normalization Strategy:** Numerical inputs (Rank) will be scaled using `StandardScaler` or `MinMaxScaler` to prevent large rank values from dominating the model weights.
*   **Train/Test Split Philosophy:** Time-series split is crucial. Train on 2019-2022, test on 2023. *Do not use random K-Fold cross-validation across years*, as this leaks future cutoff trends into the past.
*   **Model Versioning:** The pipeline will output serialized models (e.g., `v1.0.joblib`) accompanied by a JSON metadata file tracking hyperparameters and test accuracy.

---

## 8. Prediction Storage Strategy

*   **Should predictions be stored?** Yes. Storing predictions helps build analytics on user behavior and model usage.
*   **Metadata Stored:** Input Rank, Input Category, Input State, Top 3 Recommended Colleges, Model Version, Timestamp.
*   **Retention Strategy:** Anonymous prediction logs will be aggressively aggregated and raw logs deleted after 90 days. Authenticated user predictions are retained until the user deletes their account.
*   **Privacy Considerations:** Unauthenticated predictions must never store IP addresses or browser fingerprints to maintain strict anonymity.

---

## 9. Analytics Data

To measure the platform's utility and continuously improve the recommendation engine, we collect:
*   **Prediction Frequency:** Volume of API calls per hour/day to manage load scaling.
*   **Popular Colleges & Branches:** Aggregated counts of which institutions and programs are most frequently queried. This data can power a "Trending Colleges" UI section.
*   **Traffic Trends:** Spikes corresponding to exam result days or counselling round dates.
*   **Data Avoidance:** We strictly *do not* collect personally identifiable information (PII) like names or precise locations in the analytics stream. Rank distributions are analyzed only in aggregate batches.

---

## 10. Security & Privacy

*   **PII:** If a user registers, their email and name are PII. The database will separate identity tables from prediction tables, linked only by an abstract UUID.
*   **Data Encryption:** Passwords hashed via Bcrypt. Database connections encrypted via SSL/TLS. 
*   **Access Control:** Read-only database user for the API. Admin database user isolated for migrations and ETL tasks.
*   **Input Validation:** Pydantic schemas sanitize and validate all inputs, rejecting SQL injection attempts immediately.
*   **Backup Strategy:** Automated daily snapshots of the PostgreSQL database, retained for 30 days.

---

## 11. Performance Considerations

*   **Indexing Philosophy:** "Index for Reads, optimize for Writes." Since historical data is written once a year but read millions of times, heavy composite indexing on `(college_id, category_id)` is justified despite write penalties.
*   **Query Optimization:** Avoid `SELECT *`. The API will only select the specific columns required to render the UI. Use SQLAlchemy's `joinedload` or `selectinload` to prevent N+1 query problems when fetching College -> Branch relationships.
*   **Caching Opportunities:** Static lookup tables (List of Colleges, List of States) will be cached in memory on the backend upon startup.
*   **Archiving:** If the database grows too large, data older than 7 years can be partitioned or moved to cold storage, as its relevance to current ML predictions diminishes.

---

## 12. Future Expansion

The normalized architecture acts as a foundation for rapid growth:
*   **More Counselling Systems:** By adding rows to the `CounsellingBody` table, we can ingest MHT-CET data without altering the schema.
*   **More Entrance Exams:** A `ScoreType` entity (JEE Main, JEE Advanced, State CET) can easily map to inputs.
*   **Multiple Prediction Models:** The `ModelMetadata` table allows the API to A/B test a Random Forest vs. a Gradient Boosting model simultaneously.
*   **Admin Dashboard:** The analytics tables are pre-designed to provide immediate visualizations of system usage for an admin portal.

---

## 13. Architect Recommendations

1.  **Maintainability via Normalization:** Do not take shortcuts by flattening the database to avoid JOINs. A fully normalized database ensures data integrity. Performance issues from JOINs can be solved with indexing, but data corruption from denormalization is permanent.
2.  **Machine Learning Readiness:** Treat historical data as immutable. If an error in the data is found, append a correction rather than overwriting history arbitrarily, to ensure ML training remains reproducible.
3.  **Data Quality over Algorithm Complexity:** A simple Logistic Regression model trained on perfectly cleaned, outlier-removed data will outperform a complex Deep Neural Network trained on noisy, duplicated JoSAA PDFs. Invest heavily in the ETL/Cleaning phase.
4.  **Portfolio Quality:** Document the database schema using an Entity-Relationship Diagram (ERD) in the project documentation. Database architecture is highly scrutinized by senior engineering interviewers.
5.  **Internship Evaluation:** Be prepared to explain the *Time-Series split* for ML training. Evaluators look for this specifically in forecasting/historical trend projects.

---

**Phase 4 completed successfully. Awaiting Phase 5: Backend Foundation & API Architecture.**
