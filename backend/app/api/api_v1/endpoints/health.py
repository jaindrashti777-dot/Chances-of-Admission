from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.prediction.model_registry import model_manager

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Check if the API is running and healthy.
    """
    return {"status": "healthy", "version": "1.0.0"}

@router.get("/status")
def system_status(db: Session = Depends(get_db)):
    """
    Detailed system status, checking database connectivity and ML model availability.
    """
    # Check Database
    try:
        db.execute(text("SELECT 1"))
        db_status = "online"
    except Exception:
        db_status = "offline"

    # Check ML Model
    ml_status = "loaded" if model_manager._model is not None else "unloaded"

    return {
        "api": "online",
        "database": db_status,
        "ml_model": ml_status
    }
