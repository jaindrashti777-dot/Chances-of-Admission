"""
Pydantic schemas for the Analytics API endpoints.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class YearlyRecord(BaseModel):
    year:         int
    closing_rank: int
    opening_rank: Optional[int] = None


class ProgramResult(BaseModel):
    college_name:       str
    branch_name:        str
    institute_type:     str
    state:              str

    # Historical stats
    last_year:          int
    last_year_closing:  int
    mean_closing:       float
    min_closing:        int
    max_closing:        int
    std_closing:        float
    years_of_data:      int
    yearly_records:     List[YearlyRecord]

    # Trend
    trend_direction:    str = Field(..., description="tightening | stable | relaxing")
    trend_pct:          float = Field(..., description="YoY closing rank change %")

    # Classification
    match_type:         str = Field(..., description="Safe | Target | Reach")
    margin_ranks:       int = Field(..., description="user_rank minus last_year_closing")


class RankMatchResponse(BaseModel):
    user_rank:      int
    category:       str
    quota:          str
    seat_pool:      str
    safe:           List[ProgramResult]
    target:         List[ProgramResult]
    reach:          List[ProgramResult]
    total_programs: int
    data_years:     List[int]


class TrendPoint(BaseModel):
    year:         int
    closing_rank: int
    opening_rank: Optional[int] = None


class TrendResponse(BaseModel):
    college_name:  str
    branch_name:   str
    category:      str
    quota:         str
    seat_pool:     str
    trend:         List[TrendPoint]
    mean_closing:  float
    min_closing:   int
    max_closing:   int
    years_of_data: int


class FilterOptions(BaseModel):
    colleges:   List[str]
    branches:   List[str]
    categories: List[str]
    quotas:     List[str]
    seat_pools: List[str]
    years:      List[int]


class DatasetSummary(BaseModel):
    total_records:   int
    colleges:        int
    branches:        int
    years_covered:   List[int]
    data_source:     str
    rounds_per_year: int
