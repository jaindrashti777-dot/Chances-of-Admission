from fastapi import APIRouter
from backend.app.core.responses import APIResponse, success_response

router = APIRouter()

@router.get("/health", response_model=APIResponse)
def health_check():
    """
    Check if the API is running and healthy.
    """
    return success_response({"status": "healthy", "version": "1.0.0"})

@router.get("/status", response_model=APIResponse)
def system_status():
    """
    Detailed system status (placeholder for DB and ML checks).
    """
    return success_response({
        "api": "online",
        "database": "unconfigured",
        "ml_model": "unloaded"
    })
