#!/usr/bin/env python3
"""
Stage 05 — Exploratory Data Analysis
======================================
Generates a self-contained HTML EDA report on the master dataset.

Sections:
    1. Dataset Overview
    2. Coverage — institutes, branches, years, rounds
    3. Rank Distributions — by category, institute type, branch
    4. Year-over-Year Trends — closing rank drift for top institutes
    5. Competitive Pressure — rank_spread analysis
    6. Category Representation
    7. Data Quality Flags

Output:
    data/reports/eda_report.html  (self-contained, no external deps)

Usage:
    python data/pipeline/05_eda.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import base64
from io import BytesIO

# ---------------------------------------------------------------------------
ROOT    = Path(__file__).resolve().parents[2]
MASTER  = ROOT / "data" / "master" / "master_dataset.csv"
REPORTS = ROOT / "data" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] — %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("pipeline.05_eda")

# ---------------------------------------------------------------------------
# Plot style
# ---------------------------------------------------------------------------
PALETTE = {
    "OPEN":     "#4C9BE8",
    "EWS":      "#F5A623",
    "OBC-NCL":  "#7ED321",
    "SC":       "#D0021B",
    "ST":       "#9B59B6",
    "NIT":      "#2E86AB",
    "IIIT":     "#A23B72",
    "GFTI":     "#F18F01",
    "IIT":      "#C73E1D",
}

plt.rcParams.update({
    "figure.facecolor": "#0F172A",
    "axes.facecolor":   "#1E293B",
    "axes.edgecolor":   "#334155",
    "axes.labelcolor":  "#CBD5E1",
    "xtick.color":      "#64748B",
    "ytick.color":      "#64748B",
    "text.color":       "#E2E8F0",
    "grid.color":       "#1E293B",
    "legend.facecolor": "#1E293B",
    "legend.edgecolor": "#334155",
})


def fig_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


# ---------------------------------------------------------------------------
# Plot functions
# ---------------------------------------------------------------------------

def plot_row_dist(df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Dataset Coverage", color="#E2E8F0", fontsize=14, y=1.02)

    # By year
    year_counts = df.groupby("year").size()
    axes[0].bar(year_counts.index.astype(str), year_counts.values,
                color=["#4C9BE8", "#7ED321", "#F5A623"])
    axes[0].set_title("Rows by Year", color="#CBD5E1")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # By institute type
    type_counts = df.groupby("institute_type").size().sort_values(ascending=False)
    colors = [PALETTE.get(t, "#94A3B8") for t in type_counts.index]
    axes[1].bar(type_counts.index, type_counts.values, color=colors)
    axes[1].set_title("Rows by Institute Type", color="#CBD5E1")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # By category
    cat_counts = df.groupby("category").size().sort_values(ascending=False)
    cat_colors = [PALETTE.get(c.split("-")[0], "#94A3B8") for c in cat_counts.index]
    axes[2].bar(cat_counts.index, cat_counts.values, color=cat_colors)
    axes[2].set_title("Rows by Category", color="#CBD5E1")
    axes[2].tick_params(axis="x", rotation=45)
    axes[2].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.tight_layout()
    return fig_to_base64(fig)


def plot_rank_distributions(df: pd.DataFrame) -> str:
    """Closing rank distributions by category (box plot)."""
    base_cats = ["OPEN", "EWS", "OBC-NCL", "SC", "ST"]
    plot_data = [
        df[df["category"] == cat]["closing_rank"].dropna().values
        for cat in base_cats
    ]
    colors = [PALETTE.get(c, "#94A3B8") for c in base_cats]

    fig, ax = plt.subplots(figsize=(12, 5))
    bp = ax.boxplot(
        plot_data,
        tick_labels=base_cats,
        patch_artist=True,
        notch=False,
        showfliers=False,
        medianprops={"color": "#FFFFFF", "linewidth": 2},
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    for element in ["whiskers", "caps"]:
        for item in bp[element]:
            item.set_color("#64748B")

    ax.set_title("Closing Rank Distribution by Category (Round 6, all institutes)",
                 color="#E2E8F0", fontsize=13)
    ax.set_ylabel("Closing Rank", color="#CBD5E1")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Category", color="#CBD5E1")
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_yoy_trends(df: pd.DataFrame) -> str:
    """Year-over-year closing rank trend for top NIT CSE programs."""
    target_branch = "Computer Science and Engineering"
    top_nits = [
        "NIT Tiruchirappalli", "NIT Warangal", "NIT Surathkal",
        "NIT Rourkela", "NIT Calicut", "MNIT Jaipur",
    ]

    subset = df[
        (df["branch_name"] == target_branch) &
        (df["institute_name"].isin(top_nits)) &
        (df["category"] == "OPEN") &
        (df["quota"] == "OS") &
        (df["seat_pool"] == "Gender-Neutral") &
        (df["round_number"] == 6)
    ].copy()

    if subset.empty:
        log.warning("No data for YoY trend plot — skipping")
        return ""

    fig, ax = plt.subplots(figsize=(12, 5))
    years = sorted(subset["year"].unique())

    for i, nit in enumerate(top_nits):
        nit_data = subset[subset["institute_name"] == nit].sort_values("year")
        if nit_data.empty:
            continue
        color = plt.cm.Set2(i / len(top_nits))  # noqa: E1101
        ax.plot(nit_data["year"], nit_data["closing_rank"], marker="o",
                label=nit, color=color, linewidth=2, markersize=6)
        # Annotate last point
        last = nit_data.iloc[-1]
        ax.annotate(f"{int(last['closing_rank']):,}", xy=(last["year"], last["closing_rank"]),
                    fontsize=7, color=color, ha="left", va="bottom")

    ax.set_title("Year-over-Year Closing Rank — Top NITs (CSE, OPEN-OS-GN, Round 6)",
                 color="#E2E8F0", fontsize=12)
    ax.set_xlabel("Year", color="#CBD5E1")
    ax.set_ylabel("Closing Rank (lower = more competitive)", color="#CBD5E1")
    ax.set_xticks(years)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.invert_yaxis()  # lower rank = better
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_competitive_pressure(df: pd.DataFrame) -> str:
    """Rank spread (closing - opening) by branch — lower spread = more competitive."""
    r6 = df[df["round_number"] == 6].copy()
    branch_spread = (
        r6.groupby("branch_name")["rank_spread"]
        .median()
        .sort_values()
        .head(20)
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(branch_spread.index, branch_spread.values, color="#4C9BE8", alpha=0.8)
    ax.set_title("Median Rank Spread by Branch (Round 6)\nLower = More Competitive",
                 color="#E2E8F0", fontsize=12)
    ax.set_xlabel("Closing Rank − Opening Rank", color="#CBD5E1")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_institute_tier_dist(df: pd.DataFrame) -> str:
    """Row count and rank range by institute tier."""
    r6 = df[df["round_number"] == 6]
    tiers = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Count
    tier_counts = r6.groupby("institute_tier").size().reindex(tiers, fill_value=0)
    axes[0].bar(tier_counts.index, tier_counts.values,
                color=["#C73E1D", "#F5A623", "#4C9BE8", "#94A3B8"])
    axes[0].set_title("Records by Institute Tier", color="#CBD5E1")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Median closing rank by tier (OPEN, OS/AI, GN)
    tier_ranks = (
        r6[r6["category"] == "OPEN"]
        .groupby("institute_tier")["closing_rank"]
        .median()
        .reindex(tiers)
    )
    axes[1].bar(tier_ranks.index, tier_ranks.values,
                color=["#C73E1D", "#F5A623", "#4C9BE8", "#94A3B8"])
    axes[1].set_title("Median Closing Rank (OPEN category) by Tier", color="#CBD5E1")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.tight_layout()
    return fig_to_base64(fig)


# ---------------------------------------------------------------------------
# HTML report builder
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JoSAA EDA Report — Engineering Admission Intelligence Platform</title>
<style>
  :root {{
    --bg: #0F172A; --surface: #1E293B; --border: #334155;
    --text: #E2E8F0; --muted: #94A3B8; --accent: #3B82F6;
    --green: #22C55E; --yellow: #F59E0B; --red: #EF4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }}
  header {{ background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-bottom: 1px solid var(--border); padding: 2rem 3rem; }}
  header h1 {{ font-size: 1.75rem; font-weight: 700; color: var(--text); }}
  header p {{ color: var(--muted); margin-top: 0.25rem; }}
  .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem; }}
  .badge-green {{ background: #14532D; color: var(--green); }}
  .badge-yellow {{ background: #78350F; color: var(--yellow); }}
  .badge-red {{ background: #7F1D1D; color: var(--red); }}
  main {{ max-width: 1400px; margin: 0 auto; padding: 2rem 3rem; }}
  section {{ margin-bottom: 3rem; }}
  h2 {{ font-size: 1.25rem; font-weight: 600; color: var(--text); border-left: 3px solid var(--accent); padding-left: 0.75rem; margin-bottom: 1rem; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
  .stat-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.25rem; text-align: center; }}
  .stat-card .value {{ font-size: 1.75rem; font-weight: 700; color: var(--accent); }}
  .stat-card .label {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }}
  .chart-grid {{ display: grid; grid-template-columns: 1fr; gap: 1.5rem; }}
  .chart-grid.two {{ grid-template-columns: 1fr 1fr; }}
  .chart-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.5rem; overflow: hidden; }}
  .chart-card img {{ width: 100%; height: auto; border-radius: 0.5rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ background: var(--border); color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.7rem; padding: 0.6rem 0.75rem; text-align: left; }}
  td {{ padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); }}
  tr:hover td {{ background: rgba(255,255,255,0.03); }}
  .table-container {{ background: var(--surface); border: 1px solid var(--border); border-radius: 0.75rem; overflow: hidden; margin-top: 0.5rem; }}
  .synth-banner {{ background: #78350F; border: 1px solid #F59E0B; border-radius: 0.5rem; padding: 1rem 1.25rem; margin-bottom: 1.5rem; color: #FDE68A; font-size: 0.875rem; }}
  footer {{ text-align: center; padding: 2rem; color: var(--muted); font-size: 0.75rem; border-top: 1px solid var(--border); }}
</style>
</head>
<body>
<header>
  <h1>📊 JoSAA EDA Report <span class="badge badge-{status_badge}">{status_text}</span></h1>
  <p>Engineering Admission Intelligence Platform — Generated {generated_at}</p>
</header>
<main>

{synthetic_banner}

<section>
  <h2>1. Dataset Overview</h2>
  <div class="stats-grid">
    <div class="stat-card"><div class="value">{total_rows}</div><div class="label">Total Records</div></div>
    <div class="stat-card"><div class="value">{n_institutes}</div><div class="label">Unique Institutes</div></div>
    <div class="stat-card"><div class="value">{n_branches}</div><div class="label">Unique Branches</div></div>
    <div class="stat-card"><div class="value">{n_years}</div><div class="label">Years Covered</div></div>
    <div class="stat-card"><div class="value">{n_categories}</div><div class="label">Categories</div></div>
    <div class="stat-card"><div class="value">{min_rank:,}–{max_rank:,}</div><div class="label">Rank Range</div></div>
    <div class="stat-card"><div class="value">{real_pct}%</div><div class="label">Real Data</div></div>
    <div class="stat-card"><div class="value">{file_size_mb} MB</div><div class="label">Dataset Size</div></div>
  </div>
</section>

<section>
  <h2>2. Coverage</h2>
  <div class="chart-grid"><div class="chart-card"><img src="{plot_coverage}" alt="Coverage chart"></div></div>
</section>

<section>
  <h2>3. Closing Rank Distribution by Category</h2>
  <div class="chart-grid"><div class="chart-card"><img src="{plot_ranks}" alt="Rank distribution chart"></div></div>
</section>

<section>
  <h2>4. Year-over-Year Trends — Top NITs (CSE)</h2>
  <div class="chart-grid"><div class="chart-card"><img src="{plot_yoy}" alt="Year-over-year trend chart"></div></div>
</section>

<section>
  <h2>5. Competitive Pressure by Branch</h2>
  <div class="chart-grid"><div class="chart-card"><img src="{plot_pressure}" alt="Competitive pressure chart"></div></div>
</section>

<section>
  <h2>6. Institute Tier Analysis</h2>
  <div class="chart-grid"><div class="chart-card"><img src="{plot_tiers}" alt="Institute tier chart"></div></div>
</section>

<section>
  <h2>7. Top 20 Most Competitive Programs (OPEN, OS/AI, Round 6)</h2>
  <div class="table-container">
    <table>
      <thead><tr><th>#</th><th>Institute</th><th>Branch</th><th>Tier</th><th>Closing Rank (2024)</th></tr></thead>
      <tbody>
        {top_programs_html}
      </tbody>
    </table>
  </div>
</section>

</main>
<footer>Engineering Admission Intelligence Platform · EDA Report · Data sourced from JoSAA official records</footer>
</body>
</html>"""


def build_top_programs_table(df: pd.DataFrame) -> str:
    target = df[
        (df["category"] == "OPEN") &
        (df["quota"].isin(["OS", "AI"])) &
        (df["seat_pool"] == "Gender-Neutral") &
        (df["round_number"] == 6) &
        (df["year"] == df["year"].max())
    ].copy()

    top = target.nsmallest(20, "closing_rank")[
        ["institute_name", "branch_name", "institute_tier", "closing_rank"]
    ]

    rows_html = ""
    for i, row in enumerate(top.itertuples(), start=1):
        rows_html += (
            f"<tr><td>{i}</td>"
            f"<td>{row.institute_name}</td>"
            f"<td>{row.branch_name}</td>"
            f"<td>{row.institute_tier}</td>"
            f"<td>{int(row.closing_rank):,}</td></tr>\n"
        )
    return rows_html


def run_eda() -> None:
    if not MASTER.exists():
        raise FileNotFoundError(
            f"master_dataset.csv not found at {MASTER}. Run 04_merge.py first."
        )

    log.info("Loading master dataset...")
    df = pd.read_csv(MASTER)
    log.info(f"  {len(df):,} rows loaded")

    real_rows  = (df["data_source"] == "REAL").sum() if "data_source" in df else len(df)
    synth_rows = len(df) - real_rows
    has_synthetic = synth_rows > 0

    real_pct = int(100 * real_rows / len(df)) if len(df) > 0 else 0

    file_size_mb = f"{MASTER.stat().st_size / 1024 / 1024:.1f}"

    log.info("Generating plots...")
    plot_coverage = plot_row_dist(df)
    plot_ranks    = plot_rank_distributions(df)
    plot_yoy      = plot_yoy_trends(df)
    plot_pressure = plot_competitive_pressure(df)
    plot_tiers    = plot_institute_tier_dist(df)

    synthetic_banner = (
        '<div class="synth-banner">⚠️ <strong>SYNTHETIC DATA WARNING</strong>: '
        f'{synth_rows:,} rows in this dataset are programmatically generated (not real JoSAA records). '
        'Replace with real data via Kaggle or direct scraping before production use. '
        'All conclusions from this report are for pipeline validation only.</div>'
        if has_synthetic else ""
    )

    top_programs_html = build_top_programs_table(df)

    from datetime import datetime
    status_badge = "yellow" if has_synthetic else "green"
    status_text  = "SYNTHETIC DATA" if has_synthetic else "REAL DATA"

    html = HTML_TEMPLATE.format(
        status_badge=status_badge,
        status_text=status_text,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        synthetic_banner=synthetic_banner,
        total_rows=f"{len(df):,}",
        n_institutes=df["institute_name"].nunique(),
        n_branches=df["branch_name"].nunique(),
        n_years=df["year"].nunique(),
        n_categories=df["category"].nunique(),
        min_rank=int(df["closing_rank"].min()),
        max_rank=int(df["closing_rank"].max()),
        real_pct=real_pct,
        file_size_mb=file_size_mb,
        plot_coverage=plot_coverage,
        plot_ranks=plot_ranks,
        plot_yoy=plot_yoy if plot_yoy else "data:image/png;base64,",
        plot_pressure=plot_pressure,
        plot_tiers=plot_tiers,
        top_programs_html=top_programs_html,
    )

    out_path = REPORTS / "eda_report.html"
    out_path.write_text(html, encoding="utf-8")
    log.info(f"\n✅ EDA report → {out_path}")
    log.info(f"   Open in browser: file:///{out_path.as_posix()}")


if __name__ == "__main__":
    run_eda()
