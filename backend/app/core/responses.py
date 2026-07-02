from typing import Any, Generic, TypeVar, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

T = TypeVar("T")

class ResponseMeta(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class APIResponse(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

def success_response(data: Any) -> APIResponse:
    return APIResponse(status="success", data=data)

def error_response(message: str, details: Optional[Any] = None) -> APIResponse:
    return APIResponse(status="error", error={"message": message, "details": details})
