import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import joblib
import json
from pathlib import Path
import logging
from datetime import datetime

from ml.src.features.build_features import get_feature_pipeline

logger = logging.getLogger(__name__)

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    return {"MAE": mae, "RMSE": rmse, "R2": r2}

def train_and_tune(df: pd.DataFrame, target_col: str, models_dir: str, reports_dir: str):
    X = df.drop(columns=[target_col, 'opening_rank'], errors='ignore')
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    preprocessor = get_feature_pipeline()
    
    # Define models to compare
    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(random_state=42),
        "XGBoost": XGBRegressor(random_state=42, objective='reg:squarederror')
    }
    
    results = {}
    best_model = None
    best_score = float('-inf')
    best_name = ""
    
    for name, regressor in models.items():
        logger.info(f"Training {name}...")
        pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                   ('model', regressor)])
        
        # Hyperparameter tuning for XGBoost as an example
        if name == "XGBoost":
            param_grid = {
                'model__n_estimators': [50, 100],
                'model__max_depth': [3, 5],
                'model__learning_rate': [0.1, 0.2]
            }
            grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='r2', n_jobs=-1)
            grid_search.fit(X_train, y_train)
            pipeline = grid_search.best_estimator_
            logger.info(f"Best params for XGBoost: {grid_search.best_params_}")
        else:
            pipeline.fit(X_train, y_train)
            
        metrics = evaluate_model(pipeline, X_test, y_test)
        results[name] = metrics
        
        if metrics['R2'] > best_score:
            best_score = metrics['R2']
            best_model = pipeline
            best_name = name
            
    logger.info(f"Best model: {best_name} with R2: {best_score}")
    
    # Save the best model and metrics
    Path(models_dir).mkdir(parents=True, exist_ok=True)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    
    model_path = Path(models_dir) / "best_model.joblib"
    joblib.dump(best_model, model_path)
    
    metadata = {
        "training_date": datetime.utcnow().isoformat(),
        "best_model": best_name,
        "metrics": results,
        "features": list(X.columns)
    }
    
    with open(Path(reports_dir) / "training_metrics.json", "w") as f:
        json.dump(metadata, f, indent=4)
        
    logger.info("Training complete. Artifacts saved.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        df = pd.read_csv("ml/data/processed/processed_data.csv")
        train_and_tune(df, target_col="closing_rank", models_dir="ml/artifacts", reports_dir="ml/reports/metrics")
    except Exception as e:
        logger.error(f"Error during training: {e}")
