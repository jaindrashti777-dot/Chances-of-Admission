import logging
import sys
import json
import contextvars
from datetime import datetime
from backend.app.core.config import settings

request_id_contextvar = contextvars.ContextVar("request_id", default="N/A")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
            "request_id": request_id_contextvar.get()
        }
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_contextvar.get()
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(JSONFormatter())
    else:
        # Readable formatting for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        
    logger.addHandler(handler)
    
    # Disable Uvicorn's default access logging format to use our own
    logging.getLogger("uvicorn.access").handlers = []
