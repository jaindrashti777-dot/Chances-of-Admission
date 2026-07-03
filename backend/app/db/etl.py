"""
ETL Pipeline: josaa_cutoffs_2021_2023.csv → SQLite
===================================================
Extract → Transform → Load

Populates all tables in dependency order:
  1. counselling_body (reference)
  2. category         (reference)
  3. quota            (reference)
  4. college          (entity)
  5. branch           (entity)
  6. college_branch   (join)
  7. historical_cutoff (fact)

Idempotent: safe to re-run. Uses get-or-create for all reference rows.
"""

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.cutoff import (
    CounsellingBody, Category, Quota, HistoricalCutoff,
)
from backend.app.models.college import College, Branch, CollegeBranch

logger = logging.getLogger(__name__)

DATA_PATH = Path("ml/data/raw/josaa_cutoffs_2021_2023.csv")


# ── helpers ────────────────────────────────────────────────────────────────

def _get_or_create(db: Session, model, **kwargs):
    """Return existing row or create a new one; returns (instance, created)."""
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    instance = model(**kwargs)
    db.add(instance)
    db.flush()          # assigns id without full commit
    return instance, True


def _state_for(college_name: str, df: pd.DataFrame) -> str:
    """Look up the state for a college from the enriched CSV."""
    rows = df[df["college_name"] == college_name]
    if rows.empty:
        return "Unknown"
    return rows.iloc[0]["state"] if "state" in df.columns else "Unknown"


# ── main ETL ───────────────────────────────────────────────────────────────

def run_etl(db: Session, data_path: Path = DATA_PATH) -> dict:
    """
    Full ETL. Returns a summary dict with row counts.
    """
    if not data_path.exists():
        logger.warning(
            f"Dataset not found at {data_path}. "
            "Falling back to legacy raw_data.csv."
        )
        data_path = Path("ml/data/raw/raw_data.csv")

    if not data_path.exists():
        logger.error("No dataset found. Skipping ETL.")
        return {"status": "skipped", "reason": "no data file"}

    logger.info(f"Loading dataset from {data_path} …")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df):,} rows, {df['college_name'].nunique()} colleges.")

    # ── Phase 1: Reference tables ──────────────────────────────────────────

    body_cache: dict[str, CounsellingBody] = {}
    for body_name in df["counselling_body"].dropna().unique():
        obj, _ = _get_or_create(db, CounsellingBody, name=str(body_name))
        body_cache[body_name] = obj

    cat_cache: dict[str, Category] = {}
    for cat_name in df["category"].dropna().unique():
        obj, _ = _get_or_create(db, Category, name=str(cat_name))
        cat_cache[cat_name] = obj

    quota_cache: dict[str, Quota] = {}
    for quota_name in df["quota"].dropna().unique():
        obj, _ = _get_or_create(db, Quota, name=str(quota_name))
        quota_cache[quota_name] = obj

    db.commit()
    logger.info("Reference tables populated.")

    # ── Phase 2: Colleges and Branches ────────────────────────────────────

    college_cache: dict[str, College] = {}
    for _, grp in df.groupby("college_name"):
        row = grp.iloc[0]
        college_name   = str(row["college_name"])
        institute_type = str(row["institute_type"])
        state          = str(row["state"]) if "state" in grp.columns else "Unknown"

        existing = db.query(College).filter_by(name=college_name).first()
        if existing:
            college_cache[college_name] = existing
        else:
            obj = College(
                name=college_name,
                state=state,
                institute_type=institute_type,
            )
            db.add(obj)
            db.flush()
            college_cache[college_name] = obj

    branch_cache: dict[str, Branch] = {}
    for branch_name in df["branch_name"].dropna().unique():
        obj, _ = _get_or_create(db, Branch, name=str(branch_name))
        branch_cache[branch_name] = obj

    db.commit()
    logger.info(
        f"Colleges: {len(college_cache)}, Branches: {len(branch_cache)}"
    )

    # ── Phase 3: College–Branch join ──────────────────────────────────────

    cb_seen: set[tuple[int, int]] = set()
    for _, row in df[["college_name", "branch_name"]].drop_duplicates().iterrows():
        c_id = college_cache[row["college_name"]].id
        b_id = branch_cache[row["branch_name"]].id
        key  = (c_id, b_id)
        if key in cb_seen:
            continue
        existing = db.query(CollegeBranch).filter_by(
            college_id=c_id, branch_id=b_id
        ).first()
        if not existing:
            db.add(CollegeBranch(college_id=c_id, branch_id=b_id))
        cb_seen.add(key)

    db.commit()
    logger.info(f"College–Branch links: {len(cb_seen)}")

    # ── Phase 4: Historical Cutoffs ───────────────────────────────────────

    inserted = 0
    skipped  = 0

    for chunk_start in range(0, len(df), 5_000):
        chunk = df.iloc[chunk_start : chunk_start + 5_000]

        for _, row in chunk.iterrows():
            c_id  = college_cache[row["college_name"]].id
            b_id  = branch_cache[row["branch_name"]].id
            cat_id  = cat_cache[row["category"]].id
            quot_id = quota_cache[row["quota"]].id
            body_id = body_cache[row["counselling_body"]].id

            existing = db.query(HistoricalCutoff).filter_by(
                college_id          = c_id,
                branch_id           = b_id,
                counselling_body_id = body_id,
                category_id         = cat_id,
                quota_id            = quot_id,
                seat_pool           = row["seat_pool"],
                year                = int(row["year"]),
                round_number        = int(row["round_number"]),
            ).first()

            if existing:
                skipped += 1
                continue

            db.add(HistoricalCutoff(
                college_id          = c_id,
                branch_id           = b_id,
                counselling_body_id = body_id,
                category_id         = cat_id,
                quota_id            = quot_id,
                seat_pool           = str(row["seat_pool"]),
                year                = int(row["year"]),
                round_number        = int(row["round_number"]),
                opening_rank        = int(row["opening_rank"]) if pd.notna(row["opening_rank"]) else None,
                closing_rank        = int(row["closing_rank"]) if pd.notna(row["closing_rank"]) else None,
            ))
            inserted += 1

        db.commit()
        logger.info(
            f"  … {min(chunk_start + 5000, len(df)):,}/{len(df):,} rows processed"
        )

    summary = {
        "status":     "ok",
        "rows_read":  len(df),
        "inserted":   inserted,
        "skipped":    skipped,
        "colleges":   len(college_cache),
        "branches":   len(branch_cache),
    }
    logger.info(f"ETL complete: {summary}")
    return summary
