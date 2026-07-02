import pandas as pd
import logging
import shap
from fastapi import HTTPException
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse, SHAPExplanation
from backend.app.prediction.model_registry import model_manager

logger = logging.getLogger(__name__)

class Predictor:
    @staticmethod
    def process_prediction(request: PredictionRequest) -> PredictionResponse:
        model = model_manager.get_model()
        if not model:
            raise HTTPException(status_code=503, detail="Prediction model is currently unavailable.")
            
        # Convert request to DataFrame
        input_data = request.model_dump(exclude={'user_rank'})
        df = pd.DataFrame([input_data])
        
        try:
            # Predict closing rank
            predicted_rank = float(model.predict(df)[0])
            
            # Probability Heuristic
            user_rank = request.user_rank
            if user_rank <= predicted_rank * 0.8:
                probability = 0.95
                risk = "Safe"
            elif user_rank <= predicted_rank * 1.05:
                probability = 0.70
                risk = "Target"
            elif user_rank <= predicted_rank * 1.2:
                probability = 0.35
                risk = "Reach"
            else:
                probability = 0.05
                risk = "Unlikely"
                
            # SHAP Explainability
            explanation = PredictionService._generate_explanation(model, df, risk)
            
            return PredictionResponse(
                predicted_closing_rank=round(predicted_rank),
                user_rank=user_rank,
                admission_probability=probability,
                confidence_score=0.85, # Static for MVP, can be derived from variance in trees
                risk_level=risk,
                explanation=explanation
            )
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail="Error during prediction processing.")

    @staticmethod
    def _generate_explanation(model, df, risk_level) -> SHAPExplanation:
        """
        Generates a simplified SHAP explanation for the API response.
        """
        try:
            preprocessor = model.named_steps['preprocessor']
            regressor = model.named_steps['model']
            
            X_transformed = preprocessor.transform(df)
            explainer = shap.TreeExplainer(regressor)
            shap_values = explainer.shap_values(X_transformed)
            
            # This is a highly simplified dummy aggregation for API response formatting.
            # In production, map shap_values[0] back to feature names.
            top_pos = {"Category Match": 120.5}
            top_neg = {"High Competition State": -45.2}
            
            summary = f"Based on historical trends, this is a {risk_level} option. The category and quota are the strongest positive factors."
            
            return SHAPExplanation(
                top_positive_features=top_pos,
                top_negative_features=top_neg,
                human_summary=summary
            )
        except Exception as e:
            logger.warning(f"Failed to generate SHAP explanation: {e}")
            return None

predictor = Predictor()
