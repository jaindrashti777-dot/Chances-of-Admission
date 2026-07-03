#!/usr/bin/env python3
"""
Stage 01 — Data Source Manager
================================
Acquires JoSAA/CSAB cutoff data following strict tier hierarchy.

Tiers (in priority order):
    1. OFFICIAL  — Canonical source (manually placed CSV/Excel in data/raw/josaa/official/)
    2. KAGGLE    — Verified mirror (downloaded via Kaggle API)
    3. SYNTHETIC — Testing only (generated/copied from synthetic stubs)

Provenance tracking:
    Every acquisition writes a provenance.json alongside the raw file,
    recording the source tier, URL/path, timestamp, row count, and SHA-256.

Usage:
    python data/pipeline/01_acquire.py --year 2023
    python data/pipeline/01_acquire.py --year all
    python data/pipeline/01_acquire.py --strategy official --year 2025
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths & Constants
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
RAW_JOSAA = ROOT / "data" / "raw" / "josaa"
RAW_CSAB  = ROOT / "data" / "raw" / "csab"
OFFICIAL_DIR = RAW_JOSAA / "official"

SOURCE_OFFICIAL = "OFFICIAL"
SOURCE_KAGGLE   = "KAGGLE"
SOURCE_SYNTHETIC= "SYNTHETIC"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline.01_acquire")

KAGGLE_DATASETS = {
    2023: "akshaydattatraykhare/jee-advanced-2023-josaa-cutoff",
    2024: "himanshurawat789/josaa-cutoff-2024",
}

SYNTHETIC_STUB = ROOT / "ml" / "data" / "raw" / "josaa_cutoffs_2021_2023.csv"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def write_provenance(dest_dir: Path, year: int, source_tier: str, source_detail: str, row_count: int, notes: str = "") -> None:
    prov = {
        "year": year,
        "source_tier": source_tier,
        "source_detail": source_detail,
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "notes": notes,
    }
    csv_files = list(dest_dir.glob("*.csv"))
    if csv_files:
        prov["sha256"] = sha256_of_file(csv_files[0])
        prov["filename"] = csv_files[0].name
        
    prov_path = dest_dir / "provenance.json"
    prov_path.write_text(json.dumps(prov, indent=2))
    log.info(f"Provenance [{source_tier}] written → {prov_path}")


# ---------------------------------------------------------------------------
# Strategy 1: Official Data
# ---------------------------------------------------------------------------

def try_official(year: int) -> bool:
    """Attempt to load official data from data/raw/josaa/official/."""
    if not OFFICIAL_DIR.exists():
        return False
        
    # Look for a CSV matching the year
    matches = list(OFFICIAL_DIR.glob(f"*{year}*.csv"))
    if not matches:
        return False
        
    primary = matches[0]
    df = pd.read_csv(primary)
    log.info(f"Official: loaded {len(df):,} rows from {primary.name}")
    
    dest = RAW_JOSAA / str(year)
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / f"josaa_{year}_raw.csv"
    
    # Copy file over
    shutil.copy2(primary, out_path)
    
    write_provenance(
        dest, year, SOURCE_OFFICIAL, f"local_file:{primary.name}", len(df),
        notes="Official data sourced from manual drop."
    )
    return True


# ---------------------------------------------------------------------------
# Strategy 2: Kaggle Mirror
# ---------------------------------------------------------------------------

def try_kaggle(year: int) -> bool:
    """Attempt to download from Kaggle verified mirror."""
    if year not in KAGGLE_DATASETS:
        return False

    if not shutil.which("kaggle"):
        log.warning("kaggle CLI not found — skipping Kaggle strategy")
        return False

    dataset = KAGGLE_DATASETS[year]
    dest = RAW_JOSAA / str(year)
    dest.mkdir(parents=True, exist_ok=True)

    log.info(f"Attempting Kaggle download: {dataset}")
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", dataset, "-p", str(dest), "--unzip"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log.warning(f"Kaggle download failed: {result.stderr}")
        return False

    csvs = list(dest.glob("*.csv"))
    if not csvs:
        return False

    primary = csvs[0]
    df = pd.read_csv(primary)
    
    # Standardize filename
    out_path = dest / f"josaa_{year}_raw.csv"
    if primary != out_path:
        primary.rename(out_path)
        
    log.info(f"Kaggle: loaded {len(df):,} rows from {dataset}")

    write_provenance(
        dest, year, SOURCE_KAGGLE, f"kaggle:{dataset}", len(df),
        notes="Verified mirror downloaded from Kaggle."
    )
    return True


# ---------------------------------------------------------------------------
# Strategy 3: Synthetic Data (Testing Only)
# ---------------------------------------------------------------------------

def use_synthetic_fallback(year: int) -> bool:
    """Generate synthetic fallback for testing. Must be excluded from prod training."""
    if not SYNTHETIC_STUB.exists():
        log.error("Synthetic stub dataset not found.")
        return False

    dest = RAW_JOSAA / str(year)
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / f"josaa_{year}_raw.csv"

    df_all = pd.read_csv(SYNTHETIC_STUB)
    df_year = df_all[df_all["year"] == year].copy()

    if df_year.empty:
        df_year = df_all[df_all["year"] == 2023].copy()
        df_year["year"] = year

    df_year.to_csv(out_path, index=False)

    write_provenance(
        dest, year, SOURCE_SYNTHETIC, "generator:synthetic_stub", len(df_year),
        notes="TESTING ONLY. Synthetic data explicitly flagged for exclusion in production."
    )

    log.warning(f"⚠  SYNTHETIC DATA written for year {year} ({len(df_year):,} rows).")
    return True


# ---------------------------------------------------------------------------
# Acquire a single year
# ---------------------------------------------------------------------------

def acquire_year(year: int, strategy: str = "auto") -> bool:
    log.info(f"{'='*60}")
    log.info(f"Acquiring JoSAA data for year {year} (strategy={strategy})")
    log.info(f"{'='*60}")

    dest = RAW_JOSAA / str(year)

    if strategy == "auto":
        if try_official(year):
            return True
        log.info("Official missing — trying Kaggle mirror...")
        if try_kaggle(year):
            return True
        log.info("Kaggle failed/missing — using synthetic fallback...")
        return use_synthetic_fallback(year)

    elif strategy == "official":
        return try_official(year)
    elif strategy == "kaggle":
        return try_kaggle(year)
    elif strategy == "synthetic":
        return use_synthetic_fallback(year)
    else:
        log.error(f"Unknown strategy: {strategy}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 01: Acquire JoSAA/CSAB raw cutoff data via Data Source Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--year", choices=["2023", "2024", "2025", "all"], default="all")
    parser.add_argument("--strategy", choices=["auto", "official", "kaggle", "synthetic"], default="auto")
    args = parser.parse_args()

    years = [2023, 2024, 2025] if args.year == "all" else [int(args.year)]
    results = {}

    for yr in years:
        success = acquire_year(yr, args.strategy)
        results[yr] = "OK" if success else "FAILED"

    log.info("\n" + "="*60)
    log.info("ACQUISITION SUMMARY")
    log.info("="*60)
    for yr, status in results.items():
        icon = "✅" if status == "OK" else "❌"
        log.info(f"  {icon} {yr}: {status}")

    if any(s == "FAILED" for s in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
