#!/usr/bin/env python3
"""
Comprehensive data audit script — answers all 7 steps.
Prints a structured report to stdout.
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT   = Path(__file__).resolve().parent
MASTER = ROOT / "data" / "master" / "master_dataset.csv"

print("=" * 70)
print("  DATASET AUDIT REPORT")
print("=" * 70)

df = pd.read_csv(MASTER)

# ── STEP 1: Format & Structure ─────────────────────────────────────────────
print("\n📁 STEP 1 — FORMAT & STRUCTURE")
print(f"  Format:        CSV")
print(f"  Total rows:    {len(df):,}")
print(f"  Total columns: {len(df.columns)}")
print(f"  File size:     {MASTER.stat().st_size / 1024 / 1024:.1f} MB")
print(f"\n  Columns:")
for col in df.columns:
    dtype = str(df[col].dtype)
    nulls = df[col].isna().sum()
    print(f"    {col:<30}  dtype={dtype:<10}  nulls={nulls:,}")

# ── STEP 2: Sample Rows ────────────────────────────────────────────────────
print("\n📋 STEP 2 — SAMPLE 10 ROWS")
key_cols = ["year", "institute_name", "branch_name", "category", "quota",
            "seat_pool", "round_number", "opening_rank", "closing_rank"]
print(df[key_cols].head(10).to_string(index=False))

# ── STEP 3: Missing Values ────────────────────────────────────────────────
print("\n🔍 STEP 3 — MISSING VALUES")
nulls = df.isnull().sum()
nulls = nulls[nulls > 0]
if nulls.empty:
    print("  ✅ No missing values in any column")
else:
    for col, n in nulls.items():
        pct = 100 * n / len(df)
        print(f"  ⚠  {col:<30}: {n:,} missing ({pct:.1f}%)")

# ── STEP 4: Duplicates ────────────────────────────────────────────────────
print("\n🔁 STEP 4 — DUPLICATE ROWS")
key_cols_dup = ["institute_name","branch_name","category","quota","seat_pool","year","round_number"]
n_dup = df.duplicated(subset=key_cols_dup).sum()
print(f"  Exact key duplicates: {n_dup:,}")

# ── STEP 5: Institute Name Audit ──────────────────────────────────────────
print("\n🏛  STEP 5 — INSTITUTE NAME AUDIT")
institutes = sorted(df["institute_name"].unique())
print(f"  Unique institute names: {len(institutes)}")
print(f"\n  Full list:")
for i, name in enumerate(institutes, 1):
    count = len(df[df["institute_name"] == name])
    print(f"    {i:>3}. {name:<55} ({count:,} rows)")

# ── STEP 6: Branch Name Audit ─────────────────────────────────────────────
print("\n🌿 STEP 6 — BRANCH NAME AUDIT")
branches = df["branch_name"].value_counts()
print(f"  Unique branch names: {len(branches)}")
print(f"\n  All branches (by frequency):")
for branch, count in branches.items():
    print(f"    {branch:<60} {count:,} rows")

# ── STEP 7: Category / Quota / Seat Pool ─────────────────────────────────
print("\n🏷  STEP 7 — CATEGORICAL VALUES")
print(f"  Categories:  {sorted(df['category'].unique())}")
print(f"  Quotas:      {sorted(df['quota'].unique())}")
print(f"  Seat pools:  {sorted(df['seat_pool'].unique())}")
print(f"  Years:       {sorted(df['year'].unique())}")
print(f"  Rounds:      {sorted(df['round_number'].unique())}")
print(f"  Inst types:  {sorted(df['institute_type'].dropna().unique())}")

# ── STEP 8: Rank Statistics ───────────────────────────────────────────────
print("\n📊 STEP 8 — RANK STATISTICS")
print(f"  Opening rank — min: {df['opening_rank'].min():,}  max: {df['opening_rank'].max():,}  mean: {df['opening_rank'].mean():,.0f}")
print(f"  Closing rank — min: {df['closing_rank'].min():,}  max: {df['closing_rank'].max():,}  mean: {df['closing_rank'].mean():,.0f}")

# Rank inversion check
inverted = (df["opening_rank"] >= df["closing_rank"]).sum()
print(f"\n  Rows where opening >= closing rank: {inverted:,}  {'✅ None' if inverted == 0 else '⚠  NEEDS FIX'}")

# ── STEP 9: Category-wise Analysis ───────────────────────────────────────
print("\n📈 STEP 9 — CATEGORY-WISE CLOSING RANK (Round 6, OS/AI, GN)")
r6 = df[(df["round_number"]==6) & (df["quota"].isin(["OS","AI"])) & (df["seat_pool"]=="Gender-Neutral")]
base_cats = ["OPEN","EWS","OBC-NCL","SC","ST"]
for cat in base_cats:
    subset = r6[r6["category"] == cat]["closing_rank"]
    if not subset.empty:
        print(f"  {cat:<12}: median={subset.median():>8,.0f}  min={subset.min():>8,}  max={subset.max():>8,}")

# ── STEP 10: Most Competitive Programs ───────────────────────────────────
print("\n🏆 STEP 10 — TOP 15 MOST COMPETITIVE PROGRAMS (OPEN, Round 6)")
top = r6[r6["category"]=="OPEN"].nsmallest(15,"closing_rank")[
    ["institute_name","branch_name","closing_rank","year"]
]
print(top.to_string(index=False))

# ── STEP 11: YoY Trend ───────────────────────────────────────────────────
print("\n📅 STEP 11 — YEAR-OVER-YEAR ROW COUNT")
for yr, grp in df.groupby("year"):
    print(f"  {yr}: {len(grp):,} rows  |  {grp['institute_name'].nunique()} institutes  |  {grp['branch_name'].nunique()} branches")

# ── STEP 12: Data Source Flag ────────────────────────────────────────────
if "data_source" in df.columns:
    print("\n⚠  STEP 12 — DATA PROVENANCE")
    for src, count in df["data_source"].value_counts().items():
        print(f"  {src}: {count:,} rows ({100*count/len(df):.1f}%)")

print("\n" + "=" * 70)
print("  AUDIT COMPLETE")
print("=" * 70)
