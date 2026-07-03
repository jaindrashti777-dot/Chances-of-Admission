from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

from backend.app.schemas.prediction import RecommendationResponse, CollegeRecommendation
from backend.app.models.cutoff import HistoricalCutoff
from backend.app.models.college import College, Branch

logger = logging.getLogger(__name__)

class CollegeRecommender:
    @staticmethod
    def get_recommendations(db: Session, user_rank: int, category_name: str, quota_name: str) -> RecommendationResponse:
        """
        Queries historical cutoffs from the database and categorizes them into Safe, Target, and Dream based on the user's rank.
        This avoids running ML predictions for thousands of colleges in real-time.
        """
        safe, target, dream = [], [], []
        
        # We query for cutoffs for the latest available year (e.g., 2023)
        from backend.app.models.cutoff import Category, Quota
        
        # Fetch colleges where the user rank is within a reasonable range
        # user_rank * 0.8 => closing rank needed is at least 0.8x user rank (Dream)
        # user_rank * 3.0 => closing rank is up to 3x user rank (Very Safe)
        min_closing_rank = user_rank * 0.75
        max_closing_rank = user_rank * 3.0
        
        stmt = select(HistoricalCutoff, College, Branch).join(College).join(Branch)\
            .join(Category, HistoricalCutoff.category_id == Category.id)\
            .join(Quota, HistoricalCutoff.quota_id == Quota.id)\
            .where(
                Category.name == category_name,
                Quota.name == quota_name,
                HistoricalCutoff.year == 2023,
                HistoricalCutoff.round_number == 6, # Use last round
                HistoricalCutoff.closing_rank >= min_closing_rank,
                HistoricalCutoff.closing_rank <= max_closing_rank
        )
        
        results = db.execute(stmt).all()
        
        for cutoff, college, branch in results:
            closing_rank = cutoff.closing_rank
            if not closing_rank:
                continue
                
            rec = CollegeRecommendation(
                college_name=college.name,
                branch_name=branch.name,
                institute_type=college.institute_type,
                predicted_closing_rank=closing_rank,
                match_type=""
            )
            
            # Categorize based on proximity to closing rank
            if user_rank <= closing_rank * 0.85:
                rec.match_type = "Safe"
                safe.append(rec)
            elif user_rank <= closing_rank * 1.05:
                rec.match_type = "Target"
                target.append(rec)
            elif user_rank <= closing_rank * 1.25:
                rec.match_type = "Dream"
                dream.append(rec)
                
        # Sort and limit
        safe = sorted(safe, key=lambda x: x.predicted_closing_rank)[:5]
        target = sorted(target, key=lambda x: abs(x.predicted_closing_rank - user_rank))[:5] # Closest targets
        dream = sorted(dream, key=lambda x: x.predicted_closing_rank, reverse=True)[:5]
        
        return RecommendationResponse(
            user_rank=user_rank,
            safe_colleges=safe,
            target_colleges=target,
            dream_colleges=dream
        )
        
    @staticmethod
    def get_historical_trend(db: Session, college_name: str, branch_name: str, category_name: str, quota_name: str):
        from backend.app.models.cutoff import Category, Quota
        from backend.app.schemas.prediction import TrendResponse, TrendDataPoint
        
        stmt = select(HistoricalCutoff.year, HistoricalCutoff.closing_rank)\
            .join(College, HistoricalCutoff.college_id == College.id)\
            .join(Branch, HistoricalCutoff.branch_id == Branch.id)\
            .join(Category, HistoricalCutoff.category_id == Category.id)\
            .join(Quota, HistoricalCutoff.quota_id == Quota.id)\
            .where(
                College.name == college_name,
                Branch.name == branch_name,
                Category.name == category_name,
                Quota.name == quota_name,
                HistoricalCutoff.round_number == 6 # Trend based on final round
            ).order_by(HistoricalCutoff.year.asc())
            
        results = db.execute(stmt).all()
        
        seen_years = set()
        trend_data = []
        for year, closing_rank in results:
            if year not in seen_years and closing_rank:
                seen_years.add(year)
                trend_data.append(TrendDataPoint(year=year, closing_rank=closing_rank))
                
        return TrendResponse(
            college_name=college_name,
            branch_name=branch_name,
            category=category_name,
            quota=quota_name,
            trend=trend_data
        )

college_recommender = CollegeRecommender()

