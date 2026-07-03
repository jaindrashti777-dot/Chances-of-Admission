"""
Data Pipeline Package
=====================
Production-grade ETL pipeline for JoSAA/CSAB admission data.

Stages:
    01_acquire.py        — Download/reference raw data
    02_clean.py          — Normalize and clean per-year CSVs
    03_validate.py       — Data quality gate
    04_merge.py          — Build master_dataset.csv
    05_eda.py            — Automated EDA report
    06_build_features.py — Feature engineering for ML
    run_pipeline.py      — Orchestrator
"""
