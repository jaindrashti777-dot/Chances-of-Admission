from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Check if the API is running and healthy.
    """
    return {"status": "healthy", "version": "1.0.0"}

@router.get("/status")
def system_status():
    """
    Detailed system status (placeholder for DB and ML checks).
    """
    return {
        "api": "online",
        "database": "unconfigured",
        "ml_model": "unloaded"
    }
