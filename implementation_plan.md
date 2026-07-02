# Phase 3: Project Structure & Development Environment

This plan outlines the steps to initialize the project repository according to the approved Software Requirements Specification and System Architecture.

## Goal Description
Create a professional development foundation for the "Chances of Admission (India)" project, including a clean folder structure, backend setup (FastAPI), frontend setup (React+Vite+TS), and necessary configuration files, without implementing business logic.

## Proposed Changes

### 1. Folder Structure Setup
We will create a root-level directory structure to separate concerns clearly:
- `frontend/` - React SPA (TypeScript, Vite, Tailwind CSS)
- `backend/` - FastAPI application
- `ml/` - Machine Learning pipelines and model training scripts
- `dataset/` - Raw and cleaned CSV/JSON files containing historical data
- `docs/` - Architecture designs, API contracts, and user guides
- `tests/` - Global E2E and integration tests (unit tests will be inside `frontend/` and `backend/`)
- `scripts/` - Automation scripts for DB seeding, ETL pipelines, and deployments
- `assets/` - Static assets like images or brand logos
- `config/` - Global configuration files

### 2. Configuration Files
Generate root-level configurations:
- `[NEW] .gitignore` - Ignore `node_modules`, `__pycache__`, `.env`, `.venv`, OS files.
- `[NEW] .env.example` - Template for environment variables (DB URLs, API keys) without secrets.
- `[NEW] README.md` - Professional README containing project overview, tech stack, getting started guide, and architecture links.
- `[NEW] .editorconfig` - Enforce consistent indentation (spaces, 2 for JS, 4 for Python).

### 3. Backend Initialization (Python/FastAPI)
- `[NEW] backend/requirements.txt` - Define core dependencies (`fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `pytest`).
- `[NEW] backend/main.py` - Application entry point with a `/health` endpoint placeholder.
- `[NEW] backend/core/config.py` - Configuration loader (Pydantic BaseSettings).
- `[NEW] backend/core/logging.py` - Structured logging setup (JSON logs in prod, readable in dev).
- `[NEW] backend/core/exceptions.py` - Global exception handler placeholder.
- `[NEW] backend/api/dependencies.py` - Dependency injection placeholder.
- `[NEW] backend/Dockerfile` - Docker readiness.

### 4. Frontend Initialization (React/TypeScript/Vite)
- We will use `npx create-vite frontend --template react-ts` to scaffold the project.
- `[NEW] frontend/package.json` - Updated with `tailwindcss`, `eslint`, `prettier`, `react-router-dom`.
- `[NEW] frontend/tailwind.config.js` and `postcss.config.js` - Tailwind setup.
- `[NEW] frontend/src/App.tsx` - Basic layout and routing placeholder.
- `[NEW] frontend/Dockerfile` - Docker readiness.

### 5. Development Standards
- Python: `black` for formatting, `flake8` for linting, `mypy` for typing.
- Frontend: `eslint` and `prettier` for linting and formatting.
- Git: Define a branch strategy (main, dev, feature/*) and commit conventions in the README.

## User Review Required
> [!IMPORTANT]
> Please review this structure and approach. If approved, I will proceed with creating the files and running the initialization commands. This will establish the foundation for all subsequent phases.

## Verification Plan
1. Ensure all directories and files are created successfully.
2. Verify `frontend` starts up without errors.
3. Verify `backend` can be run and serves the `/health` endpoint.
4. Verify linters and formatters are configured.
