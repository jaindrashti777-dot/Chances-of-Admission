"""
Analysis API endpoints
=======================
Data-driven endpoints backed by 3 years of real JoSAA historical cutoff data.
No ML black box — pure statistical analysis of historical closing ranks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.analytics.rank_analyzer import rank_analyzer
from backend.app.schemas.analysis import (
    RankMatchResponse,
    TrendResponse,
    FilterOptions,
    DatasetSummary,
    ProgramResult,
    YearlyRecord,
)

router = APIRouter()


# ── /rank-match ────────────────────────────────────────────────────────────

@router.get(
    "/rank-match",
    response_model=RankMatchResponse,
    summary="Rank-Based College Matching",
    description=(
        "Returns all engineering programs classified as Safe, Target, or Reach "
        "based on 3 years of historical JoSAA/CSAB closing ranks. "
        "Classification uses the statistical envelope (min/mean/max) of Round-6 "
        "final closing ranks — not ML magic."
    ),
)
def rank_match(
    user_rank: int  = Query(..., gt=0, le=500_000, description="Candidate's JEE rank"),
    category:  str  = Query(..., description="e.g. OPEN, EWS, OBC-NCL, SC, ST"),
    quota:     str  = Query(..., description="e.g. OS, HS, AI"),
    seat_pool: str  = Query("Gender-Neutral", description="Gender-Neutral or Female-Only"),
    limit:     int  = Query(150, ge=10, le=300, description="Max results per bucket"),
    db: Session = Depends(get_db),
):
    result = rank_analyzer.analyze(
        db=db,
        user_rank=user_rank,
        category=category,
        quota=quota,
        seat_pool=seat_pool,
        limit=limit,
    )

    def _to_schema(a) -> ProgramResult:
        return ProgramResult(
            college_name      = a.college_name,
            branch_name       = a.branch_name,
            institute_type    = a.institute_type,
            state             = a.state,
            last_year         = a.last_year,
            last_year_closing = a.last_year_closing,
            mean_closing      = a.mean_closing,
            min_closing       = a.min_closing,
            max_closing       = a.max_closing,
            std_closing       = a.std_closing,
            years_of_data     = a.years_of_data,
            yearly_records    = [
                YearlyRecord(year=yr.year, closing_rank=yr.closing_rank,
                             opening_rank=yr.opening_rank)
                for yr in a.yearly_records
            ],
            trend_direction   = a.trend_direction,
            trend_pct         = a.trend_pct,
            match_type        = a.match_type,
            margin_ranks      = a.margin_ranks,
        )

    return RankMatchResponse(
        user_rank      = result.user_rank,
        category       = result.category,
        quota          = result.quota,
        seat_pool      = result.seat_pool,
        safe           = [_to_schema(a) for a in result.safe],
        target         = [_to_schema(a) for a in result.target],
        reach          = [_to_schema(a) for a in result.reach],
        total_programs = result.total_programs,
        data_years     = result.data_years,
    )


# ── /trend ────────────────────────────────────────────────────────────────

@router.get(
    "/trend",
    response_model=TrendResponse,
    summary="Historical Cutoff Trend",
    description=(
        "Returns year-by-year Round-6 closing and opening ranks for a specific "
        "college + branch + category + quota combination."
    ),
)
def historical_trend(
    college_name: str = Query(..., description="Full college name"),
    branch_name:  str = Query(..., description="Branch name"),
    category:     str = Query(..., description="e.g. OPEN"),
    quota:        str = Query(..., description="e.g. OS"),
    seat_pool:    str = Query("Gender-Neutral"),
    db: Session = Depends(get_db),
):
    result = rank_analyzer.get_trend(
        db=db,
        college_name=college_name,
        branch_name=branch_name,
        category=category,
        quota=quota,
        seat_pool=seat_pool,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {college_name} / {branch_name} / {category} / {quota}",
        )

    return TrendResponse(**result)


# ── /filters ─────────────────────────────────────────────────────────────

@router.get(
    "/filters",
    response_model=FilterOptions,
    summary="Available Filter Values",
    description="Returns all valid filter values from the database for frontend dropdowns.",
)
def filter_options(db: Session = Depends(get_db)):
    opts = rank_analyzer.get_filter_options(db)
    return FilterOptions(**opts)


# ── /summary ─────────────────────────────────────────────────────────────

@router.get(
    "/summary",
    response_model=DatasetSummary,
    summary="Dataset Summary",
    description="Returns provenance metadata about the loaded historical dataset.",
)
def dataset_summary(db: Session = Depends(get_db)):
    summary = rank_analyzer.get_dataset_summary(db)
    return DatasetSummary(**summary)
