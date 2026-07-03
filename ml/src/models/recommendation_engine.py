"""
Hybrid Recommendation Engine
==============================
Architecture: Rule Engine → Candidate Filter → ML Ranking → Tier Labels

NOT a black-box probability predictor.
Answers: "Given this student's profile, which colleges are realistically available?"

Input:
    student_rank   : int   — JEE Mains percentile-to-rank or direct rank
    category       : str   — OPEN | EWS | OBC-NCL | SC | ST | OPEN-PwD | ...
    gender         : str   — Male | Female
    home_state     : str   — State name (for HS quota eligibility)
    preferred_branch: str  — Optional branch filter
    preferred_type : list  — Optional institute type filter [NIT, IIIT, GFTI]
    year           : int   — Reference year for cutoffs (default: latest)

Output:
    List[RecommendationResult] sorted by likelihood:
        institute_name, branch_name, seat_pool, quota, recommendation_tier,
        round_6_closing_rank, rank_buffer, historical_trend
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
ROOT     = Path(__file__).resolve().parents[3]
MASTER   = ROOT / "data" / "master" / "master_dataset.csv"
FEATURES = ROOT / "data" / "training" / "features.csv"

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Recommendation tiers
# ---------------------------------------------------------------------------

TIERS = {
    "Very Likely":   "Historically well within your cutoff range. High chance of seat.",
    "Likely":        "Close to historical cutoff. Good chance if rank is consistent.",
    "Competitive":   "Slightly above historical cutoff. Possible in favorable rounds.",
    "Ambitious":     "Significantly above historical cutoff. Low probability.",
}

# Tier thresholds: rank_buffer = (closing_rank - student_rank) / closing_rank
# Positive buffer = student rank is BETTER than cutoff (safer)
# Negative buffer = student rank is WORSE than cutoff (risky)
TIER_THRESHOLDS = [
    ("Very Likely",  0.15),   # Student rank is 15%+ better than cutoff
    ("Likely",       0.0),    # Student rank is within 0–15% of cutoff
    ("Competitive", -0.20),   # Student rank is 0–20% worse than cutoff
    ("Ambitious",   -1.0),    # Student rank is 20%+ worse — still show it
]


@dataclass
class StudentProfile:
    student_rank:      int
    category:          str
    gender:            str               # "Male" | "Female"
    home_state:        str
    preferred_branch:  Optional[str] = None
    preferred_types:   list[str]     = field(default_factory=list)
    reference_year:    int           = 2025


@dataclass
class RecommendationResult:
    institute_name:       str
    branch_name:          str
    institute_type:       str
    institute_state:      str
    nirf_rank:            Optional[float]
    institute_tier:       str
    quota:                str
    seat_pool:            str
    category:             str
    round_6_closing_rank: int
    rank_buffer:          float          # positive = safer
    recommendation_tier:  str
    tier_description:     str
    historical_trend:     str           # tightening | relaxing | stable
    avg_3yr_closing:      Optional[float]
    counselling_body:     str


# ---------------------------------------------------------------------------
# Rule Engine — Stage 1
# ---------------------------------------------------------------------------

class RuleEngine:
    """
    Filters the master dataset to only the rows eligible for this student.

    Rules applied:
        1. Category match
        2. Seat pool match (Gender-Neutral always eligible; Female-Only only for Female)
        3. Quota eligibility (HS only if student's home_state == institute_state)
        4. Optional branch filter
        5. Optional institute type filter
        6. Only Round 6 cutoffs (most stable signal)
        7. Reference year (latest available)
    """

    def __init__(self, master_df: pd.DataFrame):
        self.df = master_df

    def filter(self, profile: StudentProfile) -> pd.DataFrame:
        df = self.df.copy()

        # R1: Category
        df = df[df["category"] == profile.category]
        log.debug(f"  After category filter ({profile.category}): {len(df):,} rows")

        # R2: Seat pool
        if profile.gender == "Female":
            # Female students can use both Gender-Neutral and Female-Only pools
            pass  # no filter needed
        else:
            # Male students can only use Gender-Neutral
            df = df[df["seat_pool"] == "Gender-Neutral"]
        log.debug(f"  After gender/pool filter: {len(df):,} rows")

        # R3: Quota — build eligible quotas for this student
        eligible_quotas = ["AI"]  # Always eligible for AI quota (IIITs)
        eligible_quotas.append("OS")  # Always eligible for Other State

        # HS quota: only if student's state == institute's state
        # We'll handle this at row level after join
        df = df[df["quota"].isin(["AI", "OS", "HS"])]

        # For HS rows: only keep if institute_state == student's home_state
        hs_mask = df["quota"] == "HS"
        home_state_match = df["institute_state"].str.lower() == profile.home_state.lower()
        df = df[~hs_mask | (hs_mask & home_state_match)]
        log.debug(f"  After quota/state filter: {len(df):,} rows")

        # R4: Round 6 only (final cutoff = most reliable for ranking)
        df = df[df["round_number"] == 6]
        log.debug(f"  After round 6 filter: {len(df):,} rows")

        # R5: Reference year — use latest available year's data
        available_years = sorted(df["year"].unique(), reverse=True)
        ref_year = profile.reference_year
        if ref_year not in available_years:
            ref_year = available_years[0]
        df = df[df["year"] == ref_year]
        log.debug(f"  After year filter ({ref_year}): {len(df):,} rows")

        # R6: Optional branch filter
        if profile.preferred_branch:
            df = df[df["branch_name"].str.lower() == profile.preferred_branch.lower()]
            log.debug(f"  After branch filter: {len(df):,} rows")

        # R7: Optional institute type filter
        if profile.preferred_types:
            df = df[df["institute_type"].isin(profile.preferred_types)]
            log.debug(f"  After type filter: {len(df):,} rows")

        return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# ML Ranker — Stage 2
# ---------------------------------------------------------------------------

class RankScorer:
    """
    Scores each candidate college using the features.csv data.

    Scoring components:
        1. rank_buffer   : How safe is the student vs. historical cutoff? (primary signal)
        2. trend_penalty : Is cutoff tightening? (negative adjustment)
        3. tier_bonus    : Higher-tier institutes get a small bonus for equal buffers
        4. consistency   : Lower std_closing_rank = more predictable = preferred

    This replaces the black-box ML model for Sprint 2.
    In Sprint 3, we'll replace this with a trained GradientBoosting ranker.
    """

    def __init__(self, features_df: pd.DataFrame):
        self.features = features_df

    def score(self, candidate_row: pd.Series, student_rank: int) -> dict:
        """Compute a composite score for one candidate program."""
        closing_rank = int(candidate_row["closing_rank"])
        institute    = candidate_row["institute_name"]
        branch       = candidate_row["branch_name"]
        category     = candidate_row["category"]
        quota        = candidate_row["quota"]
        seat_pool    = candidate_row["seat_pool"]

        # rank_buffer: positive = student is safer than cutoff
        rank_buffer = (closing_rank - student_rank) / closing_rank

        # Look up historical features
        feat_row = self.features[
            (self.features["institute_name"] == institute) &
            (self.features["branch_name"] == branch) &
            (self.features["category"] == category) &
            (self.features["quota"] == quota) &
            (self.features["seat_pool"] == seat_pool)
        ]

        trend         = "stable"
        avg_3yr       = None
        consistency   = 0.0
        tier_encoded  = 4

        if not feat_row.empty:
            row = feat_row.iloc[0]
            trend       = row.get("demand_trend", "stable")
            avg_3yr     = row.get("avg_closing_rank", None)
            yoy_pct     = row.get("yoy_rank_change_pct", 0.0)
            consistency = float(row.get("std_closing_rank", 0.0))
            tier_encoded = int(row.get("institute_tier_encoded", 4))

            # Trend adjustment: if cutoff is tightening (lower rank needed each year),
            # penalize slightly — next year may be harder
            if trend == "tightening" and yoy_pct:
                rank_buffer += yoy_pct / 200  # small penalty

        # Composite score (higher = better recommendation)
        # Weights: safety (70%) + tier quality (20%) + consistency (10%)
        tier_bonus    = (5 - tier_encoded) * 0.05  # Tier1 gets +0.2, Tier4 gets 0
        consistency_bonus = -consistency / 50000     # Lower std = more bonus
        composite = (rank_buffer * 0.70) + tier_bonus + consistency_bonus

        return {
            "rank_buffer":   rank_buffer,
            "composite":     composite,
            "trend":         trend,
            "avg_3yr":       avg_3yr,
            "tier_encoded":  tier_encoded,
        }

    def assign_tier(self, rank_buffer: float) -> tuple[str, str]:
        for tier_name, threshold in TIER_THRESHOLDS:
            if rank_buffer >= threshold:
                return tier_name, TIERS[tier_name]
        return "Ambitious", TIERS["Ambitious"]


# ---------------------------------------------------------------------------
# Recommendation Engine — Main Entry Point
# ---------------------------------------------------------------------------

class RecommendationEngine:

    def __init__(self):
        if not MASTER.exists():
            raise FileNotFoundError(
                f"master_dataset.csv not found. Run the pipeline first:\n"
                f"  python data/pipeline/run_pipeline.py --all --include-synthetic"
            )
        self.master   = pd.read_csv(MASTER)
        self.features = pd.read_csv(FEATURES) if FEATURES.exists() else pd.DataFrame()
        self.rule_engine = RuleEngine(self.master)
        self.ranker      = RankScorer(self.features)
        log.info(
            f"RecommendationEngine loaded: {len(self.master):,} cutoff rows, "
            f"{len(self.features):,} feature rows"
        )

    def recommend(
        self,
        profile: StudentProfile,
        top_n:   int = 50,
        include_ambitious: bool = True,
    ) -> list[RecommendationResult]:
        """
        Full pipeline: filter → score → rank → label → return.
        """
        # Stage 1: Rule-based filtering
        candidates = self.rule_engine.filter(profile)
        log.info(f"Rule engine: {len(candidates):,} candidate programs after filtering")

        if candidates.empty:
            log.warning("No candidates found after rule filtering.")
            return []

        # Stage 2: Score each candidate
        results_with_scores = []
        for _, row in candidates.iterrows():
            scores = self.ranker.score(row, profile.student_rank)
            tier, desc = self.ranker.assign_tier(scores["rank_buffer"])

            if not include_ambitious and tier == "Ambitious":
                continue

            body = row.get("counselling_body", "JoSAA")

            result = RecommendationResult(
                institute_name=       row["institute_name"],
                branch_name=          row["branch_name"],
                institute_type=       row.get("institute_type", ""),
                institute_state=      row.get("institute_state", ""),
                nirf_rank=            row.get("nirf_rank"),
                institute_tier=       row.get("institute_tier", "Tier 4"),
                quota=                row["quota"],
                seat_pool=            row["seat_pool"],
                category=             row["category"],
                round_6_closing_rank= int(row["closing_rank"]),
                rank_buffer=          round(scores["rank_buffer"], 4),
                recommendation_tier=  tier,
                tier_description=     desc,
                historical_trend=     scores["trend"],
                avg_3yr_closing=      scores["avg_3yr"],
                counselling_body=     body,
            )
            results_with_scores.append((scores["composite"], result))

        # Stage 3: Sort by composite score (best first)
        results_with_scores.sort(key=lambda x: x[0], reverse=True)
        results_sorted = [r for _, r in results_with_scores]

        return results_sorted[:top_n]

    def summary(self, results: list[RecommendationResult]) -> dict:
        """Return a structured summary of recommendations."""
        by_tier = {}
        for r in results:
            by_tier.setdefault(r.recommendation_tier, []).append(r)

        return {
            "total": len(results),
            "by_tier": {tier: len(lst) for tier, lst in by_tier.items()},
            "very_likely":  by_tier.get("Very Likely",  []),
            "likely":       by_tier.get("Likely",       []),
            "competitive":  by_tier.get("Competitive",  []),
            "ambitious":    by_tier.get("Ambitious",    []),
        }


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%H:%M:%S")

    engine = RecommendationEngine()

    # Example student: SC Female, Rajasthan, Rank 9200
    profile = StudentProfile(
        student_rank=9200,
        category="SC",
        gender="Female",
        home_state="Rajasthan",
        preferred_branch=None,
        preferred_types=[],
        reference_year=2025,
    )

    print(f"\n{'='*70}")
    print(f"  STUDENT PROFILE")
    print(f"{'='*70}")
    print(f"  Rank:     {profile.student_rank:,}")
    print(f"  Category: {profile.category}")
    print(f"  Gender:   {profile.gender}")
    print(f"  State:    {profile.home_state}")
    print(f"  Year:     {profile.reference_year}")

    results = engine.recommend(profile, top_n=30, include_ambitious=False)
    summary = engine.summary(results)

    print(f"\n{'='*70}")
    print(f"  RECOMMENDATIONS ({summary['total']} programs found)")
    print(f"{'='*70}")
    print(f"  Very Likely:  {summary['by_tier'].get('Very Likely',  0)}")
    print(f"  Likely:       {summary['by_tier'].get('Likely',       0)}")
    print(f"  Competitive:  {summary['by_tier'].get('Competitive',  0)}")

    print(f"\n{'─'*70}")
    print(f"  {'VERY LIKELY'}")
    print(f"{'─'*70}")
    for r in summary["very_likely"][:10]:
        print(
            f"  {r.institute_tier:<8} | {r.institute_name:<40} | "
            f"{r.branch_name[:30]:<30} | "
            f"Rank {r.round_6_closing_rank:>7,} | "
            f"Buffer {r.rank_buffer:+.2%} | {r.quota} {r.seat_pool}"
        )

    print(f"\n{'─'*70}")
    print(f"  {'LIKELY'}")
    print(f"{'─'*70}")
    for r in summary["likely"][:10]:
        print(
            f"  {r.institute_tier:<8} | {r.institute_name:<40} | "
            f"{r.branch_name[:30]:<30} | "
            f"Rank {r.round_6_closing_rank:>7,} | "
            f"Buffer {r.rank_buffer:+.2%} | {r.quota} {r.seat_pool}"
        )
