import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
from pathlib import Path
import logging
from datetime import datetime
import shap

from ml.src.features.build_features import get_feature_pipeline

logger = logging.getLogger(__name__)

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    return {"MAE": mae, "RMSE": rmse, "R2": r2}

def train_and_evaluate(df: pd.DataFrame, target_col: str, models_dir: str, reports_dir: str):
    logger.info(f"Starting ML retraining pipeline with {len(df)} records.")
    
    # Time-based split for realistic evaluation
    train_df = df[df['year'] < 2023]
    test_df = df[df['year'] == 2023]
    
    X_train = train_df.drop(columns=[target_col, 'opening_rank'], errors='ignore')
    y_train = train_df[target_col]
    X_test = test_df.drop(columns=[target_col, 'opening_rank'], errors='ignore')
    y_test = test_df[target_col]
    
    logger.info(f"Train size: {len(X_train)} (pre-2023), Test size: {len(X_test)} (2023)")
    
    preprocessor = get_feature_pipeline()
    
    # We focus exclusively on XGBoost per the architecture decision
    regressor = XGBRegressor(
        n_estimators=150, 
        max_depth=6, 
        learning_rate=0.1,
        random_state=42, 
        objective='reg:squarederror',
        n_jobs=-1
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', regressor)
    ])
    
    logger.info("Training XGBoost Regressor...")
    pipeline.fit(X_train, y_train)
    
    logger.info("Evaluating on 2023 holdout set...")
    metrics = evaluate_model(pipeline, X_test, y_test)
    logger.info(f"Metrics: {metrics}")
    
    # Save the best model
    Path(models_dir).mkdir(parents=True, exist_ok=True)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    
    model_path = Path(models_dir) / "best_model.joblib"
    joblib.dump(pipeline, model_path)
    
    # Generate SHAP explainer and save it
    logger.info("Generating SHAP TreeExplainer...")
    try:
        explainer = shap.TreeExplainer(pipeline.named_steps['model'])
        explainer_path = Path(models_dir) / "shap_explainer.joblib"
        joblib.dump(explainer, explainer_path)
    except Exception as e:
        logger.error(f"Failed to create SHAP explainer: {e}")
    
    # Save training metrics
    metadata = {
        "training_date": datetime.utcnow().isoformat(),
        "model_type": "XGBoost",
        "split": "Time-based (Train: <2023, Test: 2023)",
        "metrics": metrics,
        "train_size": len(X_train),
        "test_size": len(X_test)
    }
    
    with open(Path(reports_dir) / "training_metrics.json", "w") as f:
        json.dump(metadata, f, indent=4)
        
    logger.info(f"Training complete. Model saved to {model_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        df = pd.read_csv("ml/data/processed/processed_data.csv")
        train_and_evaluate(df, target_col="closing_rank", models_dir="ml/artifacts", reports_dir="ml/reports/metrics")
    except Exception as e:
        logger.error(f"Error during training: {e}")

