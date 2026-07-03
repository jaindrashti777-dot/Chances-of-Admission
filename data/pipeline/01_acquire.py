#!/usr/bin/env python3
"""
Stage 01 — Data Acquisition
============================
Downloads or references official JoSAA/CSAB cutoff data for 2023, 2024, 2025.

Acquisition Strategy (in priority order):
    1. Kaggle API   — Download pre-scraped JoSAA datasets via kaggle CLI
    2. Web Scraper  — Scrape josaa.nic.in directly (fallback)
    3. Manual       — User places raw CSVs manually (documented below)

Provenance tracking:
    Every acquisition writes a provenance.json alongside the raw file,
    recording the source URL, timestamp, row count, and SHA-256 checksum.

Usage:
    python data/pipeline/01_acquire.py --year 2023
    python data/pipeline/01_acquire.py --year 2024
    python data/pipeline/01_acquire.py --year all
    python data/pipeline/01_acquire.py --strategy scrape --year 2025
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]          # project root
RAW_JOSAA = ROOT / "data" / "raw" / "josaa"
RAW_CSAB  = ROOT / "data" / "raw" / "csab"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline.01_acquire")

# ---------------------------------------------------------------------------
# Kaggle dataset references
# Known public JoSAA datasets on Kaggle that contain real historical data
# ---------------------------------------------------------------------------
KAGGLE_DATASETS = {
    2023: "akshaydattatraykhare/jee-advanced-2023-josaa-cutoff",
    2024: "himanshurawat789/josaa-cutoff-2024",
    # 2025 may not be on Kaggle yet — fallback to scraper
}

# ---------------------------------------------------------------------------
# JoSAA website scraper config
# The portal uses session-based pagination but round-specific endpoints exist.
# ---------------------------------------------------------------------------
JOSAA_BASE_URL = "https://josaa.nic.in"
# Cutoff data is rendered in HTML tables at this endpoint (POST-based)
JOSAA_CUTOFF_ENDPOINT = "https://josaa.nic.in/webinfocms/Handler/fileTransfer.ashx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ---------------------------------------------------------------------------
# Fallback: use the existing synthetic data but flag it clearly
# ---------------------------------------------------------------------------
SYNTHETIC_SOURCE = ROOT / "ml" / "data" / "raw" / "josaa_cutoffs_2021_2023.csv"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_provenance(dest_dir: Path, year: int, source: str, row_count: int, notes: str = "") -> None:
    prov = {
        "year": year,
        "source": source,
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "notes": notes,
    }
    csv_files = list(dest_dir.glob("*.csv"))
    if csv_files:
        prov["sha256"] = sha256_of_file(csv_files[0])
    prov_path = dest_dir / "provenance.json"
    prov_path.write_text(json.dumps(prov, indent=2))
    log.info(f"Provenance written → {prov_path}")


# ---------------------------------------------------------------------------
# Strategy 1: Kaggle API
# ---------------------------------------------------------------------------

def try_kaggle(year: int) -> bool:
    """Attempt to download from Kaggle. Returns True if successful."""
    if year not in KAGGLE_DATASETS:
        log.info(f"No Kaggle dataset registered for year {year}")
        return False

    # Check kaggle CLI is available
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

    # Find the downloaded CSV
    csvs = list(dest.glob("*.csv"))
    if not csvs:
        log.warning("Kaggle download succeeded but no CSV found")
        return False

    # Standardize filename
    primary = csvs[0]
    df = pd.read_csv(primary)
    log.info(f"Kaggle: loaded {len(df):,} rows from {primary.name}")

    write_provenance(dest, year, f"kaggle:{dataset}", len(df))
    return True


# ---------------------------------------------------------------------------
# Strategy 2: Web Scraper — josaa.nic.in
# ---------------------------------------------------------------------------

# JoSAA provides a downloadable Excel/CSV at a known static URL pattern for each year
# These are the official data release pages (verified manually)
JOSAA_OFFICIAL_DOWNLOADS = {
    2023: [
        # Round 1-6 cutoff data from the official JoSAA 2023 portal
        # These endpoints serve CSV/XLSX with all institute cutoffs
        "https://josaa.nic.in/webinfocms/Handler/fileTransfer.ashx?file=JoSAA2023Round6Allotment.xlsx",
    ],
    2024: [
        "https://josaa.nic.in/webinfocms/Handler/fileTransfer.ashx?file=JoSAA2024Round6Allotment.xlsx",
    ],
    2025: [
        "https://josaa.nic.in/webinfocms/Handler/fileTransfer.ashx?file=JoSAA2025Round5Allotment.xlsx",
    ],
}


def scrape_josaa_table(year: int, round_num: int, session: requests.Session) -> pd.DataFrame | None:
    """
    Scrape the JoSAA cutoff HTML table for a specific year and round.
    Falls back to constructing a DataFrame from the paginated response.
    """
    # The JoSAA API endpoint for cutoff data uses these POST parameters
    payload = {
        "etype": "1",
        "round": str(round_num),
        "Year": str(year),
        "instType": "",
        "quota": "",
        "gender": "",
        "branchCode": "",
    }

    try:
        resp = session.post(
            JOSAA_CUTOFF_ENDPOINT,
            data=payload,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f"  Scrape request failed for year={year} round={round_num}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        log.warning(f"  No table found for year={year} round={round_num}")
        return None

    rows = []
    headers = []
    for i, tr in enumerate(table.find_all("tr")):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if i == 0:
            headers = cells
        else:
            if cells:
                rows.append(cells)

    if not headers or not rows:
        return None

    df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
    df["year"] = year
    df["round_number"] = round_num
    log.info(f"  Scraped {len(df):,} rows for year={year} round={round_num}")
    return df


def try_scrape(year: int) -> bool:
    """Attempt to scrape josaa.nic.in. Returns True if successful."""
    dest = RAW_JOSAA / str(year)
    dest.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    # Determine how many rounds to scrape
    rounds = range(1, 7) if year < 2025 else range(1, 6)  # 2025 may be partial

    all_dfs = []
    for rnd in rounds:
        log.info(f"Scraping JoSAA {year} Round {rnd}...")
        df = scrape_josaa_table(year, rnd, session)
        if df is not None:
            all_dfs.append(df)
        time.sleep(1.5)  # polite scraping

    if not all_dfs:
        log.warning(f"Scraper yielded no data for year {year}")
        return False

    combined = pd.concat(all_dfs, ignore_index=True)
    out_path = dest / f"josaa_{year}_raw.csv"
    combined.to_csv(out_path, index=False)
    log.info(f"Scraper: saved {len(combined):,} rows → {out_path}")

    write_provenance(
        dest, year,
        f"scrape:{JOSAA_CUTOFF_ENDPOINT}",
        len(combined),
        notes=f"Scraped rounds {list(rounds)}"
    )
    return True


# ---------------------------------------------------------------------------
# Strategy 3: Use existing synthetic data (clearly flagged)
# ---------------------------------------------------------------------------

def use_synthetic_fallback(year: int) -> bool:
    """
    Copy the existing synthetic dataset as a clearly labeled placeholder.
    This MUST be replaced with real data before final delivery.
    Logs a loud warning and writes a provenance record flagging it as synthetic.
    """
    if not SYNTHETIC_SOURCE.exists():
        log.error("Synthetic fallback dataset not found either. Manual intervention required.")
        return False

    dest = RAW_JOSAA / str(year)
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / f"josaa_{year}_raw.csv"

    # Filter the synthetic data to the requested year (it covers 2021-2023)
    df_all = pd.read_csv(SYNTHETIC_SOURCE)
    df_year = df_all[df_all["year"] == year].copy()

    if df_year.empty:
        # For 2024/2025 which don't exist in the synthetic data, use 2023 as proxy
        df_year = df_all[df_all["year"] == 2023].copy()
        df_year["year"] = year
        log.warning(
            f"⚠  SYNTHETIC FALLBACK: Using 2023 data as proxy for {year}. "
            "This is NOT real data. Replace before production."
        )

    df_year.to_csv(out_path, index=False)

    write_provenance(
        dest, year,
        "SYNTHETIC:ml/data/raw/josaa_cutoffs_2021_2023.csv",
        len(df_year),
        notes=(
            "WARNING: This is programmatically generated synthetic data. "
            "NOT real JoSAA records. Replace with real data via Kaggle or scraping."
        ),
    )

    log.warning(
        f"⚠  SYNTHETIC DATA written for year {year} ({len(df_year):,} rows). "
        "Mark data/reports/validation_report.json as SYNTHETIC."
    )
    return True


# ---------------------------------------------------------------------------
# Acquire a single year
# ---------------------------------------------------------------------------

def acquire_year(year: int, strategy: str = "auto") -> bool:
    """
    Acquire JoSAA data for a given year using the specified strategy.

    Args:
        year: 2023, 2024, or 2025
        strategy: "auto" | "kaggle" | "scrape" | "synthetic"
    """
    log.info(f"{'='*60}")
    log.info(f"Acquiring JoSAA data for year {year} (strategy={strategy})")
    log.info(f"{'='*60}")

    dest = RAW_JOSAA / str(year)

    # Skip if already acquired
    existing = list(dest.glob("*.csv"))
    if existing and strategy == "auto":
        log.info(f"Year {year}: raw CSV already exists ({existing[0].name}). Skipping.")
        return True

    if strategy == "auto":
        # Try in priority order
        if try_kaggle(year):
            return True
        log.info("Kaggle failed — trying web scraper...")
        if try_scrape(year):
            return True
        log.info("Scraper failed — using synthetic fallback...")
        return use_synthetic_fallback(year)

    elif strategy == "kaggle":
        return try_kaggle(year)
    elif strategy == "scrape":
        return try_scrape(year)
    elif strategy == "synthetic":
        return use_synthetic_fallback(year)
    else:
        log.error(f"Unknown strategy: {strategy}")
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 01: Acquire JoSAA/CSAB raw cutoff data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--year",
        choices=["2023", "2024", "2025", "all"],
        default="all",
        help="Which year(s) to acquire (default: all)",
    )
    parser.add_argument(
        "--strategy",
        choices=["auto", "kaggle", "scrape", "synthetic"],
        default="auto",
        help="Acquisition strategy (default: auto — tries Kaggle → scrape → synthetic)",
    )
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
