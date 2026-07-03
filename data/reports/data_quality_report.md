# Data Quality Report

## 1. Dataset Overview
- **Format**: CSV (`master_dataset.csv`)
- **Total Rows**: 235,224
- **Unique Institutes**: 111
- **Unique Branches**: 8

## 2. Missing Values & Duplicates
- **Missing Values**:
  - `nirf_rank`: 2,268 missing
  - `naac_grade`: 6,804 missing
  - *Note: These are valid nulls. Institutes like the School of Planning and Architecture do not participate in the NIRF Engineering rankings.*
  - **All other 24 columns have 0 missing values.**
- **Duplicate Rows**: 0 (Validated via `institute` + `branch` + `category` + `quota` + `seat_pool` + `round` + `year` composite key).
- **Invalid Values**: 0 (No rank inversions where opening rank >= closing rank).

## 3. Distributions
- **Categories**: OPEN, EWS, OBC-NCL, SC, ST
- **Quotas**: AI (All India), HS (Home State), OS (Other State)
- **Seat Pools**: Gender-Neutral, Female-Only
- **Counselling Bodies**: JoSAA, CSAB
- **Institute Types**: NIT, IIIT, GFTI

## 4. Rank Statistics
- **Opening Rank Range**: 326 – 96,999 (Mean: 60,402)
- **Closing Rank Range**: 546 – 100,000 (Mean: 71,079)

## 5. Synthetic Data Assumptions & Strategy
- **Official Rows**: 0
- **Synthetic Rows**: 235,224 (100%)
- **Why were synthetic rows created?**
  During initial prototyping, real JoSAA cutoff data was not readily available in a clean format. A synthetic generator was used to stub out the dataset so the UI and database schemas could be built. However, the ranks are statistically uniform and do not reflect real-world counselling dynamics (e.g., SC closing ranks are artificially inflated to 100,000 for many programs).
- **Can they be replaced with official data?**
  **Yes, immediately.** The newly built ETL pipeline (`data/pipeline/01_acquire.py`) is designed to pull real data. By running `python data/pipeline/run_pipeline.py --all --strategy kaggle` with a valid Kaggle API key, the pipeline will overwrite all synthetic records with official historical data and re-run all validation checks.

## 6. Target Validation
The ML objective has been explicitly redefined. We are **no longer predicting a raw probability percentage**. 
The model is now a **Hybrid Recommendation Engine**:
1. **Rule Engine**: Hard-filters out ineligible programs based on category, gender, state quota, and year.
2. **Rank Scorer**: Calculates a composite score based on rank buffer (safety margin), historical demand trends (tightening/relaxing), and institute tier.
3. **Target Output**: Programs are classified into actionable buckets: `Very Likely`, `Likely`, `Competitive`, and `Ambitious`.
