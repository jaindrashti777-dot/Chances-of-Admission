# 🔍 Chances of Admission — App Analysis Report

## App Overview

**"Chances of Admission (India)"** — A JEE Main rank-based admission probability predictor for NITs, IITs, and GFTIs, powered by JoSAA historical cutoff data. The stack is:

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python) + Uvicorn |
| ML Model | Scikit-learn (`.joblib`) |
| Database | SQLite (`chances.db`) |

---

## 📸 Screenshots

### Home Page
![Home Page](file:///C:/Users/sligh/.gemini/antigravity-ide/brain/53683b2e-9698-404c-ae01-88787faee7cc/landing_page_1783029882321.png)

### Predict Page
![Predict Page](file:///C:/Users/sligh/.gemini/antigravity-ide/brain/53683b2e-9698-404c-ae01-88787faee7cc/predict_page_1783029894021.png)

---

## 🟢 What's Working

| Component | Status | Notes |
|---|---|---|
| Frontend renders | ✅ | Vite dev server up at `localhost:5173` |
| Backend starts | ✅ | FastAPI up at `localhost:8000` |
| ML model loads | ✅ | `ml/artifacts/best_model.joblib` loaded successfully |
| API via Swagger | ✅ | `POST /api/v1/prediction/` returns `200 OK` with `predicted_closing_rank` |
| Backend docs | ✅ | Swagger UI accessible at `http://127.0.0.1:8000/docs` |
| Navigation | ✅ | `/` (Home) and `/predict` routes work |
| Form renders | ✅ | All fields visible with correct dropdowns |

---

## 🔴 Critical Bug — CORS Blocking Frontend ↔ Backend

This is the **root cause** of the prediction failure:

```python
# backend/app/core/middleware.py  (line 47)
allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"]
```

**Problem:** `settings.DEBUG` defaults to `False`, so CORS only allows `https://yourdomain.com`.
The frontend at `http://localhost:5173` is **blocked by CORS**, causing the `Network Error`.

**Fix:** Add `http://localhost:5173` to the allowed origins, or set `DEBUG=True` in the `.env` file.

---

## 🟡 Other Issues Found

### 1. Non-Fatal Logging Error at Startup
The `RequestContextMiddleware` injects `request_id` into log records only during request processing, but `model_manager.load_model()` runs during the **lifespan startup phase** (before any request), so the log formatter fails to find `request_id`:
```
KeyError: 'request_id'
ValueError: Formatting field not found in record: 'request_id'
```
**Impact:** Non-fatal. The server starts fine, but this is noisy and should be fixed.

### 2. Results Page Never Reached
Since the API call fails, users never see the `/results` route. The `Results.tsx` page is fully built (donut chart, risk badge, SHAP explanation panel) but is unreachable until CORS is fixed.

### 3. Duplicate API Client Files
Two identical files exist:
- `frontend/src/api/client.ts`
- `frontend/src/services/api/client.ts`

This is dead code and should be cleaned up.

### 4. No Loading / Error State Shown on Submit
When the form is submitted and fails, the error message shown is generic: *"Prediction failed. Please check your inputs and try again."* There is no spinner or progress indicator during the network call.

---

## 🎨 UI/UX Assessment

| Dimension | Score | Notes |
|---|---|---|
| Visual Design | 6/10 | Clean minimal look, but very plain grey background. No dark mode, no visual flair. |
| Layout | 8/10 | Well-structured, good use of whitespace, responsive |
| Typography | 7/10 | Good bold headers, but body text is generic |
| Color Palette | 5/10 | Monochrome grey + blue accent. Feels basic / unpolished |
| Form UX | 7/10 | Dropdowns have good defaults; placeholder text is helpful |
| Results Page | N/A | Not reachable due to CORS bug |
| Mobile | Unknown | Not tested |

---

## ✅ Recommended Fixes (Priority Order)

### P0 — Fix CORS (blocks all predictions)
Add `localhost:5173` to allowed origins:
```python
# backend/app/core/middleware.py
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```
Or set `DEBUG=True` in the `.env` file.

### P1 — Fix Startup Log Formatter
Initialize `request_id` with a default value in the log record factory, or only attach it inside the middleware dispatch body.

### P2 — Add Loading Spinner on Submit
Show a spinner while the API call is in flight so users know the app is working.

### P3 — Remove Duplicate `api/client.ts`
Delete whichever file is not actually imported, to avoid confusion.

### P4 — UI Polish
- Add a gradient or subtle hero background to the home page
- Consider a dark mode toggle
- Add micro-animations on the Results donut chart

---

## 🎬 Browser Recording

![App walkthrough recording](file:///C:/Users/sligh/.gemini/antigravity-ide/brain/53683b2e-9698-404c-ae01-88787faee7cc/app_analysis_1783029844719.webp)
