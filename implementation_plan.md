# Engineering Refactor Mode: Implementation Plan

The application is feature-complete. The objective is now to transform it from an AI-generated prototype into a handcrafted, professional software engineering project ready for Version 1.0 release. 

## Goal
Eliminate "AI fingerprints" (generic naming, massive files, repeated logic, placeholder UI) and enforce strict architectural boundaries, maintainability, and quality standards.

## User Review Required
> [!IMPORTANT]
> The refactor will be conducted iteratively. For each phase, I will:
> 1. **Review** the code.
> 2. **Explain** the findings and proposed changes.
> 3. **Refactor** the code.
> 4. **Validate** the changes.
> I will STOP after each phase and request your approval before moving to the next.

## Execution Phases

### Phase 1: Architecture & Folder Structure Review
- **Audit**: Analyze the overall project hierarchy, feature ownership, and module boundaries.
- **Action**: Remove dead folders, rename generic folders, ensure strict separation of concerns.
- **Deliverable**: Initialize `Engineering-Decisions.md` to track all major architectural decisions moving forward.

### Phase 2: Database & Data Layer Review
- **Audit**: Review `backend/app/db/`, `backend/app/models/`, and `backend/app/repositories/`.
- **Action**: Check schema normalization, index logic, query efficiency, and repository pattern implementation. Refactor generic naming (e.g., `base.py`, `item.py`) into domain-driven naming.

### Phase 3: Backend API & Services Review
- **Audit**: Review `backend/app/api/` and `backend/app/services/`.
- **Action**: Audit Request lifecycle, strict Pydantic validation, unified error handling, and robust logging. Remove excessive abstractions if they constitute over-engineering, or add them if under-engineered.

### Phase 4: Machine Learning Pipeline Review
- **Audit**: Review `ml/` and `backend/app/ml_integration/`.
- **Action**: Ensure reproducible preprocessing, justify feature engineering, and decouple model serving completely from core business logic. Remove any "fake analytics" or pseudo-ML code.

### Phase 5: Frontend & UX Review
- **Audit**: Review `frontend/src/` (components, pages, routing, hooks).
- **Action**: Eliminate generic Tailwind "placeholder cards", refine typography, check accessibility, and enforce proper React state management/memoization. Make the UI feel intentionally designed.

### Phase 6: Documentation & Final Polish
- **Audit**: Review all Markdown files in `docs/` and `project-docs/`.
- **Action**: Rewrite documentation to reflect human engineering logic. Remove "AI-generated" phrasing. 
- **Deliverable**: Generate the Final Review Scorecard from the perspectives of a Senior Engineer, Engineering Manager, Tech Lead, and Recruiter.

## Open Questions
- Do you agree with this phased order of execution?
- Would you prefer me to commit my changes after *each phase* or at the very end of the entire audit?
