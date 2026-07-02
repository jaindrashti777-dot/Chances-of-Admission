# Deployment, DevOps & Production Release Guide

## 1. Production Architecture
- **Frontend**: Hosted on Vercel. Vercel automatically builds the React+Vite app from the `frontend/` directory on every push to `main`.
- **Backend**: Hosted on Render (Web Service). Render builds the FastAPI backend using the provided `Dockerfile` or native Python environment.
- **Database**: PostgreSQL hosted on Render or Supabase. Connection string provided via `DATABASE_URL` environment variable.

## 2. Environment Setup
Never hardcode secrets. Ensure the following variables are securely configured in Vercel and Render dashboard settings:
- `DATABASE_URL`: Connection string for PostgreSQL.
- `CORS_ORIGINS`: Allowed origins (e.g., `["https://your-vercel-app.vercel.app"]`).

## 3. Deployment Workflow
1. **Push to GitHub**: Developer pushes code to `main`.
2. **CI Pipeline (GitHub Actions)**: `.github/workflows/ci.yml` runs automated tests on the backend and builds the frontend.
3. **Continuous Deployment (CD)**:
   - **Vercel** detects the update in the `frontend` folder and redeploys.
   - **Render** detects the update and deploys the backend container.

## 4. Monitoring & Logging
- **Application Health**: The backend exposes `/api/v1/health` which should be plugged into an uptime monitor (e.g., UptimeRobot).
- **Structured Logging**: FastAPI logs all prediction exceptions to standard output, which Render aggregates natively. Do not log PII (Personal Identifiable Information) such as specific ranks mapping to user identities if authentication is ever added.

## 5. Scalability & Load Balancing
- **Database**: Add connection pooling (`PgBouncer` or SQLAlchemy static pools) when connections exceed database limits during peak JoSAA counselling season.
- **Backend**: Render allows horizontal scaling. The model is loaded entirely in-memory at startup (`best_model.joblib`), making the API stateless. Thus, you can spawn multiple FastAPI instances behind a load balancer without any shared state issues.
- **Frontend**: Vercel acts as a global CDN, caching static assets at the edge.

## 6. Disaster Recovery & Backups
- **Database Backups**: Schedule daily automated logical backups (`pg_dump`) to an AWS S3 bucket.
- **Model Backups**: Ensure `best_model.joblib` is version-controlled via Git LFS or stored securely in Cloud Storage. If the model file gets corrupted on Render, a rollback to the previous Git commit instantly restores the previous working model.
