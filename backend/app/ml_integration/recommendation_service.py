from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

from backend.app.schemas.prediction import RecommendationResponse, CollegeRecommendation
from backend.app.models.cutoff import HistoricalCutoff
from backend.app.models.college import College, Branch

logger = logging.getLogger(__name__)

class RecommendationService:
    @staticmethod
    def get_recommendations(db: Session, user_rank: int, category_id: int, quota_id: int) -> RecommendationResponse:
        """
        Queries historical cutoffs from the database and categorizes them into Safe, Target, and Dream based on the user's rank.
        This avoids running ML predictions for thousands of colleges in real-time.
        """
        safe, target, dream = [], [], []
        
        # Simplified query: fetch cutoffs for the latest year matching user category/quota
        # In a real scenario, this would aggregate or use the ML model in batch offline.
        stmt = select(HistoricalCutoff, College, Branch).join(College).join(Branch).where(
            HistoricalCutoff.category_id == category_id,
            HistoricalCutoff.quota_id == quota_id,
            HistoricalCutoff.year == 2023 # Using previous year as heuristic
        ).limit(50)
        
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
            
            if user_rank <= closing_rank * 0.8:
                rec.match_type = "Safe"
                safe.append(rec)
            elif user_rank <= closing_rank * 1.05:
                rec.match_type = "Target"
                target.append(rec)
            elif user_rank <= closing_rank * 1.2:
                rec.match_type = "Dream"
                dream.append(rec)
                
        # Sort and limit
        safe = sorted(safe, key=lambda x: x.predicted_closing_rank)[:5]
        target = sorted(target, key=lambda x: x.predicted_closing_rank)[:5]
        dream = sorted(dream, key=lambda x: x.predicted_closing_rank, reverse=True)[:5]
        
        return RecommendationResponse(
            user_rank=user_rank,
            safe_colleges=safe,
            target_colleges=target,
            dream_colleges=dream
        )

recommendation_service = RecommendationService()
