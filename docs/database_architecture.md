# Database Architecture

## Overview
This document outlines the database implementation details for the **Chances Of Admission (India)** project. The database layer is built using PostgreSQL and SQLAlchemy 2.x, designed for high read performance (lookups) and structured normalization.

## Data Models

### 1. Core Reference Tables
- **College**: Institutes (NIT, IIIT, GFTI).
- **Branch**: Academic programs.
- **CounsellingBody**: Organizers (e.g., JoSAA).
- **Category**: Social categories (e.g., GEN, OBC-NCL, SC, ST).
- **Quota**: Domicile quotas (e.g., HS, OS, AI).

### 2. Junction & Fact Tables
- **CollegeBranch**: Many-to-many junction between `College` and `Branch`.
- **HistoricalCutoff**: The central fact table. Stores opening and closing ranks.
  - *Indexes*: B-Tree indexes on lookup columns (`year`, `college_id`, `category_id`, `quota_id`) to accelerate predictions and searches.
  - *Constraints*: Unique constraints on the combination of `college_id`, `branch_id`, `category_id`, `quota_id`, `seat_pool`, `year`, and `round_number`.

### 3. User & Analytics
- **User**: Authentication and profile information.
- **PredictionRecord** (Future): Tracks user queries.

## Repository Pattern
We implement a generic `CRUDBase` class that provides common SQLAlchemy 2.0 select and execute operations. Each model has a specific Repository (e.g., `CRUDCollege`) extending `CRUDBase` to provide custom query methods.

**Rule**: Do NOT put business logic inside Repositories. They should only execute DB operations. 

## Service Layer
Services (e.g., `CollegeService`) act as the orchestrators. They:
1. Handle transaction lifecycle (`db.commit()`, `db.rollback()`).
2. Interact with multiple repositories.
3. Throw appropriate Python exceptions for the API routers to catch.

## Migrations (Alembic)
- Alembic is configured to use the `alembic` directory.
- `env.py` has been modified to read `DATABASE_URL` from the central configuration (`core.config`) and use `backend.app.db.base.Base.metadata`.
- **Workflow**:
  1. Modify SQLAlchemy models in `backend/app/models/`.
  2. Run: `alembic revision --autogenerate -m "description"`
  3. Run: `alembic upgrade head`

## Testing
- Tests use an in-memory SQLite database.
- The `db_session` fixture uses a single connection and starts a nested transaction for each test. After the test completes, the transaction is rolled back. This ensures tests do not leak state and run extremely fast without requiring Dockerized PostgreSQL.
