from typing import Optional, List
from backend.app.schemas.base import BaseSchema

class CollegeBase(BaseSchema):
    name: str
    state: str
    institute_type: str
    is_active: bool = True

class CollegeCreate(CollegeBase):
    pass

class CollegeUpdate(CollegeBase):
    name: Optional[str] = None
    state: Optional[str] = None
    institute_type: Optional[str] = None
    is_active: Optional[bool] = None

class CollegeResponse(CollegeBase):
    id: int

class BranchBase(BaseSchema):
    name: str
    code: Optional[str] = None

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BranchBase):
    name: Optional[str] = None
    code: Optional[str] = None

class BranchResponse(BranchBase):
    id: int
