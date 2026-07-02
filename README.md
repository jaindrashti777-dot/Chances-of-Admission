<div align="center">
  <img src="https://via.placeholder.com/150" alt="Chances of Admission Logo">
  <h1>Chances Of Admission (India)</h1>
  <p>An AI-powered web application for predicting engineering college admission probabilities using historical JoSAA counselling data.</p>
</div>

---

## 📖 Project Overview
The transition from high school to engineering colleges in India is highly competitive. Students face immense anxiety when analyzing their Joint Entrance Examination (JEE) ranks against thousands of college and branch permutations.

**Chances Of Admission (India)** solves this by utilizing machine learning to predict the closing ranks for National Institutes of Technology (NITs), Indian Institutes of Information Technology (IIITs), and Government Funded Technical Institutes (GFTIs). It calculates a personalized probability score and categorizes options into Safe, Target, and Dream colleges.

## 🎯 Objectives
- **Predictive Accuracy**: Estimate closing ranks based on historical JoSAA data (2016-2023).
- **Explainable AI**: Provide transparency into *why* a prediction was made using SHAP values.
- **Decision Support**: Recommend colleges tailored to a student's rank, category, quota, and gender.
- **Scalability**: Deliver predictions via a high-performance, stateless API built on FastAPI.

## ✨ Features
- **Admission Probability Gauge**: Instantly view the percentage chance of securing a seat.
- **Smart Recommendations**: Categorized college lists (Safe, Target, Dream).
- **Interactive Form**: Strict validation of user inputs via Zod and React Hook Form.
- **SHAP Explanations**: Understand which factors (e.g., Category, Quota) influenced the prediction.

## 🏗 Architecture
The system follows a classic decoupled 3-tier architecture:
- **Frontend**: A React SPA that consumes REST APIs, hosted on a global CDN.
- **Backend API**: A FastAPI service routing requests, performing ML inference, and handling DB interactions.
- **ML Pipeline**: An offline scikit-learn/XGBoost pipeline that trains the model and serializes it as an artifact.
- **Database**: PostgreSQL storing historical cutoffs for fast recommendation querying.

## 💻 Technology Stack
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts.
- **Backend**: Python 3.12, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic.
- **Machine Learning**: Pandas, Scikit-Learn, XGBoost, SHAP, Joblib.
- **DevOps**: Docker, Docker Compose, GitHub Actions, Vercel, Render.

## 🚀 Running Locally

### Prerequisites
- Docker and Docker Compose installed.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chances-of-admission.git
   cd chances-of-admission
   ```
2. Create environment variables:
   ```bash
   cp .env.example .env
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: `http://localhost:5173`
   - Backend API Docs: `http://localhost:8000/docs`

## 📈 Machine Learning Workflow
The ML pipeline is entirely self-contained within the `ml/` directory.
1. **Data Cleaning**: Handled by `src/data/make_dataset.py` to standardize nomenclature.
2. **Feature Engineering**: A `ColumnTransformer` handles One-Hot Encoding for categorical features (Quota, Category) and Min-Max scaling for numerical features.
3. **Training**: An XGBoost regressor is trained to predict the `closing_rank` with hyperparameter optimization via GridSearchCV.
4. **Inference**: The combined preprocessor and regressor are saved as `best_model.joblib`. The FastAPI backend loads this artifact into memory as a Singleton on startup.

## ☁️ Deployment
- **Frontend**: CI/CD configured via GitHub Actions to deploy to Vercel automatically.
- **Backend**: Deployed to Render as a Web Service running a Docker container.
- **Database**: PostgreSQL hosted securely in the cloud.

## ⚠️ Known Limitations
- The model's accuracy degrades for newly introduced branches with less than 3 years of historical data.
- The MVP focuses exclusively on JoSAA counselling (NITs, IIITs, GFTIs) and does not currently include IITs (JEE Advanced) or state-level counselling bodies.

## 🔮 Future Improvements (v2.0)
- **User Accounts**: Allow users to save their profile and track changes across counselling rounds.
- **Cutoff Trend Analysis**: Add historical charts to the frontend.
- **IIT Integration**: Incorporate JEE Advanced data.

## 📄 License
This project is licensed under the MIT License.

## 🙏 Acknowledgements
Built as an Industrial Training Project for the Python Programming for AI & Data Science course.
