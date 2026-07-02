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
from backend.app.prediction.predictor import predictor
from backend.app.prediction.model_registry import model_manager
from backend.app.prediction.college_recommender import college_recommender
from backend.app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=PredictionResponse)
def predict_admission(request: PredictionRequest):
    """
    Predict admission probability for a single college/branch combination.
    """
    return predictor.process_prediction(request)

@router.post("/batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest):
    """
    Predict admission probabilities for multiple combinations.
    """
    results = []
    for req in request.predictions:
        try:
            res = predictor.process_prediction(req)
            results.append(res)
        except Exception as e:
            logger.warning(f"Batch item failed: {e}")
            # Append a structured error for the specific item or skip
    return BatchPredictionResponse(results=results)

@router.get("/info")
def get_model_info():
    """
    Returns metadata about the currently loaded ML model.
    """
    return model_manager.get_info()

@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    user_rank: int,
    category_id: int,
    quota_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Safe, Target, and Dream college recommendations based on historical data.
    """
    return college_recommender.get_recommendations(db, user_rank, category_id, quota_id)
