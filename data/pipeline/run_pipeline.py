#!/usr/bin/env python3
"""
Pipeline Orchestrator — Engineering Admission Intelligence Platform
===================================================================
Runs the full ETL pipeline from raw data acquisition to ML-ready features.

Stages:
    1  acquire        — Download/reference raw JoSAA data
    2  clean          — Normalize and canonicalize per-year CSVs
    3  validate       — Data quality gate (fails pipeline on critical errors)
    4  merge          — Build master_dataset.csv
    5  eda            — Generate EDA report (HTML)
    6  build_features — Engineer ML features

Usage:
    # Full pipeline (recommended)
    python data/pipeline/run_pipeline.py --all

    # Specific stages
    python data/pipeline/run_pipeline.py --stages 1,2,3

    # Resume from a specific stage (skips earlier stages)
    python data/pipeline/run_pipeline.py --from 3

    # Include synthetic data (useful while waiting for real data)
    python data/pipeline/run_pipeline.py --all --include-synthetic

    # Acquire with a specific strategy
    python data/pipeline/run_pipeline.py --stages 1 --strategy scrape --year 2024
"""

from __future__ import annotations

import argparse
import importlib.util
import logging
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = ROOT / "data" / "pipeline"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] PIPELINE — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline.orchestrator")

# ---------------------------------------------------------------------------
# Stage registry
# ---------------------------------------------------------------------------

ALL_STAGES = {
    1: {"name": "acquire",         "script": "01_acquire.py"},
    2: {"name": "clean",           "script": "02_clean.py"},
    3: {"name": "validate",        "script": "03_validate.py"},
    4: {"name": "merge",           "script": "04_merge.py"},
    5: {"name": "eda",             "script": "05_eda.py"},
    6: {"name": "build_features",  "script": "06_build_features.py"},
}


def print_banner() -> None:
    log.info("=" * 70)
    log.info("  Engineering Admission Intelligence Platform")
    log.info("  JoSAA Data Pipeline — Sprint 1")
    log.info("=" * 70)


def run_stage(stage_num: int, extra_args: list[str] | None = None) -> bool:
    """Run a single pipeline stage as a subprocess. Returns True if successful."""
    stage = ALL_STAGES[stage_num]
    script = PIPELINE_DIR / stage["script"]

    if not script.exists():
        log.error(f"Stage {stage_num} script not found: {script}")
        return False

    args = [sys.executable, str(script)] + (extra_args or [])

    log.info(f"\n{'─' * 70}")
    log.info(f"  STAGE {stage_num}: {stage['name'].upper()}")
    log.info(f"{'─' * 70}")
    log.info(f"  Command: {' '.join(args)}")

    t_start = time.time()
    result = subprocess.run(args, cwd=str(ROOT))
    elapsed = time.time() - t_start

    if result.returncode == 0:
        log.info(f"  ✅ Stage {stage_num} completed in {elapsed:.1f}s")
        return True
    else:
        log.error(f"  ❌ Stage {stage_num} FAILED (exit code {result.returncode}) after {elapsed:.1f}s")
        return False


def parse_stages(stages_str: str) -> list[int]:
    """Parse '1,2,3' or '1-4' or '3' into a list of integers."""
    stages = set()
    for part in stages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            stages.update(range(int(start), int(end) + 1))
        else:
            stages.add(int(part))
    return sorted(s for s in stages if s in ALL_STAGES)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ETL Pipeline Orchestrator — JoSAA Engineering Admission Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    stage_group = parser.add_mutually_exclusive_group(required=True)
    stage_group.add_argument("--all",    action="store_true", help="Run all stages (1–6)")
    stage_group.add_argument("--stages", type=str,            help="Comma-separated stage numbers, e.g. 1,2,3")
    stage_group.add_argument("--from",   type=int, dest="from_stage",
                             metavar="N",                     help="Run from stage N through 6")

    parser.add_argument("--include-synthetic", action="store_true",
                        help="Allow synthetic data through the pipeline")
    parser.add_argument("--strategy", choices=["auto", "official", "kaggle", "synthetic"],
                        default="auto", help="Stage 1 acquisition strategy (default: auto)")
    parser.add_argument("--year", choices=["2023", "2024", "2025", "all"],
                        default="all", help="Stage 1: which year(s) to acquire")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stages that would run without executing them")

    args = parser.parse_args()

    print_banner()

    # Determine which stages to run
    if args.all:
        stages_to_run = list(ALL_STAGES.keys())
    elif args.stages:
        stages_to_run = parse_stages(args.stages)
    else:
        stages_to_run = [s for s in ALL_STAGES if s >= args.from_stage]

    log.info(f"\nStages to run: {stages_to_run}")
    log.info(f"Strategy:      {args.strategy}")
    log.info(f"Year(s):       {args.year}")
    log.info(f"Synthetic:     {'YES (flagged)' if args.include_synthetic else 'NO (skip)'}")

    if args.dry_run:
        log.info("\nDRY RUN — no stages will be executed")
        for num in stages_to_run:
            log.info(f"  Would run: Stage {num} — {ALL_STAGES[num]['name']}")
        return

    # Build per-stage extra args
    stage_args: dict[int, list[str]] = {
        1: ["--year", args.year, "--strategy", args.strategy],
        2: ["--year", args.year] if args.year != "all" else [],
        3: ["--strict"] if not args.include_synthetic else [],
        4: ["--include-synthetic"] if args.include_synthetic else [],
        5: [],
        6: ["--allow-synthetic-training"] if args.include_synthetic else [],
    }

    # Execute
    t_pipeline_start = time.time()
    results: dict[int, bool] = {}

    for stage_num in stages_to_run:
        success = run_stage(stage_num, stage_args.get(stage_num, []))
        results[stage_num] = success

        # Validate is a hard gate — if it fails, stop the pipeline
        if stage_num == 3 and not success and not args.include_synthetic:
            log.error(
                "\n🛑 Validation failed. Pipeline halted.\n"
                "   Fix data quality issues or re-run with --include-synthetic\n"
                "   to allow synthetic data through."
            )
            break

        if not success and stage_num < 4:
            log.error(f"\n🛑 Stage {stage_num} failed. Cannot continue.")
            break

    elapsed_total = time.time() - t_pipeline_start

    # Final summary
    log.info("\n" + "=" * 70)
    log.info("PIPELINE SUMMARY")
    log.info("=" * 70)
    for num in stages_to_run:
        if num in results:
            icon   = "✅" if results[num] else "❌"
            status = "PASS" if results[num] else "FAIL"
        else:
            icon, status = "⏭ ", "SKIPPED"
        log.info(f"  {icon}  Stage {num}: {ALL_STAGES[num]['name']:<20} {status}")

    all_passed = all(results.values()) if results else False
    log.info(f"\n  Total time: {elapsed_total:.1f}s")
    log.info(f"  Overall:    {'✅ SUCCESS' if all_passed else '❌ FAILED'}")

    # Output artifact locations
    if all_passed:
        log.info("\nDeliverables:")
        artifacts = {
            "master_dataset.csv": ROOT / "data" / "master" / "master_dataset.csv",
            "validation_report.json": ROOT / "data" / "reports" / "validation_report.json",
            "eda_report.html": ROOT / "data" / "reports" / "eda_report.html",
            "features.csv": ROOT / "data" / "training" / "features.csv",
        }
        for name, path in artifacts.items():
            exists = path.exists()
            size   = f"({path.stat().st_size / 1024:.0f} KB)" if exists else ""
            icon   = "📄" if exists else "❓"
            log.info(f"  {icon}  {name:<30} {size}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
