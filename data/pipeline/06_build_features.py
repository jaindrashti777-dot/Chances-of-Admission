#!/usr/bin/env python3
"""
Stage 06 — Feature Engineering
================================
Transforms the master dataset into ML-ready features for the ranking model.

Design philosophy:
    The ML model does NOT see raw cutoff rows.
    It sees student-context features derived from historical data.

Features engineered:
    From historical cutoffs (per institute+branch+category+quota+pool):
        - round_6_closing_rank    : Final round cutoff (most stable signal)
        - round_1_closing_rank    : First round cutoff (tightest signal)
        - rank_tightening_ratio   : round_1 / round_6 (how much cutoff moved)
        - closing_rank_lag1       : Previous year's closing rank
        - closing_rank_lag2       : 2 years ago closing rank
        - yoy_rank_change         : Percentage change year-over-year
        - demand_trend            : 'tightening' | 'relaxing' | 'stable'
        - avg_closing_rank_3yr    : 3-year average closing rank
        - rank_std_3yr            : Standard deviation over 3 years (consistency)

    Student-context features (computed at inference time):
        - rank_buffer             : (closing_rank - student_rank) / closing_rank
        - rank_percentile         : Student rank percentile in their year

    Institute metadata:
        - nirf_rank
        - institute_tier_encoded  : Tier 1=1, Tier 2=2, Tier 3=3, Tier 4=4
        - is_iiit                 : boolean
        - is_nit                  : boolean

    Branch metadata:
        - is_cse_branch           : CSE, IT, DSAI, AIML — boolean
        - is_core_branch          : based on core_or_emerging

    Category/Quota:
        - category_encoded        : ordinal encoding
        - is_home_state_quota     : HS vs OS/AI

Output:
    data/training/features.csv  — Wide table, one row per (institute, branch,
                                  category, quota, pool, year=latest)

Usage:
    python data/pipeline/06_build_features.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
ROOT     = Path(__file__).resolve().parents[2]
MASTER   = ROOT / "data" / "master" / "master_dataset.csv"
TRAINING = ROOT / "data" / "training"
TRAINING.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] — %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("pipeline.06_features")

# ---------------------------------------------------------------------------
# Encodings
# ---------------------------------------------------------------------------

CATEGORY_ORDER = {
    "OPEN": 0, "EWS": 1, "OBC-NCL": 2, "SC": 3, "ST": 4,
    "OPEN-PwD": 5, "EWS-PwD": 6, "OBC-NCL-PwD": 7, "SC-PwD": 8, "ST-PwD": 9,
}

TIER_ORDER = {"Tier 1": 1, "Tier 2": 2, "Tier 3": 3, "Tier 4": 4}

CSE_BRANCHES = {
    "Computer Science and Engineering",
    "Information Technology",
    "Data Science and Artificial Intelligence",
    "Artificial Intelligence and Machine Learning",
    "Computer Science and Engineering (Artificial Intelligence)",
    "Computer Science and Engineering (Cyber Security)",
    "Internet of Things",
    "Electronics and Computer Engineering",
    "Mathematics and Computing",
}


def build_features(allow_synthetic: bool = False) -> pd.DataFrame:
    if not MASTER.exists():
        raise FileNotFoundError(f"master_dataset.csv not found at {MASTER}")

    log.info("Loading master dataset...")
    df = pd.read_csv(MASTER)
    
    # Filter synthetic data
    if "data_source" in df.columns:
        synth_count = (df["data_source"] == "SYNTHETIC").sum()
        if synth_count > 0:
            if not allow_synthetic:
                log.warning(f"Dropping {synth_count:,} SYNTHETIC rows (use --allow-synthetic-training to include)")
                df = df[df["data_source"] != "SYNTHETIC"]
            else:
                log.warning(f"Including {synth_count:,} SYNTHETIC rows for training due to --allow-synthetic-training flag")
    
    if df.empty:
        log.error("Dataset is empty after filtering! Cannot build features.")
        return pd.DataFrame()

    log.info(f"  {len(df):,} rows loaded for feature engineering")

    # ── 1. Extract Round 6 (final cutoff) as the base signal ────────────
    log.info("\n[1/6] Extracting Round 6 cutoffs as base signal...")
    r6 = df[df["round_number"] == 6].copy()
    r1 = df[df["round_number"] == 1].copy()
    log.info(f"  Round 6 rows: {len(r6):,}  |  Round 1 rows: {len(r1):,}")

    # Key for aggregation
    key = ["institute_name", "branch_name", "category", "quota", "seat_pool"]

    # ── 2. Build pivot: one row per (institute, branch, cat, quota, pool) ─
    log.info("\n[2/6] Pivoting to per-program features...")

    # Round 6 closing rank per year
    r6_pivot = r6.pivot_table(
        index=key,
        columns="year",
        values="closing_rank",
        aggfunc="first",
    ).reset_index()

    # Rename year columns
    year_cols = sorted([c for c in r6_pivot.columns if isinstance(c, int)])
    for yr in year_cols:
        r6_pivot.rename(columns={yr: f"cr_{yr}"}, inplace=True)

    # Round 1 closing rank per year (optional)
    r1_pivot = r1.pivot_table(
        index=key,
        columns="year",
        values="closing_rank",
        aggfunc="first",
    ).reset_index()
    for yr in year_cols:
        if yr in r1_pivot.columns:
            r1_pivot.rename(columns={yr: f"cr_r1_{yr}"}, inplace=True)

    features = r6_pivot.merge(r1_pivot, on=key, how="left")
    log.info(f"  Pivoted: {len(features):,} program combinations")

    # ── 3. Derived rank features ─────────────────────────────────────────
    log.info("\n[3/6] Engineering rank-based features...")

    cr_cols = [f"cr_{yr}" for yr in year_cols if f"cr_{yr}" in features.columns]

    # 3-year average (handle missing years gracefully)
    features["avg_closing_rank"] = features[cr_cols].mean(axis=1)
    features["std_closing_rank"] = features[cr_cols].std(axis=1).fillna(0)

    # Year-over-year change (most recent two years)
    if len(year_cols) >= 2:
        latest = year_cols[-1]
        prev   = year_cols[-2]
        cr_latest = f"cr_{latest}"
        cr_prev   = f"cr_{prev}"
        if cr_latest in features.columns and cr_prev in features.columns:
            features["yoy_rank_change_pct"] = (
                (features[cr_latest] - features[cr_prev]) / features[cr_prev].replace(0, np.nan)
            ) * 100
            features["demand_trend"] = features["yoy_rank_change_pct"].map(
                lambda x: "tightening" if pd.notna(x) and x < -2
                          else ("relaxing" if pd.notna(x) and x > 2 else "stable")
            )
        else:
            features["yoy_rank_change_pct"] = np.nan
            features["demand_trend"] = "unknown"

    # Round tightening ratio (how much did rank move from R1 to R6?)
    for yr in year_cols:
        cr_r1 = f"cr_r1_{yr}"
        cr_r6 = f"cr_{yr}"
        if cr_r1 in features.columns and cr_r6 in features.columns:
            features[f"tightening_ratio_{yr}"] = (
                features[cr_r1] / features[cr_r6].replace(0, np.nan)
            )

    # Latest year closing rank (primary ML target feature)
    latest_yr_col = f"cr_{year_cols[-1]}" if year_cols else None
    if latest_yr_col and latest_yr_col in features.columns:
        features["round_6_closing_rank"] = features[latest_yr_col]
    else:
        features["round_6_closing_rank"] = features["avg_closing_rank"]

    # ── 4. Join metadata back ─────────────────────────────────────────────
    log.info("\n[4/6] Adding metadata features...")

    # Institute metadata from master
    inst_meta = (
        df[["institute_name", "institute_type", "nirf_rank", "institute_tier",
            "institute_state"]]
        .drop_duplicates("institute_name")
    )
    features = features.merge(inst_meta, on="institute_name", how="left")

    # Branch metadata from master
    branch_meta = (
        df[["branch_name", "branch_code", "department", "core_or_emerging"]]
        .drop_duplicates("branch_name")
    )
    features = features.merge(branch_meta, on="branch_name", how="left")

    # ── 5. Encode categorical features ────────────────────────────────────
    log.info("\n[5/6] Encoding categorical features...")

    features["category_encoded"]      = features["category"].map(CATEGORY_ORDER).fillna(-1).astype(int)
    features["institute_tier_encoded"] = features["institute_tier"].map(TIER_ORDER).fillna(4).astype(int)
    features["is_nit"]                = (features["institute_type"] == "NIT").astype(int)
    features["is_iiit"]               = (features["institute_type"] == "IIIT").astype(int)
    features["is_gfti"]               = (features["institute_type"] == "GFTI").astype(int)
    features["is_home_state_quota"]   = (features["quota"] == "HS").astype(int)
    features["is_female_pool"]        = (features["seat_pool"] == "Female-Only").astype(int)
    features["is_cse_branch"]         = features["branch_name"].isin(CSE_BRANCHES).astype(int)
    features["is_core_branch"]        = (features["core_or_emerging"] == "Core").astype(int)

    # ── 6. Final column ordering and output ───────────────────────────────
    log.info("\n[6/6] Writing features.csv...")

    # Drop rows with no closing rank data at all
    before = len(features)
    features = features.dropna(subset=["round_6_closing_rank"])
    log.info(f"  Dropped {before - len(features):,} rows with no closing rank")

    # Canonical output
    priority_cols = [
        # Identifiers
        "institute_name", "branch_name", "category", "quota", "seat_pool",
        # Primary rank signal
        "round_6_closing_rank",
        # Historical ranks by year
        *[f"cr_{yr}" for yr in year_cols if f"cr_{yr}" in features.columns],
        # Statistical features
        "avg_closing_rank", "std_closing_rank",
        "yoy_rank_change_pct", "demand_trend",
        # Metadata
        "institute_type", "institute_state", "nirf_rank",
        "institute_tier", "institute_tier_encoded",
        "branch_code", "department", "core_or_emerging",
        # Binary features
        "is_nit", "is_iiit", "is_gfti",
        "is_home_state_quota", "is_female_pool",
        "is_cse_branch", "is_core_branch",
        # Encoded
        "category_encoded",
    ]
    # Add any tightening ratio cols
    tightening_cols = [c for c in features.columns if c.startswith("tightening_ratio_")]
    priority_cols.extend(tightening_cols)

    final_cols = [c for c in priority_cols if c in features.columns]
    features = features[final_cols]

    out_path = TRAINING / "features.csv"
    features.to_csv(out_path, index=False)

    log.info(f"\n{'='*60}")
    log.info("FEATURE ENGINEERING SUMMARY")
    log.info(f"{'='*60}")
    log.info(f"  Output:              {out_path}")
    log.info(f"  Feature rows:        {len(features):,}")
    log.info(f"  Feature columns:     {len(features.columns)}")
    log.info(f"  File size:           {out_path.stat().st_size / 1024:.1f} KB")
    log.info(f"  Columns: {features.columns.tolist()}")
    log.info(f"\n  Sample:")
    log.info(features.head(3).to_string())

    return features


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 06: Build ML Features")
    parser.add_argument("--allow-synthetic-training", action="store_true", 
                        help="Allow SYNTHETIC data to be used in the feature set")
    args = parser.parse_args()
    build_features(allow_synthetic=args.allow_synthetic_training)
