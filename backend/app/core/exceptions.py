from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.app.core.responses import error_response
import logging

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc.errors()}")
        response = error_response(
            message="Validation Error",
            details=exc.errors()
        )
        # Assign request_id from state if available
        if hasattr(request.state, "request_id"):
            response.meta.request_id = request.state.request_id
        return JSONResponse(status_code=422, content=response.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        response = error_response(message=exc.detail)
        if hasattr(request.state, "request_id"):
            response.meta.request_id = request.state.request_id
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception occurred")
        response = error_response(message="Internal Server Error")
        if hasattr(request.state, "request_id"):
            response.meta.request_id = request.state.request_id
        return JSONResponse(status_code=500, content=response.model_dump())
