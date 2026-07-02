# Project Folder Structure

This document outlines the high-level organization of the Chances Of Admission repository.

```
chances-of-admission/
├── backend/                  # FastAPI Backend Application
│   ├── app/
│   │   ├── api/              # API Route Handlers (v1)
│   │   ├── core/             # Core configurations (Security, Config, Middlewares)
│   │   ├── db/               # Database connection and session management
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic layer
│   │   └── ml_integration/   # Integration layer for the ML Pipeline
│   ├── tests/                # Pytest unit and integration tests
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Production Docker image definition for Backend
│
├── frontend/                 # React + Vite Frontend Application
│   ├── src/
│   │   ├── api/              # Axios client and TanStack query hooks
│   │   ├── components/       # Reusable UI elements (Buttons, Cards, etc.)
│   │   ├── layout/           # Shared page layouts (Navbar, Containers)
│   │   ├── pages/            # View components (Home, Prediction, Results)
│   │   └── utils/            # Helper functions (Tailwind class merging)
│   ├── package.json          # Node dependencies
│   └── Dockerfile            # Production Nginx image definition for Frontend
│
├── ml/                       # Machine Learning Pipeline
│   ├── data/                 # Raw and processed datasets (ignored in source control)
│   ├── models/               # Serialized joblib artifacts
│   ├── reports/              # Metrics and EDA visualizations
│   ├── src/
│   │   ├── data/             # Scripts to clean and preprocess raw data
│   │   ├── features/         # Feature engineering (ColumnTransformer)
│   │   ├── models/           # Training and Prediction scripts (XGBoost)
│   │   └── visualization/    # Exploratory Data Analysis (EDA) plotting
│   └── tests/                # ML Pipeline unit tests
│
├── docs/                     # Comprehensive Project Documentation
│   ├── srs.md                        # Software Requirements Specification
│   ├── architecture_design.md        # System Architecture
│   ├── data_architecture.md          # Database Design and Schemas
│   ├── ml_pipeline.md                # ML Workflow
│   ├── prediction_api.md             # API Design
│   ├── frontend_architecture.md      # Frontend Design
│   ├── deployment_guide.md           # Deployment Workflow
│   ├── internship_report.md          # Final Project Report
│   ├── presentation_content.md       # Demo Scripts & PPT Outline
│   └── viva_questions.md             # Interview Prep
│
├── alembic/                  # Database migration scripts
├── .github/                  # CI/CD Workflows (GitHub Actions)
├── docker-compose.yml        # Local orchestrated development environment
├── .env.example              # Template for environment variables
└── README.md                 # Project Overview and Quickstart Guide
```
