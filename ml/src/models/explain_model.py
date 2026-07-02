import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_shap_explanations(model_path: str, data_path: str, output_dir: str):
    """
    Generates SHAP values and explainability plots for the best model.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        pipeline = joblib.load(model_path)
        df = pd.read_csv(data_path)
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        return
        
    X = df.drop(columns=['closing_rank', 'opening_rank'], errors='ignore')
    
    # We need to extract the actual regressor and the transformed features
    preprocessor = pipeline.named_steps['preprocessor']
    model = pipeline.named_steps['model']
    
    # Transform a sample of data (e.g. 500 rows for speed)
    X_sample = X.sample(n=min(500, len(X)), random_state=42)
    X_transformed = preprocessor.transform(X_sample)
    
    # Check if we can get feature names out of the preprocessor
    try:
        feature_names = preprocessor.get_feature_names_out()
    except AttributeError:
        # Fallback if get_feature_names_out is not supported or errors
        feature_names = [f"Feature_{i}" for i in range(X_transformed.shape[1])]
        
    # Generate SHAP values (using TreeExplainer since we use RF/XGBoost)
    # If LinearRegression, we'd use LinearExplainer. Let's assume Tree for now.
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_transformed)
        
        # Summary Plot
        plt.figure()
        shap.summary_plot(shap_values, X_transformed, feature_names=feature_names, show=False)
        plt.savefig(Path(output_dir) / "shap_summary.png", bbox_inches='tight')
        plt.close()
        
        logger.info(f"SHAP explanations saved to {output_dir}")
        
    except Exception as e:
        logger.error(f"Could not generate SHAP explanations: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_shap_explanations(
        "ml/models/best_model.joblib", 
        "ml/data/processed/processed_data.csv", 
        "ml/reports/explainability"
    )
