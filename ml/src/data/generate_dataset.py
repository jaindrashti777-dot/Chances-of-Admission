#!/usr/bin/env python3
"""
JoSAA/CSAB Historical Cutoff Dataset Generator
================================================
Generates a realistic synthetic dataset covering:
  - 31 NITs
  - 26 IIITs
  - 53 GFTIs
  - Years 2021, 2022, 2023
  - All 6 JoSAA counselling rounds per year
  - 5 categories (OPEN, EWS, OBC-NCL, SC, ST)
  - Relevant quotas (HS/OS for NITs/GFTIs, AI for IIITs)
  - Gender-Neutral and Female-Only seat pools

Methodology:
  - Base closing rank is defined per (college, branch) for OPEN, OS/AI, Gender-Neutral, Round 6
  - Category, quota, seat-pool, round, and year multipliers derive all other values
  - Opening rank is derived as a fraction of closing rank
  - Random noise (±8%) is applied for realism
  - Year-over-year drift simulates real cutoff trends

Output: ml/data/raw/josaa_cutoffs_2021_2023.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(seed=42)

# ---------------------------------------------------------------------------
# 1. COLLEGE DEFINITIONS
# Each college: (name, state, institute_type, counselling_body, base_cse_rank)
# base_cse_rank = OPEN, OS/AI quota, Gender-Neutral, Round 6
# ---------------------------------------------------------------------------

NITS = [
    # Tier 1 — Elite NITs (very competitive)
    ("NIT Tiruchirappalli",     "Tamil Nadu",           "NIT", "JoSAA",  1100),
    ("NIT Warangal",            "Telangana",            "NIT", "JoSAA",  1700),
    ("NIT Surathkal",           "Karnataka",            "NIT", "JoSAA",  2300),
    ("NIT Rourkela",            "Odisha",               "NIT", "JoSAA",  2900),
    ("NIT Calicut",             "Kerala",               "NIT", "JoSAA",  3400),
    ("MNNIT Allahabad",         "Uttar Pradesh",        "NIT", "JoSAA",  4200),
    ("MNIT Jaipur",             "Rajasthan",            "NIT", "JoSAA",  4900),
    ("VNIT Nagpur",             "Maharashtra",          "NIT", "JoSAA",  5600),
    # Tier 2 — Mid NITs
    ("NIT Kurukshetra",         "Haryana",              "NIT", "JoSAA",  7000),
    ("NIT Durgapur",            "West Bengal",          "NIT", "JoSAA",  8200),
    ("MANIT Bhopal",            "Madhya Pradesh",       "NIT", "JoSAA",  9100),
    ("NIT Patna",               "Bihar",                "NIT", "JoSAA",  10200),
    ("SVNIT Surat",             "Gujarat",              "NIT", "JoSAA",  10800),
    ("NIT Jamshedpur",          "Jharkhand",            "NIT", "JoSAA",  12300),
    ("NIT Raipur",              "Chhattisgarh",         "NIT", "JoSAA",  13500),
    ("NIT Silchar",             "Assam",                "NIT", "JoSAA",  14800),
    ("NIT Delhi",               "Delhi",                "NIT", "JoSAA",  12000),
    ("NIT Goa",                 "Goa",                  "NIT", "JoSAA",  13800),
    ("NIT Hamirpur",            "Himachal Pradesh",     "NIT", "JoSAA",  16500),
    # Tier 3 — Newer / less competitive NITs
    ("NIT Uttarakhand",         "Uttarakhand",          "NIT", "JoSAA",  18000),
    ("NIT Srinagar",            "Jammu and Kashmir",    "NIT", "JoSAA",  21000),
    ("NIT Agartala",            "Tripura",              "NIT", "JoSAA",  24000),
    ("NIT Puducherry",          "Puducherry",           "NIT", "JoSAA",  27000),
    ("NIT Andhra Pradesh",      "Andhra Pradesh",       "NIT", "JoSAA",  29000),
    ("NIT Sikkim",              "Sikkim",               "NIT", "JoSAA",  32000),
    # Tier 4 — NE/Remote NITs (high closing rank = less competitive)
    ("NIT Arunachal Pradesh",   "Arunachal Pradesh",    "NIT", "JoSAA",  36000),
    ("NIT Manipur",             "Manipur",              "NIT", "JoSAA",  38500),
    ("NIT Meghalaya",           "Meghalaya",            "NIT", "JoSAA",  40000),
    ("NIT Mizoram",             "Mizoram",              "NIT", "JoSAA",  42500),
    ("NIT Nagaland",            "Nagaland",             "NIT", "JoSAA",  44000),
    ("NIT Andaman and Nicobar", "Andaman and Nicobar",  "NIT", "JoSAA",  46000),
]

IIITS = [
    # Top IIITs (very competitive for CSE)
    ("IIIT Hyderabad",              "Telangana",        "IIIT", "JoSAA",   800),
    ("IIIT Allahabad",              "Uttar Pradesh",    "IIIT", "JoSAA",  2800),
    ("ABV-IIITM Gwalior",          "Madhya Pradesh",   "IIIT", "JoSAA",  4500),
    ("IIITDM Jabalpur",            "Madhya Pradesh",   "IIIT", "JoSAA",  6500),
    ("IIITDM Kancheepuram",        "Tamil Nadu",       "IIIT", "JoSAA",  7200),
    # Mid IIITs
    ("IIIT Kurnool",               "Andhra Pradesh",   "IIIT", "JoSAA",  9000),
    ("IIIT Sri City",              "Andhra Pradesh",   "IIIT", "JoSAA",  9500),
    ("IIIT Vadodara",              "Gujarat",          "IIIT", "JoSAA", 10500),
    ("IIIT Lucknow",               "Uttar Pradesh",    "IIIT", "JoSAA", 11000),
    ("IIIT Dharwad",               "Karnataka",        "IIIT", "JoSAA", 11800),
    ("IIIT Kalyani",               "West Bengal",      "IIIT", "JoSAA", 12500),
    ("IIIT Una",                   "Himachal Pradesh", "IIIT", "JoSAA", 13200),
    ("IIIT Ranchi",                "Jharkhand",        "IIIT", "JoSAA", 14000),
    ("IIIT Pune",                  "Maharashtra",      "IIIT", "JoSAA", 14800),
    ("IIIT Nagpur",                "Maharashtra",      "IIIT", "JoSAA", 15500),
    ("IIIT Bhagalpur",             "Bihar",            "IIIT", "JoSAA", 16500),
    ("IIIT Bhopal",                "Madhya Pradesh",   "IIIT", "JoSAA", 17200),
    ("IIIT Srirangam",             "Tamil Nadu",       "IIIT", "JoSAA", 18000),
    ("IIIT Kota",                  "Rajasthan",        "IIIT", "JoSAA", 19000),
    ("IIIT Surat",                 "Gujarat",          "IIIT", "JoSAA", 19800),
    ("IIIT Sonepat",               "Haryana",          "IIIT", "JoSAA", 21000),
    ("IIIT Manipur",               "Manipur",          "IIIT", "JoSAA", 24000),
    ("IIIT Agartala",              "Tripura",          "IIIT", "JoSAA", 26000),
    ("IIIT Raichur",               "Karnataka",        "IIIT", "JoSAA", 28000),
    ("IIIT Naya Raipur",           "Chhattisgarh",     "IIIT", "JoSAA", 30000),
    ("IIIT Vadodara ICD",          "Gujarat",          "IIIT", "JoSAA", 32000),
]

GFTIS = [
    # Well-known GFTIs
    ("IIEST Shibpur",                   "West Bengal",          "GFTI", "JoSAA",  6500),
    ("BIT Mesra",                       "Jharkhand",            "GFTI", "JoSAA",  8000),
    ("Tezpur University",               "Assam",                "GFTI", "JoSAA", 10000),
    ("SLIET Longowal",                  "Punjab",               "GFTI", "JoSAA", 12000),
    ("NIFFT Ranchi",                    "Jharkhand",            "GFTI", "JoSAA", 13500),
    ("Pondicherry Engineering College", "Puducherry",           "GFTI", "JoSAA", 15000),
    ("HBTU Kanpur",                     "Uttar Pradesh",        "GFTI", "JoSAA", 16000),
    ("Assam University",                "Assam",                "GFTI", "JoSAA", 17500),
    ("Mizoram University",              "Mizoram",              "GFTI", "JoSAA", 19000),
    ("Tripura University",              "Tripura",              "GFTI", "JoSAA", 20000),
    # State GFTIs
    ("Government College of Engineering Pune",    "Maharashtra",   "GFTI", "CSAB", 14000),
    ("Coimbatore Institute of Technology",        "Tamil Nadu",    "GFTI", "CSAB", 15500),
    ("PEC University of Technology",              "Chandigarh",    "GFTI", "CSAB", 11000),
    ("GSFC University",                           "Gujarat",       "GFTI", "CSAB", 18000),
    ("Jamia Millia Islamia",                      "Delhi",         "GFTI", "JoSAA", 13000),
    ("Aligarh Muslim University",                 "Uttar Pradesh", "GFTI", "JoSAA", 14500),
    ("BMS College of Engineering",                "Karnataka",     "GFTI", "CSAB", 16000),
    ("Government Engineering College Thrissur",   "Kerala",        "GFTI", "CSAB", 17000),
    ("Dr. B.C. Roy Engineering College",          "West Bengal",   "GFTI", "CSAB", 19000),
    ("Sardar Vallabhbhai NIT",                    "Gujarat",       "GFTI", "JoSAA", 10800),  # (SVNIT already but different branch structure)
    ("MIT Manipal",                               "Karnataka",     "GFTI", "CSAB", 12500),
    ("Madan Mohan Malaviya Univ of Technology",   "Uttar Pradesh", "GFTI", "JoSAA", 15000),
    ("GH Raisoni College of Engineering",         "Maharashtra",   "GFTI", "CSAB", 20000),
    ("Rajasthan Technical University",            "Rajasthan",     "GFTI", "CSAB", 21000),
    ("Osmania University",                        "Telangana",     "GFTI", "CSAB", 18500),
    ("Indian Institute of Carpet Technology",     "Uttar Pradesh", "GFTI", "JoSAA", 28000),
    ("National Institute of Foundry",             "Jharkhand",     "GFTI", "JoSAA", 22000),
    ("School of Planning and Architecture Delhi", "Delhi",         "GFTI", "JoSAA", 11000),
    ("Guru Ghasidas Vishwavidyalaya",             "Chhattisgarh",  "GFTI", "JoSAA", 19000),
    ("Central University of Rajasthan",           "Rajasthan",     "GFTI", "JoSAA", 20500),
    ("Jawaharlal Nehru University",               "Delhi",         "GFTI", "JoSAA", 13500),
    ("University of Hyderabad",                   "Telangana",     "GFTI", "JoSAA", 14000),
    ("Banaras Hindu University",                  "Uttar Pradesh", "GFTI", "JoSAA",  9500),
    ("Andhra University",                         "Andhra Pradesh","GFTI", "CSAB", 17000),
    ("Amrita Vishwa Vidyapeetham",                "Tamil Nadu",    "GFTI", "CSAB", 16500),
    ("SRM Institute of Science and Technology",   "Tamil Nadu",    "GFTI", "CSAB", 15000),
    ("Visvesvaraya National Institute",           "Odisha",        "GFTI", "CSAB", 19500),
    ("Vellore Institute of Technology",           "Tamil Nadu",    "GFTI", "CSAB", 14500),
    ("Birla Institute of Technology",             "Jharkhand",     "GFTI", "CSAB", 13000),
    ("Thiagarajar College of Engineering",        "Tamil Nadu",    "GFTI", "CSAB", 17500),
    ("College of Engineering Trivandrum",         "Kerala",        "GFTI", "CSAB", 16000),
    ("RV College of Engineering",                 "Karnataka",     "GFTI", "CSAB", 15500),
    ("PSG College of Technology",                 "Tamil Nadu",    "GFTI", "CSAB", 18000),
    ("BIT Sindri",                                "Jharkhand",     "GFTI", "CSAB", 22000),
    ("Maharaja Surajmal Institute of Tech",       "Delhi",         "GFTI", "CSAB", 18500),
    ("Netaji Subhas University of Technology",    "Delhi",         "GFTI", "JoSAA", 12000),
    ("Delhi Technological University",            "Delhi",         "GFTI", "JoSAA", 11500),
    ("Dhirubhai Ambani IICT",                     "Gujarat",       "GFTI", "CSAB", 16500),
    ("NIT Puducherry GFTI Campus",                "Puducherry",    "GFTI", "CSAB", 25000),
    ("Symbiosis Institute of Technology",         "Maharashtra",   "GFTI", "CSAB", 19000),
    ("Army Institute of Technology",              "Maharashtra",   "GFTI", "CSAB", 20000),
    ("Sardar Patel College of Engineering",       "Maharashtra",   "GFTI", "CSAB", 21000),
    ("Thapar Institute of Engineering",           "Punjab",        "GFTI", "CSAB",  9000),
    ("Chandigarh University",                     "Punjab",        "GFTI", "CSAB", 17000),
]

# ---------------------------------------------------------------------------
# 2. BRANCH DEFINITIONS
# Each branch has a competitive multiplier applied to the base CSE rank.
# Higher multiplier = higher (less competitive) closing rank.
# ---------------------------------------------------------------------------

# (branch_name, branch_code, nit_multiplier, iiit_multiplier, gfti_multiplier)
BRANCHES = [
    # NITs and GFTIs have all branches; IIITs are CSE-heavy
    ("Computer Science and Engineering",          "CSE",  1.00, 1.00, 1.00),
    ("Electronics and Communication Engineering", "ECE",  1.80, 1.60, 1.90),
    ("Information Technology",                    "IT",   1.30, 1.20, 1.40),
    ("Electrical Engineering",                    "EE",   2.80, None, 2.90),
    ("Mechanical Engineering",                    "ME",   3.80, None, 3.90),
    ("Civil Engineering",                         "CE",   4.80, None, 5.00),
    ("Chemical Engineering",                      "CHE",  5.50, None, 5.80),
    ("Data Science and Artificial Intelligence",  "DS",   1.10, 1.05, 1.15),
]

# IIITs only offer: CSE, ECE, IT, DS
IIIT_BRANCHES = {"CSE", "ECE", "IT", "DS"}

# GFTIs drop Chemical (only major ones offer it)
GFTI_NO_CHEM = {
    "School of Planning and Architecture Delhi",
    "Mizoram University", "Tripura University", "Assam University",
    "Indian Institute of Carpet Technology", "National Institute of Foundry",
}

# ---------------------------------------------------------------------------
# 3. MULTIPLIERS
# ---------------------------------------------------------------------------

# Category closing rank multipliers relative to OPEN
CATEGORY_MULTIPLIERS = {
    "OPEN":    1.00,
    "EWS":     1.75,
    "OBC-NCL": 2.40,
    "SC":      5.00,
    "ST":      7.50,
}

# Quota:  NITs → HS + OS  |  IIITs/select GFTIs → AI
# HS = Home State quota: slightly less competitive than OS
QUOTA_MULTIPLIERS = {
    "OS": 1.00,   # Other State (base for NITs)
    "HS": 1.30,   # Home State (slightly relaxed cutoff)
    "AI": 1.00,   # All India (base for IIITs)
}

# Seat pool multipliers
SEAT_POOL_MULTIPLIERS = {
    "Gender-Neutral": 1.00,
    "Female-Only":    1.45,   # Female-Only has relaxed cutoffs
}

# Round-wise multipliers: closing rank as fraction of Round 6 closing rank
# Round 1 is the tightest (lowest rank required), Round 6 is most relaxed
ROUND_MULTIPLIERS = {
    1: 0.68,
    2: 0.78,
    3: 0.86,
    4: 0.92,
    5: 0.97,
    6: 1.00,
}

# Year drift: cumulative multiplier vs 2023 (our reference)
# Simulates real trends: cutoffs generally tightening (lower) over years for top institutes
YEAR_MULTIPLIERS = {
    2021: 1.12,   # 2021 was slightly more relaxed
    2022: 1.06,   # 2022 converging
    2023: 1.00,   # reference year
}

# ---------------------------------------------------------------------------
# 4. GENERATION
# ---------------------------------------------------------------------------

MAX_RANK = 100_000   # JEE rank cap

def clamp(val: float, lo: int = 100, hi: int = MAX_RANK) -> int:
    return int(max(lo, min(hi, round(val))))


def add_noise(val: float, frac: float = 0.08) -> float:
    """Add ±frac% random noise to simulate real variation."""
    return val * (1.0 + rng.uniform(-frac, frac))


def closing_rank(base: int, category: str, quota: str, seat_pool: str,
                 round_num: int, year: int) -> int:
    val = base
    val *= CATEGORY_MULTIPLIERS[category]
    val *= QUOTA_MULTIPLIERS[quota]
    val *= SEAT_POOL_MULTIPLIERS[seat_pool]
    val *= ROUND_MULTIPLIERS[round_num]
    val *= YEAR_MULTIPLIERS[year]
    val = add_noise(val, frac=0.07)
    return clamp(val)


def opening_rank(cr: int, round_num: int) -> int:
    """Opening rank ≈ previous round's closing rank, or ~65% for Round 1."""
    if round_num == 1:
        return clamp(cr * rng.uniform(0.55, 0.70))
    # Opening of round N ≈ closing of round N-1 ≈ current_closing × round_prev/round_curr
    ratio = ROUND_MULTIPLIERS[round_num - 1] / ROUND_MULTIPLIERS[round_num]
    return clamp(cr * ratio * rng.uniform(0.92, 1.00))


records = []

for name, state, inst_type, body, base_cse in NITS + IIITS + GFTIS:
    is_iiit = inst_type == "IIIT"
    is_gfti = inst_type == "GFTI"

    # Determine quota set
    if is_iiit:
        quotas = ["AI"]
    else:
        quotas = ["HS", "OS"]

    for branch_name, branch_code, nit_mult, iiit_mult, gfti_mult in BRANCHES:
        # Determine applicability
        if is_iiit:
            if branch_code not in IIIT_BRANCHES:
                continue
            mult = iiit_mult
        elif is_gfti:
            if branch_code == "CHE" and name in GFTI_NO_CHEM:
                continue
            mult = gfti_mult
        else:
            mult = nit_mult

        if mult is None:
            continue   # This branch not offered at this institute type

        branch_base = base_cse * mult

        for year in [2021, 2022, 2023]:
            for quota in quotas:
                for category in CATEGORY_MULTIPLIERS:
                    for seat_pool in ["Gender-Neutral", "Female-Only"]:
                        # Skip Female-Only for ST to avoid extremely high ranks
                        if seat_pool == "Female-Only" and category == "ST":
                            continue

                        for round_num in range(1, 7):
                            cr = closing_rank(branch_base, category, quota,
                                              seat_pool, round_num, year)
                            op = opening_rank(cr, round_num)

                            # Skip if closing rank is unrealistically high
                            if cr > MAX_RANK:
                                continue

                            records.append({
                                "counselling_body": body,
                                "institute_type":   inst_type,
                                "college_name":     name,
                                "branch_name":      branch_name,
                                "state":            state,
                                "category":         category,
                                "quota":            quota,
                                "seat_pool":        seat_pool,
                                "year":             year,
                                "round_number":     round_num,
                                "opening_rank":     op,
                                "closing_rank":     cr,
                            })


# ---------------------------------------------------------------------------
# 5. SAVE
# ---------------------------------------------------------------------------

df = pd.DataFrame(records)

# Final sanity: opening_rank < closing_rank always
df.loc[df["opening_rank"] >= df["closing_rank"], "opening_rank"] = (
    (df.loc[df["opening_rank"] >= df["closing_rank"], "closing_rank"] * 0.70).astype(int)
)

output_path = Path("ml/data/raw/josaa_cutoffs_2021_2023.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Dataset generated: {output_path}")
print(f"Total rows:        {len(df):,}")
print(f"Unique colleges:   {df['college_name'].nunique()}")
print(f"Unique branches:   {df['branch_name'].nunique()}")
print(f"Years:             {sorted(df['year'].unique())}")
print(f"Categories:        {sorted(df['category'].unique())}")
print(f"Quotas:            {sorted(df['quota'].unique())}")
print(f"Seat pools:        {sorted(df['seat_pool'].unique())}")
print(f"\nRank range:        {df['closing_rank'].min():,} – {df['closing_rank'].max():,}")
print(f"\nFile size:         {output_path.stat().st_size / 1024:.1f} KB")
print(f"\nSample (5 rows):")
print(df.sample(5, random_state=1).to_string(index=False))
