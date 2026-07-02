import uuid
import time
import logging
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Inject request_id into logging record factory dynamically
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            return record
        
        logging.setLogRecordFactory(record_factory)
        
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
            # Restore factory
            logging.setLogRecordFactory(old_factory)
            
        return response

def setup_middlewares(app: FastAPI):
    app.add_middleware(RequestContextMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"], # Update in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
