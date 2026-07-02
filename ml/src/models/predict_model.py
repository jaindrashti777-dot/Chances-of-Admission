import pandas as pd
import joblib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Predictor:
    def __init__(self, model_path: str):
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        self.pipeline = joblib.load(model_path)
        logger.info("Model loaded successfully.")

    def predict_rank(self, input_data: dict) -> float:
        """
        Predicts the closing rank for a single input dictionary.
        """
        df = pd.DataFrame([input_data])
        prediction = self.pipeline.predict(df)
        return float(prediction[0])
        
    def predict_probability(self, input_data: dict, user_rank: int) -> dict:
        """
        Predicts closing rank and estimates a probability of admission.
        """
        predicted_closing = self.predict_rank(input_data)
        
        # Simple probability heuristic for demonstration
        if user_rank <= predicted_closing * 0.9:
            prob = 0.95 # Highly likely
        elif user_rank <= predicted_closing:
            prob = 0.75 # Likely
        elif user_rank <= predicted_closing * 1.1:
            prob = 0.40 # Borderline
        else:
            prob = 0.05 # Unlikely
            
        return {
            "predicted_closing_rank": round(predicted_closing),
            "user_rank": user_rank,
            "probability_score": prob,
            "confidence": 0.85 # Placeholder for model confidence interval
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example usage
    predictor = Predictor("ml/models/best_model.joblib")
    sample_input = {
        "college_name": "NIT Trichy",
        "branch_name": "Computer Science",
        "institute_type": "NIT",
        "category": "OPEN",
        "quota": "OS",
        "seat_pool": "Gender-Neutral",
        "counselling_body": "JoSAA",
        "year": 2023,
        "round_number": 6
    }
    try:
        res = predictor.predict_probability(sample_input, user_rank=1500)
        print("Prediction Result:", res)
    except Exception as e:
        logger.error(e)
