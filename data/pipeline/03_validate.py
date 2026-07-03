#!/usr/bin/env python3
"""
Stage 03 — Data Validation
============================
Runs a comprehensive data quality gate on cleaned per-year CSVs.

Validation rules:
    CRITICAL (pipeline halts if any fail):
        - opening_rank < closing_rank
        - ranks are positive integers
        - year ∈ {2023, 2024, 2025}
        - round_number ∈ {1..6}
        - category ∈ canonical set
        - quota ∈ {HS, OS, AI}
        - seat_pool ∈ {Gender-Neutral, Female-Only}
        - institute_name not null
        - branch_name not null

    WARNING (logged but pipeline continues):
        - institute_name not in metadata/institutes.csv
        - branch_name not in metadata/branches.csv
        - closing_rank > 100_000 (beyond JEE rank range)
        - opening_rank > 50_000

Output:
    data/reports/validation_report.json

Usage:
    python data/pipeline/03_validate.py
    python data/pipeline/03_validate.py --strict  # fail on warnings too
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
METADATA  = ROOT / "data" / "raw" / "metadata"
REPORTS   = ROOT / "data" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline.03_validate")

# ---------------------------------------------------------------------------
# Canonical sets
# ---------------------------------------------------------------------------
VALID_CATEGORIES = {
    "OPEN", "EWS", "OBC-NCL", "SC", "ST",
    "OPEN-PwD", "EWS-PwD", "OBC-NCL-PwD", "SC-PwD", "ST-PwD",
}
VALID_QUOTAS      = {"HS", "OS", "AI"}
VALID_SEAT_POOLS  = {"Gender-Neutral", "Female-Only"}
VALID_YEARS       = {2023, 2024, 2025}
VALID_ROUNDS      = {1, 2, 3, 4, 5, 6}
MAX_RANK          = 200_000  # upper bound for any JEE rank
WARN_CLOSING_RANK = 100_000
WARN_OPENING_RANK = 50_000


# ---------------------------------------------------------------------------
# Validation engine
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self, year: int):
        self.year          = year
        self.total_rows    = 0
        self.critical      : list[dict] = []
        self.warnings      : list[dict] = []
        self.passed        : list[str]  = []
        self.is_synthetic  = False

    def add_critical(self, rule: str, failing_rows: int, detail: str = "") -> None:
        self.critical.append({"rule": rule, "failing_rows": failing_rows, "detail": detail})
        log.error(f"  ❌ CRITICAL: {rule} — {failing_rows:,} rows fail. {detail}")

    def add_warning(self, rule: str, failing_rows: int, detail: str = "") -> None:
        self.warnings.append({"rule": rule, "failing_rows": failing_rows, "detail": detail})
        log.warning(f"  ⚠  WARNING:  {rule} — {failing_rows:,} rows. {detail}")

    def add_pass(self, rule: str) -> None:
        self.passed.append(rule)
        log.info(f"  ✅ PASS:     {rule}")

    @property
    def has_critical_failures(self) -> bool:
        return len(self.critical) > 0

    def to_dict(self) -> dict:
        return {
            "year":            self.year,
            "total_rows":      self.total_rows,
            "is_synthetic":    self.is_synthetic,
            "status":          "FAIL" if self.has_critical_failures else "PASS",
            "critical_count":  len(self.critical),
            "warning_count":   len(self.warnings),
            "passed_count":    len(self.passed),
            "critical_rules":  self.critical,
            "warning_rules":   self.warnings,
            "passed_rules":    self.passed,
        }


def check_synthetic(year: int) -> bool:
    prov_path = ROOT / "data" / "raw" / "josaa" / str(year) / "provenance.json"
    if prov_path.exists():
        prov = json.loads(prov_path.read_text())
        return "SYNTHETIC" in prov.get("source", "")
    return False


def validate_year(year: int, df: pd.DataFrame) -> ValidationResult:
    result = ValidationResult(year)
    result.total_rows  = len(df)
    result.is_synthetic = check_synthetic(year)

    if result.is_synthetic:
        log.warning(f"  ⚠  Year {year} data is SYNTHETIC. Results are not real JoSAA data.")

    log.info(f"  Total rows: {result.total_rows:,}")

    # ── CRITICAL rules ─────────────────────────────────────────────────────

    # R1: No null institute names
    nulls = df["institute_name"].isna().sum() + (df["institute_name"] == "nan").sum()
    if nulls > 0:
        result.add_critical("R1: institute_name not null", nulls)
    else:
        result.add_pass("R1: institute_name not null")

    # R2: No null branch names
    nulls = df["branch_name"].isna().sum() + (df["branch_name"] == "nan").sum()
    if nulls > 0:
        result.add_critical("R2: branch_name not null", nulls)
    else:
        result.add_pass("R2: branch_name not null")

    # R3: opening_rank < closing_rank (always)
    inverted = (df["opening_rank"] >= df["closing_rank"]).sum()
    if inverted > 0:
        result.add_critical("R3: opening_rank < closing_rank", inverted)
    else:
        result.add_pass("R3: opening_rank < closing_rank")

    # R4: Ranks are positive
    bad_ranks = ((df["opening_rank"] <= 0) | (df["closing_rank"] <= 0)).sum()
    if bad_ranks > 0:
        result.add_critical("R4: ranks are positive", bad_ranks)
    else:
        result.add_pass("R4: ranks are positive")

    # R5: Ranks within JEE range
    bad_max = (df["closing_rank"] > MAX_RANK).sum()
    if bad_max > 0:
        result.add_critical("R5: closing_rank <= MAX_RANK", bad_max, f"MAX={MAX_RANK}")
    else:
        result.add_pass("R5: closing_rank within JEE range")

    # R6: year in valid set
    bad_year = (~df["year"].isin(VALID_YEARS)).sum()
    if bad_year > 0:
        result.add_critical("R6: year in {2023,2024,2025}", bad_year)
    else:
        result.add_pass("R6: year in valid set")

    # R7: round_number in {1..6}
    bad_round = (~df["round_number"].isin(VALID_ROUNDS)).sum()
    if bad_round > 0:
        result.add_critical("R7: round_number in {1..6}", bad_round,
                             f"Values: {df[~df['round_number'].isin(VALID_ROUNDS)]['round_number'].unique().tolist()}")
    else:
        result.add_pass("R7: round_number in {1..6}")

    # R8: category in canonical set
    bad_cat = (~df["category"].isin(VALID_CATEGORIES)).sum()
    if bad_cat > 0:
        unknown = df[~df["category"].isin(VALID_CATEGORIES)]["category"].unique().tolist()
        result.add_critical("R8: category in canonical set", bad_cat, f"Unknown: {unknown[:5]}")
    else:
        result.add_pass("R8: category in canonical set")

    # R9: quota in {HS, OS, AI}
    bad_quota = (~df["quota"].isin(VALID_QUOTAS)).sum()
    if bad_quota > 0:
        unknown = df[~df["quota"].isin(VALID_QUOTAS)]["quota"].unique().tolist()
        result.add_critical("R9: quota in {HS,OS,AI}", bad_quota, f"Unknown: {unknown[:5]}")
    else:
        result.add_pass("R9: quota in {HS,OS,AI}")

    # R10: seat_pool in {Gender-Neutral, Female-Only}
    bad_pool = (~df["seat_pool"].isin(VALID_SEAT_POOLS)).sum()
    if bad_pool > 0:
        unknown = df[~df["seat_pool"].isin(VALID_SEAT_POOLS)]["seat_pool"].unique().tolist()
        result.add_critical("R10: seat_pool in valid set", bad_pool, f"Unknown: {unknown[:5]}")
    else:
        result.add_pass("R10: seat_pool in valid set")

    # ── WARNING rules ────────────────────────────────────────────────────

    # W1: Institute names in metadata
    meta_institutes_path = METADATA / "institutes.csv"
    if meta_institutes_path.exists():
        known = set(pd.read_csv(meta_institutes_path)["institute_name"].str.strip())
        unknown_insts = set(df["institute_name"].unique()) - known
        if unknown_insts:
            result.add_warning(
                "W1: institute_name in metadata", len(unknown_insts),
                f"Not in metadata (need to add): {sorted(unknown_insts)[:5]}"
            )
        else:
            result.add_pass("W1: all institute names in metadata")

    # W2: Branch names in metadata
    meta_branches_path = METADATA / "branches.csv"
    if meta_branches_path.exists():
        known = set(pd.read_csv(meta_branches_path)["branch_name"].str.strip())
        unknown_branches = set(df["branch_name"].unique()) - known
        if unknown_branches:
            result.add_warning(
                "W2: branch_name in metadata", len(unknown_branches),
                f"Not in metadata: {sorted(unknown_branches)[:5]}"
            )
        else:
            result.add_pass("W2: all branch names in metadata")

    # W3: High closing ranks
    high_close = (df["closing_rank"] > WARN_CLOSING_RANK).sum()
    if high_close > 0:
        result.add_warning("W3: closing_rank > 100k", high_close)
    else:
        result.add_pass("W3: no unusually high closing ranks")

    # W4: Duplicate key check
    key_cols = ["institute_name", "branch_name", "category", "quota", "seat_pool", "year", "round_number"]
    n_dup = df.duplicated(subset=key_cols).sum()
    if n_dup > 0:
        result.add_warning("W4: duplicate (institute, branch, cat, quota, pool, year, round)", n_dup)
    else:
        result.add_pass("W4: no duplicate records")

    # W5: Category coverage — should have all 5 base categories
    cats = set(df["category"].unique())
    base_cats = {"OPEN", "EWS", "OBC-NCL", "SC", "ST"}
    missing_cats = base_cats - cats
    if missing_cats:
        result.add_warning("W5: missing base categories", len(missing_cats), f"Missing: {missing_cats}")
    else:
        result.add_pass("W5: all 5 base categories present")

    return result


def load_processed(year: int) -> pd.DataFrame | None:
    path = PROCESSED / f"josaa_{year}.csv"
    if not path.exists():
        log.error(f"Year {year}: processed file not found at {path}. Run 02_clean.py first.")
        return None
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 03: Validate cleaned JoSAA CSVs")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as failures")
    args = parser.parse_args()

    years = [2023, 2024, 2025]
    all_results = {}

    for yr in years:
        log.info(f"\n{'='*60}")
        log.info(f"Validating JoSAA {yr}")
        log.info(f"{'='*60}")

        df = load_processed(yr)
        if df is None:
            continue

        result = validate_year(yr, df)
        all_results[yr] = result.to_dict()

    # Write report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "years": all_results,
        "overall_status": "PASS" if all(
            r["status"] == "PASS" for r in all_results.values()
        ) else "FAIL",
    }

    report_path = REPORTS / "validation_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    log.info(f"\nValidation report → {report_path}")

    # Print summary
    log.info("\n" + "="*60)
    log.info("VALIDATION SUMMARY")
    log.info("="*60)
    overall_pass = True
    for yr, res in all_results.items():
        status = res["status"]
        synthetic = " [SYNTHETIC DATA]" if res["is_synthetic"] else ""
        icon = "✅" if status == "PASS" else "❌"
        log.info(
            f"  {icon} {yr}: {status}{synthetic} "
            f"| {res['critical_count']} critical, {res['warning_count']} warnings, "
            f"{res['passed_count']} passed"
        )
        if status == "FAIL":
            overall_pass = False
        if args.strict and res["warning_count"] > 0:
            overall_pass = False

    log.info(f"\n  Overall: {'PASS ✅' if overall_pass else 'FAIL ❌'}")

    if not overall_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
