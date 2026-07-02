from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import health, prediction

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
