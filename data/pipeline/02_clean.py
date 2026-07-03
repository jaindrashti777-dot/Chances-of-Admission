#!/usr/bin/env python3
"""
Stage 02 — Data Cleaning
=========================
Cleans raw per-year JoSAA CSVs into a consistent interim schema.

Key operations:
    - Column name normalization (JoSAA changes headers between years)
    - Institute name canonicalization
    - Branch name canonicalization
    - Category normalization (handles PwD variants, spacing differences)
    - Quota normalization
    - Rank type casting and validation
    - Duplicate removal
    - Missing value handling

Output:
    data/processed/josaa_{year}.csv  — One clean file per year

Usage:
    python data/pipeline/02_clean.py --year 2023
    python data/pipeline/02_clean.py --year all
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
RAW_JOSAA = ROOT / "data" / "raw" / "josaa"
PROCESSED  = ROOT / "data" / "processed"
METADATA   = ROOT / "data" / "raw" / "metadata"

PROCESSED.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline.02_clean")

# ---------------------------------------------------------------------------
# TARGET SCHEMA
# All cleaned files conform to these exact column names and types.
# ---------------------------------------------------------------------------
TARGET_COLUMNS = [
    "counselling_body",   # str: JoSAA | CSAB
    "institute_type",     # str: NIT | IIIT | GFTI | IIT
    "institute_name",     # str: canonical
    "branch_name",        # str: canonical
    "category",           # str: OPEN | EWS | OBC-NCL | SC | ST | OPEN-PwD | ...
    "quota",              # str: HS | OS | AI
    "seat_pool",          # str: Gender-Neutral | Female-Only
    "year",               # int
    "round_number",       # int
    "opening_rank",       # int
    "closing_rank",       # int
]

# ---------------------------------------------------------------------------
# COLUMN NAME MAPPINGS
# JoSAA changed column headers across years. Map all variants → target names.
# ---------------------------------------------------------------------------
COLUMN_ALIASES: dict[str, str] = {
    # Institute
    "institute":                    "institute_name",
    "institute name":               "institute_name",
    "college name":                 "institute_name",
    "college_name":                 "institute_name",
    "institution":                  "institute_name",
    "institutename":                "institute_name",

    # Branch
    "academic program name":        "branch_name",
    "branch":                       "branch_name",
    "branch name":                  "branch_name",
    "branch_name":                  "branch_name",
    "program":                      "branch_name",
    "program name":                 "branch_name",
    "course":                       "branch_name",

    # Institute type
    "institute type":               "institute_type",
    "institute_type":               "institute_type",
    "type":                         "institute_type",
    "insttype":                     "institute_type",

    # Category
    "category":                     "category",
    "seat type":                    "category",
    "seat_type":                    "category",
    "caste":                        "category",

    # Quota
    "quota":                        "quota",
    "state quota":                  "quota",

    # Seat pool / gender
    "gender":                       "seat_pool",
    "gender neutral":               "seat_pool",
    "seat pool":                    "seat_pool",
    "seat_pool":                    "seat_pool",
    "pool":                         "seat_pool",

    # Ranks
    "opening rank":                 "opening_rank",
    "opening_rank":                 "opening_rank",
    "or":                           "opening_rank",
    "open rank":                    "opening_rank",

    "closing rank":                 "closing_rank",
    "closing_rank":                 "closing_rank",
    "cr":                           "closing_rank",
    "close rank":                   "closing_rank",

    # Round
    "round":                        "round_number",
    "round_number":                 "round_number",
    "round no":                     "round_number",
    "round no.":                    "round_number",
    "round number":                 "round_number",

    # Year
    "year":                         "year",

    # Counselling body
    "counselling_body":             "counselling_body",
    "counselling body":             "counselling_body",
    "body":                         "counselling_body",
}

# ---------------------------------------------------------------------------
# CATEGORY NORMALIZATION
# Map all known raw category strings → canonical form
# ---------------------------------------------------------------------------
CATEGORY_MAP: dict[str, str] = {
    # General / Open
    "open":             "OPEN",
    "gen":              "OPEN",
    "general":          "OPEN",
    "ur":               "OPEN",
    "unreserved":       "OPEN",

    # EWS
    "ews":              "EWS",
    "economically weaker section": "EWS",

    # OBC-NCL
    "obc":              "OBC-NCL",
    "obc-ncl":          "OBC-NCL",
    "obc ncl":          "OBC-NCL",
    "obcncl":           "OBC-NCL",
    "other backward class": "OBC-NCL",
    "other backward classes": "OBC-NCL",
    "obc (ncl)":        "OBC-NCL",

    # SC
    "sc":               "SC",
    "scheduled caste":  "SC",

    # ST
    "st":               "ST",
    "scheduled tribe":  "ST",

    # PwD variants (Person with Disability)
    "open (pwd)":       "OPEN-PwD",
    "open-pwd":         "OPEN-PwD",
    "gen-pwd":          "OPEN-PwD",
    "gen (pwd)":        "OPEN-PwD",
    "open pwd":         "OPEN-PwD",
    "open (ph)":        "OPEN-PwD",

    "ews (pwd)":        "EWS-PwD",
    "ews-pwd":          "EWS-PwD",
    "ews pwd":          "EWS-PwD",

    "obc-ncl (pwd)":    "OBC-NCL-PwD",
    "obc-ncl-pwd":      "OBC-NCL-PwD",
    "obc ncl pwd":      "OBC-NCL-PwD",
    "obc ncl (pwd)":    "OBC-NCL-PwD",
    "obc (pwd)":        "OBC-NCL-PwD",

    "sc (pwd)":         "SC-PwD",
    "sc-pwd":           "SC-PwD",
    "sc pwd":           "SC-PwD",

    "st (pwd)":         "ST-PwD",
    "st-pwd":           "ST-PwD",
    "st pwd":           "ST-PwD",
}

# ---------------------------------------------------------------------------
# SEAT POOL / GENDER NORMALIZATION
# ---------------------------------------------------------------------------
SEAT_POOL_MAP: dict[str, str] = {
    "gender-neutral":   "Gender-Neutral",
    "gender neutral":   "Gender-Neutral",
    "neutral":          "Gender-Neutral",
    "gn":               "Gender-Neutral",
    "all":              "Gender-Neutral",
    "both":             "Gender-Neutral",

    "female-only":      "Female-Only",
    "female only":      "Female-Only",
    "female":           "Female-Only",
    "fo":               "Female-Only",
    "girls":            "Female-Only",
    "girl":             "Female-Only",
}

# ---------------------------------------------------------------------------
# QUOTA NORMALIZATION
# ---------------------------------------------------------------------------
QUOTA_MAP: dict[str, str] = {
    "hs":   "HS",
    "home state": "HS",
    "home": "HS",
    "os":   "OS",
    "other state": "OS",
    "other": "OS",
    "ai":   "AI",
    "all india": "AI",
    "allindia": "AI",
}

# ---------------------------------------------------------------------------
# INSTITUTE TYPE NORMALIZATION
# ---------------------------------------------------------------------------
INSTITUTE_TYPE_MAP: dict[str, str] = {
    "nit":              "NIT",
    "national institute of technology": "NIT",
    "iiit":             "IIIT",
    "iit":              "IIT",
    "indian institute of technology": "IIT",
    "gfti":             "GFTI",
    "government funded technical institute": "GFTI",
    "centrally funded technical institute": "GFTI",
    "cfti":             "GFTI",
}

# ---------------------------------------------------------------------------
# INSTITUTE NAME CANONICALIZATION
# Map all known JoSAA raw name variants → single canonical form.
# Sourced from comparing JoSAA PDFs across years.
# ---------------------------------------------------------------------------
INSTITUTE_NAME_MAP: dict[str, str] = {
    # NIT Tiruchirappalli
    "national institute of technology tiruchirappalli": "NIT Tiruchirappalli",
    "nit tiruchirappalli": "NIT Tiruchirappalli",
    "nit trichy": "NIT Tiruchirappalli",
    "national institute of technology, tiruchirappalli": "NIT Tiruchirappalli",

    # NIT Warangal
    "national institute of technology warangal": "NIT Warangal",
    "nit warangal": "NIT Warangal",
    "national institute of technology, warangal": "NIT Warangal",

    # NIT Surathkal
    "national institute of technology karnataka, surathkal": "NIT Surathkal",
    "nit surathkal": "NIT Surathkal",
    "nitk surathkal": "NIT Surathkal",
    "national institute of technology karnataka": "NIT Surathkal",

    # NIT Rourkela
    "national institute of technology rourkela": "NIT Rourkela",
    "nit rourkela": "NIT Rourkela",
    "national institute of technology, rourkela": "NIT Rourkela",

    # NIT Calicut
    "national institute of technology calicut": "NIT Calicut",
    "nit calicut": "NIT Calicut",
    "national institute of technology, calicut": "NIT Calicut",

    # MNNIT Allahabad
    "motilal nehru national institute of technology allahabad": "MNNIT Allahabad",
    "mnnit allahabad": "MNNIT Allahabad",
    "motilal nehru national institute of technology, allahabad": "MNNIT Allahabad",

    # MNIT Jaipur
    "malaviya national institute of technology jaipur": "MNIT Jaipur",
    "mnit jaipur": "MNIT Jaipur",
    "malaviya national institute of technology, jaipur": "MNIT Jaipur",

    # VNIT Nagpur
    "visvesvaraya national institute of technology nagpur": "VNIT Nagpur",
    "vnit nagpur": "VNIT Nagpur",
    "visvesvaraya national institute of technology, nagpur": "VNIT Nagpur",

    # NIT Kurukshetra
    "national institute of technology kurukshetra": "NIT Kurukshetra",
    "nit kurukshetra": "NIT Kurukshetra",

    # NIT Durgapur
    "national institute of technology durgapur": "NIT Durgapur",
    "nit durgapur": "NIT Durgapur",

    # MANIT Bhopal
    "maulana azad national institute of technology bhopal": "MANIT Bhopal",
    "manit bhopal": "MANIT Bhopal",
    "maulana azad national institute of technology, bhopal": "MANIT Bhopal",

    # NIT Patna
    "national institute of technology patna": "NIT Patna",
    "nit patna": "NIT Patna",

    # SVNIT Surat
    "sardar vallabhbhai national institute of technology surat": "SVNIT Surat",
    "svnit surat": "SVNIT Surat",

    # NIT Jamshedpur
    "national institute of technology jamshedpur": "NIT Jamshedpur",
    "nit jamshedpur": "NIT Jamshedpur",

    # NIT Raipur
    "national institute of technology raipur": "NIT Raipur",
    "nit raipur": "NIT Raipur",

    # NIT Silchar
    "national institute of technology silchar": "NIT Silchar",
    "nit silchar": "NIT Silchar",

    # NIT Delhi
    "national institute of technology delhi": "NIT Delhi",
    "nit delhi": "NIT Delhi",

    # NIT Goa
    "national institute of technology goa": "NIT Goa",
    "nit goa": "NIT Goa",

    # NIT Hamirpur
    "national institute of technology hamirpur": "NIT Hamirpur",
    "nit hamirpur": "NIT Hamirpur",

    # NIT Uttarakhand
    "national institute of technology uttarakhand": "NIT Uttarakhand",
    "nit uttarakhand": "NIT Uttarakhand",

    # NIT Srinagar
    "national institute of technology srinagar": "NIT Srinagar",
    "nit srinagar": "NIT Srinagar",

    # NIT Agartala
    "national institute of technology agartala": "NIT Agartala",
    "nit agartala": "NIT Agartala",

    # NIT Puducherry
    "national institute of technology puducherry": "NIT Puducherry",
    "nit puducherry": "NIT Puducherry",

    # NIT Andhra Pradesh
    "national institute of technology andhra pradesh": "NIT Andhra Pradesh",
    "nit andhra pradesh": "NIT Andhra Pradesh",

    # NIT Sikkim
    "national institute of technology sikkim": "NIT Sikkim",
    "nit sikkim": "NIT Sikkim",

    # NIT Arunachal Pradesh
    "national institute of technology arunachal pradesh": "NIT Arunachal Pradesh",
    "nit arunachal pradesh": "NIT Arunachal Pradesh",

    # NIT Manipur
    "national institute of technology manipur": "NIT Manipur",
    "nit manipur": "NIT Manipur",

    # NIT Meghalaya
    "national institute of technology meghalaya": "NIT Meghalaya",
    "nit meghalaya": "NIT Meghalaya",

    # NIT Mizoram
    "national institute of technology mizoram": "NIT Mizoram",
    "nit mizoram": "NIT Mizoram",

    # NIT Nagaland
    "national institute of technology nagaland": "NIT Nagaland",
    "nit nagaland": "NIT Nagaland",

    # NIT Andaman and Nicobar
    "national institute of technology andaman and nicobar islands": "NIT Andaman and Nicobar",
    "nit andaman": "NIT Andaman and Nicobar",

    # IIIT Hyderabad
    "international institute of information technology hyderabad": "IIIT Hyderabad",
    "iiit hyderabad": "IIIT Hyderabad",
    "iiith": "IIIT Hyderabad",

    # IIIT Allahabad
    "indian institute of information technology allahabad": "IIIT Allahabad",
    "iiit allahabad": "IIIT Allahabad",
    "iiita": "IIIT Allahabad",

    # ABV-IIITM Gwalior
    "atal bihari vajpayee indian institute of information technology and management gwalior": "ABV-IIITM Gwalior",
    "abv-iiitm gwalior": "ABV-IIITM Gwalior",
    "iiitm gwalior": "ABV-IIITM Gwalior",

    # IIITDM Jabalpur
    "indian institute of information technology design and manufacturing jabalpur": "IIITDM Jabalpur",
    "iiitdm jabalpur": "IIITDM Jabalpur",

    # IIITDM Kancheepuram
    "indian institute of information technology design and manufacturing kancheepuram": "IIITDM Kancheepuram",
    "iiitdm kancheepuram": "IIITDM Kancheepuram",

    # GFTIs
    "iiest shibpur": "IIEST Shibpur",
    "indian institute of engineering science and technology shibpur": "IIEST Shibpur",
    "be college shibpur": "IIEST Shibpur",

    "bit mesra ranchi": "BIT Mesra",
    "birla institute of technology mesra": "BIT Mesra",
    "bit mesra": "BIT Mesra",

    "tezpur university": "Tezpur University",

    "sliet longowal": "SLIET Longowal",
    "sant longowal institute of engineering and technology": "SLIET Longowal",

    "jamia millia islamia": "Jamia Millia Islamia",
    "jamia millia islamia new delhi": "Jamia Millia Islamia",

    "aligarh muslim university": "Aligarh Muslim University",

    "banaras hindu university": "Banaras Hindu University",
    "institute of technology banaras hindu university": "Banaras Hindu University",
    "it bhu varanasi": "Banaras Hindu University",

    "school of planning and architecture new delhi": "School of Planning and Architecture",
    "spa delhi": "School of Planning and Architecture",

    "delhi technological university": "Delhi Technological University",
    "dtu delhi": "Delhi Technological University",

    "netaji subhas university of technology": "Netaji Subhas University of Technology",
    "nsut delhi": "Netaji Subhas University of Technology",
    "netaji subhas institute of technology": "Netaji Subhas University of Technology",

    "guru ghasidas vishwavidyalaya": "Guru Ghasidas Vishwavidyalaya",

    "madan mohan malaviya university of technology": "Madan Mohan Malaviya University of Technology",
    "mmmut gorakhpur": "Madan Mohan Malaviya University of Technology",

    "hbtu kanpur": "HBTU Kanpur",
    "harcourt butler technical university": "HBTU Kanpur",
}

# ---------------------------------------------------------------------------
# BRANCH NAME CANONICALIZATION
# ---------------------------------------------------------------------------
BRANCH_NAME_MAP: dict[str, str] = {
    # CSE variants
    "computer science and engineering": "Computer Science and Engineering",
    "cse": "Computer Science and Engineering",
    "b.tech computer science and engineering": "Computer Science and Engineering",
    "computer science & engineering": "Computer Science and Engineering",
    "computer science engineering": "Computer Science and Engineering",

    # ECE variants
    "electronics and communication engineering": "Electronics and Communication Engineering",
    "ece": "Electronics and Communication Engineering",
    "electronics & communication engineering": "Electronics and Communication Engineering",
    "electronics and communications engineering": "Electronics and Communication Engineering",
    "electronics communication engineering": "Electronics and Communication Engineering",

    # IT variants
    "information technology": "Information Technology",
    "it": "Information Technology",

    # EE variants
    "electrical engineering": "Electrical Engineering",
    "ee": "Electrical Engineering",
    "electrical and electronics engineering": "Electrical and Electronics Engineering",
    "eee": "Electrical and Electronics Engineering",

    # ME variants
    "mechanical engineering": "Mechanical Engineering",
    "me": "Mechanical Engineering",
    "mechanical engg": "Mechanical Engineering",

    # CE variants
    "civil engineering": "Civil Engineering",
    "ce": "Civil Engineering",
    "civil engg": "Civil Engineering",

    # CHE variants
    "chemical engineering": "Chemical Engineering",
    "che": "Chemical Engineering",
    "chemical engg": "Chemical Engineering",

    # DS/AI variants
    "data science and artificial intelligence": "Data Science and Artificial Intelligence",
    "data science & artificial intelligence": "Data Science and Artificial Intelligence",
    "ds and ai": "Data Science and Artificial Intelligence",
    "dsai": "Data Science and Artificial Intelligence",

    "artificial intelligence and machine learning": "Artificial Intelligence and Machine Learning",
    "ai and ml": "Artificial Intelligence and Machine Learning",
    "aiml": "Artificial Intelligence and Machine Learning",
    "artificial intelligence & machine learning": "Artificial Intelligence and Machine Learning",

    "computer science and engineering (artificial intelligence)": "Computer Science and Engineering (Artificial Intelligence)",
    "cse (ai)": "Computer Science and Engineering (Artificial Intelligence)",
    "cse ai": "Computer Science and Engineering (Artificial Intelligence)",

    # Metallurgy
    "metallurgical and materials engineering": "Metallurgical and Materials Engineering",
    "metallurgy and materials engineering": "Metallurgical and Materials Engineering",
    "metallurgical engineering": "Metallurgical and Materials Engineering",

    # Production
    "production and industrial engineering": "Production and Industrial Engineering",
    "production engineering": "Production and Industrial Engineering",

    # Biotech
    "biotechnology": "Biotechnology",
    "bio technology": "Biotechnology",

    # Architecture
    "architecture": "Architecture",
    "b.arch": "Architecture",

    # Mathematics and Computing
    "mathematics and computing": "Mathematics and Computing",
    "mathematics & computing": "Mathematics and Computing",
    "math and computing": "Mathematics and Computing",

    # Mining
    "mining engineering": "Mining Engineering",
    "mining engg": "Mining Engineering",

    # Instrumentation
    "electronics and instrumentation engineering": "Electronics and Instrumentation Engineering",
    "instrumentation and control engineering": "Instrumentation and Control Engineering",

    # Internet of Things
    "internet of things": "Internet of Things",
    "iot": "Internet of Things",

    # Cyber Security
    "computer science and engineering (cyber security)": "Computer Science and Engineering (Cyber Security)",
    "cse (cyber security)": "Computer Science and Engineering (Cyber Security)",
    "cyber security": "Computer Science and Engineering (Cyber Security)",
}

# ---------------------------------------------------------------------------
# COUNSELLING BODY NORMALIZATION
# ---------------------------------------------------------------------------
BODY_MAP: dict[str, str] = {
    "josaa": "JoSAA",
    "jo saa": "JoSAA",
    "csab": "CSAB",
    "c sab": "CSAB",
}


# ---------------------------------------------------------------------------
# Core cleaning logic
# ---------------------------------------------------------------------------

def normalize_col(col: str) -> str:
    """Lowercase, strip, collapse spaces."""
    return re.sub(r"\s+", " ", col.strip().lower())


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw column names → target names using COLUMN_ALIASES."""
    df = df.copy()
    rename_map = {}
    for col in df.columns:
        norm = normalize_col(col)
        if norm in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[norm]
    df.rename(columns=rename_map, inplace=True)
    return df


def normalize_categorical(series: pd.Series, mapping: dict[str, str], label: str) -> pd.Series:
    """Apply a normalization map to a string series, report unmapped values."""
    result = series.astype(str).str.strip().str.lower().map(
        lambda x: mapping.get(x, None)
    )
    unmapped = series[result.isna()].unique()
    if len(unmapped) > 0:
        log.warning(f"  {label}: {len(unmapped)} unmapped values: {unmapped[:10].tolist()}")
    return result


def clean_year(year: int) -> pd.DataFrame | None:
    """Load, clean, and return the processed DataFrame for a given year."""
    raw_dir = RAW_JOSAA / str(year)
    csvs = list(raw_dir.glob("*.csv"))

    if not csvs:
        log.error(f"Year {year}: no raw CSV found in {raw_dir}. Run 01_acquire.py first.")
        return None

    raw_path = csvs[0]
    log.info(f"\n{'='*60}")
    log.info(f"Cleaning JoSAA {year} — {raw_path.name}")
    log.info(f"{'='*60}")

    df = pd.read_csv(raw_path, low_memory=False)
    raw_rows = len(df)
    log.info(f"  Loaded {raw_rows:,} rows, {len(df.columns)} columns")
    log.info(f"  Raw columns: {df.columns.tolist()}")

    # Step 1: Normalize column names
    df = map_columns(df)
    log.info(f"  After column mapping: {df.columns.tolist()}")

    # Step 2: Ensure all target columns exist
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            log.warning(f"  Missing column '{col}' — will be set to NaN")
            df[col] = None

    df = df[TARGET_COLUMNS].copy()

    # Step 3: Ensure year column is filled
    if df["year"].isna().all():
        df["year"] = year
    df["year"] = df["year"].fillna(year).astype(int)

    # Step 4: Normalize string fields
    df["counselling_body"] = normalize_categorical(df["counselling_body"], BODY_MAP, "counselling_body")
    df["counselling_body"] = df["counselling_body"].fillna("JoSAA")

    df["institute_type"] = normalize_categorical(df["institute_type"], INSTITUTE_TYPE_MAP, "institute_type")

    # Step 5: Canonicalize institute names
    df["institute_name"] = (
        df["institute_name"]
        .astype(str)
        .str.strip()
        .map(lambda x: INSTITUTE_NAME_MAP.get(x.lower(), x))
    )

    # Step 6: Canonicalize branch names
    df["branch_name"] = (
        df["branch_name"]
        .astype(str)
        .str.strip()
        .map(lambda x: BRANCH_NAME_MAP.get(x.lower(), x))
    )

    # Step 7: Normalize categorical fields
    df["category"] = normalize_categorical(df["category"], CATEGORY_MAP, "category")
    df["quota"] = normalize_categorical(df["quota"], QUOTA_MAP, "quota")
    df["seat_pool"] = normalize_categorical(df["seat_pool"], SEAT_POOL_MAP, "seat_pool")

    # Step 8: Cast ranks to integer
    def safe_int(x) -> int | None:
        try:
            val = int(str(x).strip().replace(",", ""))
            return val if val > 0 else None
        except (ValueError, TypeError):
            return None

    df["opening_rank"] = df["opening_rank"].map(safe_int)
    df["closing_rank"] = df["closing_rank"].map(safe_int)
    df["round_number"] = df["round_number"].map(safe_int)

    # Step 9: Drop rows with null ranks or null category
    before = len(df)
    df = df.dropna(subset=["opening_rank", "closing_rank", "category", "quota", "seat_pool"])
    log.info(f"  Dropped {before - len(df):,} rows with null critical fields")

    # Step 10: Fix inverted ranks (opening > closing)
    inverted = df["opening_rank"] > df["closing_rank"]
    n_inverted = inverted.sum()
    if n_inverted > 0:
        log.warning(f"  Fixing {n_inverted:,} rows where opening_rank > closing_rank")
        df.loc[inverted, "opening_rank"] = (df.loc[inverted, "closing_rank"] * 0.70).astype(int)

    # Step 11: Remove duplicates
    before = len(df)
    key_cols = ["institute_name", "branch_name", "category", "quota", "seat_pool", "year", "round_number"]
    df = df.drop_duplicates(subset=key_cols, keep="last")
    log.info(f"  Removed {before - len(df):,} duplicate rows")

    # Step 12: Cast final types
    df["opening_rank"] = df["opening_rank"].astype(int)
    df["closing_rank"] = df["closing_rank"].astype(int)
    df["round_number"] = df["round_number"].astype(int)
    df["year"] = df["year"].astype(int)

    log.info(f"  ✅ Final: {len(df):,} clean rows (from {raw_rows:,} raw rows)")
    log.info(f"  Categories: {sorted(df['category'].unique())}")
    log.info(f"  Quotas:     {sorted(df['quota'].unique())}")
    log.info(f"  Seat pools: {sorted(df['seat_pool'].unique())}")
    log.info(f"  Institutes: {df['institute_name'].nunique()} unique")
    log.info(f"  Branches:   {df['branch_name'].nunique()} unique")
    log.info(f"  Rounds:     {sorted(df['round_number'].unique())}")

    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 02: Clean raw JoSAA CSVs")
    parser.add_argument(
        "--year",
        choices=["2023", "2024", "2025", "all"],
        default="all",
    )
    args = parser.parse_args()

    years = [2023, 2024, 2025] if args.year == "all" else [int(args.year)]
    results = {}

    for yr in years:
        df = clean_year(yr)
        if df is not None:
            out_path = PROCESSED / f"josaa_{yr}.csv"
            df.to_csv(out_path, index=False)
            log.info(f"  Saved → {out_path}")
            results[yr] = len(df)
        else:
            results[yr] = None

    log.info("\n" + "="*60)
    log.info("CLEANING SUMMARY")
    log.info("="*60)
    for yr, count in results.items():
        icon = "✅" if count else "❌"
        log.info(f"  {icon} {yr}: {count:,} rows" if count else f"  ❌ {yr}: FAILED")


if __name__ == "__main__":
    main()
