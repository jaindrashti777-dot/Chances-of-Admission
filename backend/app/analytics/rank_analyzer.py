"""
Rank Analyzer — Core analytics engine
======================================
Given a student's rank + category + quota + seat_pool, queries
3 years of historical JoSAA cutoff data and returns a ranked list
of all programs classified as Safe / Target / Reach.

Classification is based on the **statistical envelope** of Round 6
closing ranks across all available years, not any ML model.

Safe   → user_rank ≤ min_closing_rank × 0.85   (well inside best year)
Target → user_rank ≤ mean_closing_rank × 1.10  (within typical range)
Reach  → user_rank ≤ max_closing_rank × 1.25   (only possible in best year)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.college import College, Branch
from backend.app.models.cutoff import Category, HistoricalCutoff, Quota

logger = logging.getLogger(__name__)


# ── result data classes ────────────────────────────────────────────────────

@dataclass
class YearlyRecord:
    year: int
    closing_rank: int
    opening_rank: Optional[int] = None


@dataclass
class ProgramAnalysis:
    """Full statistical picture for one (college, branch) combination."""
    college_name:       str
    branch_name:        str
    institute_type:     str
    state:              str

    # Historical data
    yearly_records:     List[YearlyRecord]
    last_year:          int          # most recent year available
    last_year_closing:  int          # Round-6 closing rank for most recent year
    mean_closing:       float        # average across all years
    min_closing:        int          # best (most competitive) year
    max_closing:        int          # worst (least competitive) year
    std_closing:        float        # standard deviation — indicates volatility

    # Derived
    trend_direction:    str          # "tightening" | "stable" | "relaxing"
    trend_pct:          float        # year-over-year change % (last two years)
    years_of_data:      int

    # Classification
    match_type:         str          # "Safe" | "Target" | "Reach"
    margin_ranks:       int          # user_rank - last_year_closing (negative = safer)


@dataclass
class RankMatchResponse:
    user_rank:      int
    category:       str
    quota:          str
    seat_pool:      str
    safe:           List[ProgramAnalysis] = field(default_factory=list)
    target:         List[ProgramAnalysis] = field(default_factory=list)
    reach:          List[ProgramAnalysis] = field(default_factory=list)
    total_programs: int = 0
    data_years:     List[int] = field(default_factory=list)


# ── analyzer ───────────────────────────────────────────────────────────────

class RankAnalyzer:
    """
    Queries historical cutoff data from the DB and produces a
    classified, annotated list of programs for a given student profile.
    """

    # Only use the final round (Round 6) for ranking decisions.
    FINAL_ROUND = 6

    def analyze(
        self,
        db:        Session,
        user_rank: int,
        category:  str,
        quota:     str,
        seat_pool: str,
        limit:     int = 200,
    ) -> RankMatchResponse:
        """
        Main entry point. Returns a RankMatchResponse with classified programs.
        """
        # ── Step 1: fetch Round-6 cutoffs for matching profile ──────────
        rows = self._fetch_cutoffs(db, category, quota, seat_pool)

        if not rows:
            logger.warning(
                f"No historical data found for category={category}, "
                f"quota={quota}, seat_pool={seat_pool}"
            )
            return RankMatchResponse(
                user_rank=user_rank, category=category,
                quota=quota, seat_pool=seat_pool,
            )

        # ── Step 2: group by (college, branch) and compute stats ─────────
        from collections import defaultdict
        groups: dict[tuple, list] = defaultdict(list)
        for row in rows:
            key = (row.college_id, row.branch_id)
            groups[key].append(row)

        analyses: List[ProgramAnalysis] = []
        all_years: set[int] = set()

        for (college_id, branch_id), cutoffs in groups.items():
            analysis = self._compute_stats(user_rank, cutoffs)
            if analysis is None:
                continue
            analyses.append(analysis)
            for yr in analysis.yearly_records:
                all_years.add(yr.year)

        # ── Step 3: classify ──────────────────────────────────────────────
        safe, target, reach = [], [], []
        for a in analyses:
            if a.match_type == "Safe":
                safe.append(a)
            elif a.match_type == "Target":
                target.append(a)
            elif a.match_type == "Reach":
                reach.append(a)

        # Sort: Safe → ascending last-year closing (easiest first makes no sense;
        # we want the best college the student can get → sort by competitiveness)
        safe.sort(key=lambda a: a.last_year_closing)
        target.sort(key=lambda a: a.last_year_closing)
        reach.sort(key=lambda a: a.last_year_closing)

        # Apply limit across each bucket proportionally
        bucket_limit = limit // 3
        safe   = safe[:bucket_limit]
        target = target[:bucket_limit]
        reach  = reach[:bucket_limit]

        return RankMatchResponse(
            user_rank=user_rank,
            category=category,
            quota=quota,
            seat_pool=seat_pool,
            safe=safe,
            target=target,
            reach=reach,
            total_programs=len(safe) + len(target) + len(reach),
            data_years=sorted(all_years),
        )

    # ── internal ──────────────────────────────────────────────────────────

    def _fetch_cutoffs(
        self, db: Session, category: str, quota: str, seat_pool: str
    ) -> list:
        stmt = (
            select(HistoricalCutoff)
            .join(Category, HistoricalCutoff.category_id == Category.id)
            .join(Quota,    HistoricalCutoff.quota_id    == Quota.id)
            .where(
                Category.name            == category,
                Quota.name               == quota,
                HistoricalCutoff.seat_pool == seat_pool,
                HistoricalCutoff.round_number == self.FINAL_ROUND,
                HistoricalCutoff.closing_rank.isnot(None),
            )
        )
        return db.execute(stmt).scalars().all()

    def _compute_stats(
        self, user_rank: int, cutoffs: list
    ) -> Optional[ProgramAnalysis]:
        if not cutoffs:
            return None

        # Pull college/branch info from first cutoff (they all share the same)
        first = cutoffs[0]
        college: College = first.college
        branch:  Branch  = first.branch

        if not college or not branch:
            return None

        # Build year→closing map (deduplicate, take min if multiple rounds)
        year_map: dict[int, int] = {}
        for c in cutoffs:
            if c.closing_rank is None:
                continue
            yr = c.year
            if yr not in year_map or c.closing_rank < year_map[yr]:
                year_map[yr] = c.closing_rank

        if not year_map:
            return None

        yearly_records = [
            YearlyRecord(year=yr, closing_rank=cr)
            for yr, cr in sorted(year_map.items())
        ]

        closing_ranks = [yr.closing_rank for yr in yearly_records]
        last_year = max(year_map)
        last_yr_cr = year_map[last_year]
        mean_cr   = float(sum(closing_ranks)) / len(closing_ranks)
        min_cr    = min(closing_ranks)
        max_cr    = max(closing_ranks)
        std_cr    = _std(closing_ranks)

        # Trend: compare last two years if available
        sorted_years = sorted(year_map.keys())
        if len(sorted_years) >= 2:
            prev_cr   = year_map[sorted_years[-2]]
            trend_pct = (last_yr_cr - prev_cr) / prev_cr * 100
            if trend_pct < -3:
                trend_dir = "tightening"   # closing rank fell → harder to get
            elif trend_pct > 3:
                trend_dir = "relaxing"     # closing rank rose → easier to get
            else:
                trend_dir = "stable"
        else:
            trend_pct = 0.0
            trend_dir = "stable"

        # Classification based on statistical envelope
        if user_rank <= int(min_cr * 0.85):
            match_type = "Safe"
        elif user_rank <= int(mean_cr * 1.10):
            match_type = "Target"
        elif user_rank <= int(max_cr * 1.25):
            match_type = "Reach"
        else:
            return None   # Out of range entirely

        return ProgramAnalysis(
            college_name      = college.name,
            branch_name       = branch.name,
            institute_type    = college.institute_type,
            state             = college.state,
            yearly_records    = yearly_records,
            last_year         = last_year,
            last_year_closing = last_yr_cr,
            mean_closing      = round(mean_cr, 1),
            min_closing       = min_cr,
            max_closing       = max_cr,
            std_closing       = round(std_cr, 1),
            trend_direction   = trend_dir,
            trend_pct         = round(trend_pct, 1),
            years_of_data     = len(yearly_records),
            match_type        = match_type,
            margin_ranks      = user_rank - last_yr_cr,
        )

    def get_trend(
        self,
        db:          Session,
        college_name: str,
        branch_name:  str,
        category:     str,
        quota:        str,
        seat_pool:    str = "Gender-Neutral",
    ) -> Optional[dict]:
        """
        Returns year-by-year Round-6 closing rank trend for one program.
        """
        stmt = (
            select(HistoricalCutoff.year, HistoricalCutoff.closing_rank,
                   HistoricalCutoff.opening_rank)
            .join(College,  HistoricalCutoff.college_id  == College.id)
            .join(Branch,   HistoricalCutoff.branch_id   == Branch.id)
            .join(Category, HistoricalCutoff.category_id == Category.id)
            .join(Quota,    HistoricalCutoff.quota_id    == Quota.id)
            .where(
                College.name             == college_name,
                Branch.name              == branch_name,
                Category.name            == category,
                Quota.name               == quota,
                HistoricalCutoff.seat_pool   == seat_pool,
                HistoricalCutoff.round_number == self.FINAL_ROUND,
                HistoricalCutoff.closing_rank.isnot(None),
            )
            .order_by(HistoricalCutoff.year.asc())
        )
        rows = db.execute(stmt).all()

        if not rows:
            return None

        trend_points = [
            {"year": yr, "closing_rank": cr, "opening_rank": op}
            for yr, cr, op in rows
        ]

        closing_ranks = [p["closing_rank"] for p in trend_points]
        return {
            "college_name":   college_name,
            "branch_name":    branch_name,
            "category":       category,
            "quota":          quota,
            "seat_pool":      seat_pool,
            "trend":          trend_points,
            "mean_closing":   round(sum(closing_ranks) / len(closing_ranks), 1),
            "min_closing":    min(closing_ranks),
            "max_closing":    max(closing_ranks),
            "years_of_data":  len(closing_ranks),
        }

    def get_filter_options(self, db: Session) -> dict:
        """Returns all valid filter values from the database (for frontend dropdowns)."""
        colleges  = [r[0] for r in db.query(College.name).order_by(College.name).all()]
        branches  = [r[0] for r in db.query(Branch.name).order_by(Branch.name).all()]
        categories= [r[0] for r in db.query(Category.name).order_by(Category.name).all()]
        quotas    = [r[0] for r in db.query(Quota.name).order_by(Quota.name).all()]
        seat_pools= (
            db.query(HistoricalCutoff.seat_pool)
            .distinct()
            .order_by(HistoricalCutoff.seat_pool)
            .all()
        )
        years = (
            db.query(HistoricalCutoff.year)
            .distinct()
            .order_by(HistoricalCutoff.year)
            .all()
        )
        return {
            "colleges":   colleges,
            "branches":   branches,
            "categories": categories,
            "quotas":     quotas,
            "seat_pools": [r[0] for r in seat_pools],
            "years":      [r[0] for r in years],
        }

    def get_dataset_summary(self, db: Session) -> dict:
        """Returns provenance/statistics about the loaded dataset."""
        total = db.query(func.count(HistoricalCutoff.id)).scalar() or 0
        colleges = db.query(func.count(College.id)).scalar() or 0
        branches = db.query(func.count(Branch.id)).scalar() or 0
        years = [
            r[0] for r in
            db.query(HistoricalCutoff.year).distinct().order_by(HistoricalCutoff.year).all()
        ]
        return {
            "total_records":  total,
            "colleges":       colleges,
            "branches":       branches,
            "years_covered":  years,
            "data_source":    "JoSAA / CSAB Historical Counselling Data",
            "rounds_per_year": 6,
        }


# ── helpers ────────────────────────────────────────────────────────────────

def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return variance ** 0.5


rank_analyzer = RankAnalyzer()
