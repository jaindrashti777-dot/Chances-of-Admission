import uuid
import time
import logging
import json
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import request_id_contextvar

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Set contextvar instead of modifying logging factory
        token = request_id_contextvar.set(request_id)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise e
        finally:
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - Status: {getattr(response, 'status_code', 500)} - Time: {process_time:.4f}s"
            )
            request_id_contextvar.reset(token)
            
        return response

def setup_middlewares(app: FastAPI):
    app.add_middleware(RequestContextMiddleware)
    
    # Parse CORS_ORIGINS safely
    origins = []
    if isinstance(settings.CORS_ORIGINS, str):
        try:
            origins = json.loads(settings.CORS_ORIGINS)
        except json.JSONDecodeError:
            origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    elif isinstance(settings.CORS_ORIGINS, list):
        origins = settings.CORS_ORIGINS

    if not origins and not settings.DEBUG:
        origins = ["*"] # Fallback if not configured

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
