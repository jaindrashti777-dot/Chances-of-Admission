from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from backend.app.schemas.prediction import (
    PredictionRequest, 
    PredictionResponse, 
    BatchPredictionRequest, 
    BatchPredictionResponse,
    RecommendationResponse
)
from backend.app.core.responses import APIResponse, success_response, error_response
from backend.app.ml_integration.prediction_service import prediction_service
from backend.app.ml_integration.model_service import model_manager
from backend.app.ml_integration.recommendation_service import recommendation_service
from backend.app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=APIResponse[PredictionResponse])
def predict_admission(request: PredictionRequest):
    """
    Predict admission probability for a single college/branch combination.
    """
    try:
        prediction = prediction_service.process_prediction(request)
        return success_response(prediction)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in /predict endpoint: {e}")
        return error_response("Failed to generate prediction.", str(e))

@router.post("/batch", response_model=APIResponse[BatchPredictionResponse])
def predict_batch(request: BatchPredictionRequest):
    """
    Predict admission probabilities for multiple combinations.
    """
    results = []
    for req in request.predictions:
        try:
            res = prediction_service.process_prediction(req)
            results.append(res)
        except Exception as e:
            logger.warning(f"Batch item failed: {e}")
            # Append a structured error for the specific item or skip
    return success_response(BatchPredictionResponse(results=results))

@router.get("/info", response_model=APIResponse[dict])
def get_model_info():
    """
    Returns metadata about the currently loaded ML model.
    """
    return success_response(model_manager.get_info())

@router.get("/recommendations", response_model=APIResponse[RecommendationResponse])
def get_recommendations(
    user_rank: int,
    category_id: int,
    quota_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Safe, Target, and Dream college recommendations based on historical data.
    """
    try:
        recs = recommendation_service.get_recommendations(db, user_rank, category_id, quota_id)
        return success_response(recs)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return error_response("Failed to generate recommendations.", str(e))
