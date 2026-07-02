from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.core.exceptions import setup_exception_handlers
from backend.app.core.middleware import setup_middlewares
from backend.app.api.api_v1.api import api_router
from backend.app.prediction.model_service import model_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the Machine Learning model
    model_manager.load_model()
    yield
    # Shutdown logic (if any)

def create_app() -> FastAPI:
    # 1. Setup Logging
    setup_logging()
    
    # 2. Initialize App
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="API for predicting engineering admission chances in India.",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # 3. Setup Middlewares
    setup_middlewares(app)
    
    # 4. Setup Exception Handlers
    setup_exception_handlers(app)
    
    # 5. Include Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/", tags=["root"])
    def root():
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "docs": "/docs"
        }
        
    return app

app = create_app()
