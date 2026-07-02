from typing import Optional
from backend.app.schemas.base import BaseSchema

class HistoricalCutoffBase(BaseSchema):
    college_id: int
    branch_id: int
    counselling_body_id: int
    category_id: int
    quota_id: int
    year: int
    round_number: int
    seat_pool: str
    opening_rank: Optional[int] = None
    closing_rank: Optional[int] = None

class HistoricalCutoffCreate(HistoricalCutoffBase):
    pass

class HistoricalCutoffUpdate(HistoricalCutoffBase):
    opening_rank: Optional[int] = None
    closing_rank: Optional[int] = None

class HistoricalCutoffResponse(HistoricalCutoffBase):
    id: int
