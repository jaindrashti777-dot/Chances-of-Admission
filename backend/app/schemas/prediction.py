from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    user_rank: int = Field(..., gt=0, description="The candidate's JEE rank")
    college_name: str = Field(..., description="Name of the target college")
    branch_name: str = Field(..., description="Name of the target branch")
    institute_type: str = Field(..., description="E.g., NIT, IIIT, GFTI")
    category: str = Field(..., description="Candidate category (e.g., OPEN, OBC-NCL)")
    quota: str = Field(..., description="Domicile quota (e.g., OS, HS)")
    seat_pool: str = Field(..., description="Gender Neutral or Female-Only")
    counselling_body: str = Field("JoSAA", description="JoSAA or CSAB")
    year: int = Field(2024, description="Target year for prediction")
    round_number: int = Field(6, description="Target counselling round")

class BatchPredictionRequest(BaseModel):
    predictions: List[PredictionRequest] = Field(..., max_length=50)

class SHAPExplanation(BaseModel):
    top_positive_features: Dict[str, float]
    top_negative_features: Dict[str, float]
    human_summary: str

class PredictionResponse(BaseModel):
    predicted_closing_rank: int
    user_rank: int
    admission_probability: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="Safe, Target, or Reach")
    explanation: Optional[SHAPExplanation] = None

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]

class CollegeRecommendation(BaseModel):
    college_name: str
    branch_name: str
    institute_type: str
    predicted_closing_rank: int
    match_type: str = Field(..., description="Safe, Target, or Dream")

class RecommendationResponse(BaseModel):
    user_rank: int
    safe_colleges: List[CollegeRecommendation]
    target_colleges: List[CollegeRecommendation]
    dream_colleges: List[CollegeRecommendation]
