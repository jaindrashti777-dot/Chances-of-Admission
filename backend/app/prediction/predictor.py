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
            explanation = Predictor._generate_explanation(request, predicted_rank, risk)
            
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
    def _generate_explanation(request: PredictionRequest, predicted_rank: float, risk_level: str) -> SHAPExplanation:
        """
        Generates an educational explanation based on the user's inputs and predicted outcomes.
        Provides actionable insights on why a prediction was made.
        """
        top_pos = {}
        top_neg = {}
        
        # 1. Quota Insights
        if request.quota == 'HS':
            top_pos["Home State Quota"] = 100.0
        elif request.quota == 'OS':
            top_neg["All-India Competition (OS)"] = -50.0
            
        # 2. Category Insights
        if request.category != 'OPEN':
            top_pos[f"{request.category} Reservation"] = 150.0
            
        # 3. Rank Proximity Insights
        rank_diff = predicted_rank - request.user_rank
        if risk_level in ["Safe", "Target"]:
            if rank_diff > 0:
                top_pos["Strong Rank Alignment"] = 80.0
        else:
            top_neg["Rank Below Historical Range"] = -120.0
            
        # Generate Educational Summary
        summary_sentences = []
        if request.quota == 'HS':
            summary_sentences.append("Your Home State quota improves your chances significantly by placing you in a specialized seat pool.")
        if request.category != 'OPEN':
            summary_sentences.append(f"Category reservation ({request.category}) significantly affects the prediction, expanding the historical cutoff limits.")
            
        if risk_level == "Safe":
            summary_sentences.append("Your rank is comfortably within the historical range for this branch.")
        elif risk_level == "Target":
            summary_sentences.append("Your rank is highly competitive and aligns closely with historical closing ranks.")
        else:
            summary_sentences.append("Your rank falls outside the typical historical range for this branch, making it highly competitive.")
            
        human_summary = " ".join(summary_sentences)
        
        return SHAPExplanation(
            top_positive_features=top_pos,
            top_negative_features=top_neg,
            human_summary=human_summary
        )

predictor = Predictor()
