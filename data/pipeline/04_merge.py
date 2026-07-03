#!/usr/bin/env python3
"""
Stage 04 — Master Dataset Builder
===================================
Merges all validated per-year CSVs into a single authoritative dataset,
enriched with institute and branch metadata.

Operations:
    1. Load josaa_2023.csv, josaa_2024.csv, josaa_2025.csv
    2. Concatenate into a single DataFrame
    3. Left-join with institutes.csv (adds NIRF rank, city, state)
    4. Left-join with branches.csv (adds degree, duration, department)
    5. Add derived columns (institute_tier, is_home_state_eligible)
    6. Final column ordering, sort, and de-dup check
    7. Write data/master/master_dataset.csv

Output schema (28 columns):
    counselling_body, institute_type, institute_name, institute_state,
    institute_city, nirf_rank, branch_name, branch_code, degree,
    duration_years, department, core_or_emerging, category,
    quota, seat_pool, year, round_number, opening_rank, closing_rank,
    institute_tier, rank_spread, [provenance metadata]

Usage:
    python data/pipeline/04_merge.py
    python data/pipeline/04_merge.py --include-synthetic  # include synthetic-flagged data
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
ROOT      = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
MASTER    = ROOT / "data" / "master"
METADATA  = ROOT / "data" / "raw" / "metadata"
REPORTS   = ROOT / "data" / "reports"

MASTER.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline.04_merge")

# ---------------------------------------------------------------------------
# NIRF Tier mapping (based on NIRF 2024 Engineering rankings)
# Tier 1: rank 1-50   |  Tier 2: 51-100  |  Tier 3: 101-200  |  Tier 4: 200+
# ---------------------------------------------------------------------------
def assign_institute_tier(nirf_rank) -> str:
    try:
        rank = int(nirf_rank)
        if rank <= 50:
            return "Tier 1"
        elif rank <= 100:
            return "Tier 2"
        elif rank <= 200:
            return "Tier 3"
        else:
            return "Tier 4"
    except (ValueError, TypeError):
        return "Tier 4"  # unranked institutes go to Tier 4


def get_year_source(year: int) -> str:
    prov_path = ROOT / "data" / "raw" / "josaa" / str(year) / "provenance.json"
    if prov_path.exists():
        prov = json.loads(prov_path.read_text())
        return prov.get("source_tier", "UNKNOWN")
    return "UNKNOWN"


def load_years(include_synthetic: bool) -> pd.DataFrame:
    dfs = []
    for year in [2023, 2024, 2025]:
        path = PROCESSED / f"josaa_{year}.csv"
        if not path.exists():
            log.warning(f"Year {year}: processed file not found — skipping")
            continue

        source_tier = get_year_source(year)
        if source_tier == "SYNTHETIC" and not include_synthetic:
            log.warning(f"Year {year}: data is SYNTHETIC — skipping (use --include-synthetic to include)")
            continue

        df = pd.read_csv(path)
        df["data_source"] = source_tier
        log.info(f"  Loaded {year}: {len(df):,} rows [{source_tier}]")
        dfs.append(df)

    if not dfs:
        raise RuntimeError(
            "No processed data found. Run 01_acquire.py and 02_clean.py first.\n"
            "If all data is synthetic and you want to use it, pass --include-synthetic."
        )

    combined = pd.concat(dfs, ignore_index=True)
    log.info(f"  Combined: {len(combined):,} rows from {len(dfs)} year(s)")
    return combined


def load_institute_metadata() -> pd.DataFrame:
    path = METADATA / "institutes.csv"
    if not path.exists():
        log.warning("institutes.csv not found — NIRF ranks and city data will be missing")
        return pd.DataFrame()
    meta = pd.read_csv(path)
    log.info(f"  Loaded institute metadata: {len(meta)} institutes")
    return meta


def load_branch_metadata() -> pd.DataFrame:
    path = METADATA / "branches.csv"
    if not path.exists():
        log.warning("branches.csv not found — branch metadata will be missing")
        return pd.DataFrame()
    meta = pd.read_csv(path)
    log.info(f"  Loaded branch metadata: {len(meta)} branches")
    return meta


def build_master(include_synthetic: bool) -> pd.DataFrame:
    log.info("\n" + "="*60)
    log.info("Stage 04: Building master_dataset.csv")
    log.info("="*60)

    # ── 1. Load all years ────────────────────────────────────────────────
    log.info("\n[1/5] Loading processed year files...")
    df = load_years(include_synthetic)

    # ── 2. Join institute metadata ───────────────────────────────────────
    log.info("\n[2/5] Joining institute metadata...")
    inst_meta = load_institute_metadata()
    if not inst_meta.empty:
        # Select only the columns we want to add
        inst_cols = [
            "institute_name", "state", "city", "established",
            "nirf_rank_2024", "naac_grade", "autonomous"
        ]
        inst_cols = [c for c in inst_cols if c in inst_meta.columns]
        inst_subset = inst_meta[inst_cols].copy()
        inst_subset.rename(columns={
            "state": "institute_state",
            "city":  "institute_city",
            "nirf_rank_2024": "nirf_rank",
        }, inplace=True)

        df = df.merge(inst_subset, on="institute_name", how="left")
        matched = df["institute_state"].notna().sum()
        log.info(f"  Matched {matched:,}/{len(df):,} rows to institute metadata")
    else:
        df["institute_state"] = None
        df["institute_city"]  = None
        df["nirf_rank"]       = None
        df["naac_grade"]      = None
        df["established"]     = None
        df["autonomous"]      = None

    # ── 3. Join branch metadata ──────────────────────────────────────────
    log.info("\n[3/5] Joining branch metadata...")
    branch_meta = load_branch_metadata()
    if not branch_meta.empty:
        branch_cols = ["branch_name", "branch_code", "degree", "duration_years", "department", "core_or_emerging"]
        branch_cols = [c for c in branch_cols if c in branch_meta.columns]
        branch_subset = branch_meta[branch_cols].copy()

        df = df.merge(branch_subset, on="branch_name", how="left")
        matched = df["branch_code"].notna().sum()
        log.info(f"  Matched {matched:,}/{len(df):,} rows to branch metadata")
    else:
        df["branch_code"]     = None
        df["degree"]          = None
        df["duration_years"]  = None
        df["department"]      = None
        df["core_or_emerging"] = None

    # ── 4. Derived columns ───────────────────────────────────────────────
    log.info("\n[4/5] Computing derived columns...")

    # institute_tier: from NIRF rank
    df["institute_tier"] = df["nirf_rank"].map(assign_institute_tier)

    # rank_spread: closing - opening (indicates demand tightness)
    df["rank_spread"] = df["closing_rank"] - df["opening_rank"]

    # round_6_proxy: whether this row is the final-round cutoff (most stable for ML)
    df["is_final_round"] = (df["round_number"] == 6).astype(int)

    log.info(f"  Tier distribution:\n{df['institute_tier'].value_counts().to_string()}")

    # ── 5. Final ordering and output ─────────────────────────────────────
    log.info("\n[5/5] Finalizing and writing master dataset...")

    # Canonical column order
    final_columns = [
        # Primary identifiers
        "counselling_body", "institute_type", "institute_name",
        # Institute metadata
        "institute_state", "institute_city", "nirf_rank", "naac_grade",
        "established", "autonomous", "institute_tier",
        # Branch metadata
        "branch_name", "branch_code", "degree", "duration_years",
        "department", "core_or_emerging",
        # Cutoff data
        "category", "quota", "seat_pool",
        "year", "round_number",
        "opening_rank", "closing_rank",
        # Derived
        "rank_spread", "is_final_round",
        # Provenance
        "data_source",
    ]

    # Keep only columns that exist (in case metadata join missed some)
    final_columns = [c for c in final_columns if c in df.columns]
    df = df[final_columns]

    # Sort for readability
    df = df.sort_values(
        ["year", "institute_type", "institute_name", "branch_name",
         "category", "quota", "seat_pool", "round_number"],
        ascending=True
    ).reset_index(drop=True)

    # Final dedup check
    n_before = len(df)
    key_cols = [
        "institute_name", "branch_name", "category",
        "quota", "seat_pool", "year", "round_number"
    ]
    df = df.drop_duplicates(subset=key_cols, keep="last")
    if n_before != len(df):
        log.warning(f"  Removed {n_before - len(df):,} late-stage duplicates")

    # Write
    out_path = MASTER / "master_dataset.csv"
    df.to_csv(out_path, index=False)

    # Summary statistics
    log.info(f"\n{'='*60}")
    log.info("MASTER DATASET SUMMARY")
    log.info(f"{'='*60}")
    log.info(f"  Output:         {out_path}")
    log.info(f"  Total rows:     {len(df):,}")
    log.info(f"  File size:      {out_path.stat().st_size / 1024 / 1024:.1f} MB")
    log.info(f"  Years:          {sorted(df['year'].unique())}")
    log.info(f"  Institutes:     {df['institute_name'].nunique():,} unique")
    log.info(f"  Branches:       {df['branch_name'].nunique():,} unique")
    log.info(f"  Categories:     {sorted(df['category'].unique())}")
    log.info(f"  Rank range:     {df['closing_rank'].min():,} – {df['closing_rank'].max():,}")

    real_rows = (df["data_source"] == "REAL").sum()
    synth_rows = (df["data_source"] == "SYNTHETIC").sum()
    log.info(f"  Data quality:   {real_rows:,} real rows, {synth_rows:,} synthetic rows")

    if synth_rows > 0:
        log.warning(
            f"\n  ⚠  {synth_rows:,} rows are SYNTHETIC. "
            "Replace synthetic source data before production use."
        )

    log.info(f"\n  Sample (5 rows):")
    log.info(df.sample(min(5, len(df)), random_state=42)[
        ["institute_name", "branch_name", "category", "quota",
         "seat_pool", "year", "round_number", "closing_rank"]
    ].to_string(index=False))

    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 04: Build master_dataset.csv")
    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Include synthetic/placeholder data (clearly flagged in output)",
    )
    args = parser.parse_args()

    build_master(include_synthetic=args.include_synthetic)


if __name__ == "__main__":
    main()
