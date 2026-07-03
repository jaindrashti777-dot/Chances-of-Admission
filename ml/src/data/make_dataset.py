import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and validates the raw admissions dataset.
    """
    logger.info(f"Initial shape: {df.shape}")
    
    # Drop full duplicates
    df = df.drop_duplicates()
    
    # Normalize string columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Standardize categories and quotas
    valid_categories = ['OPEN', 'EWS', 'OBC-NCL', 'SC', 'ST']
    valid_quotas = ['HS', 'OS', 'AI']
    
    df = df[df['category'].isin(valid_categories)]
    df = df[df['quota'].isin(valid_quotas)]
    
    # Convert ranks to numeric, coercing errors to NaN and dropping
    df['opening_rank'] = pd.to_numeric(df['opening_rank'], errors='coerce')
    df['closing_rank'] = pd.to_numeric(df['closing_rank'], errors='coerce')
    df = df.dropna(subset=['closing_rank', 'opening_rank'])
    
    # Validate ranks
    df = df[(df['opening_rank'] > 0) & (df['closing_rank'] > 0)]
    df = df[df['closing_rank'] >= df['opening_rank']]
    
    # Ensure correct data types
    df['opening_rank'] = df['opening_rank'].astype(int)
    df['closing_rank'] = df['closing_rank'].astype(int)
    df['year'] = df['year'].astype(int)
    df['round_number'] = df['round_number'].astype(int)
    
    logger.info(f"Shape after cleaning and validation: {df.shape}")
    return df

def generate_eda_stats(df: pd.DataFrame, output_dir: Path):
    """Generates basic EDA statistics and saves to JSON."""
    stats = {
        "total_records": len(df),
        "unique_colleges": int(df['college_name'].nunique()),
        "unique_branches": int(df['branch_name'].nunique()),
        "years": sorted([int(y) for y in df['year'].unique()]),
        "categories_distribution": df['category'].value_counts().to_dict(),
        "quotas_distribution": df['quota'].value_counts().to_dict(),
        "rank_percentiles": {
            "25th": float(df['closing_rank'].quantile(0.25)),
            "50th": float(df['closing_rank'].median()),
            "75th": float(df['closing_rank'].quantile(0.75)),
            "90th": float(df['closing_rank'].quantile(0.90)),
            "max": float(df['closing_rank'].max())
        }
    }
    
    output_dir.mkdir(parents=True, exist_ok=True)
    stats_file = output_dir / "data_quality.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)
    logger.info(f"EDA stats saved to {stats_file}")

def make_dataset(input_dir: str, output_dir: str, reports_dir: str):
    """
    Reads raw data, cleans it, generates stats, and saves versioned processed data.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    reports_path = Path(reports_dir)
    
    # Merge all CSVs in raw directory (simulating multi-year merge)
    all_files = list(input_path.glob("*.csv"))
    if not all_files:
        logger.error(f"No CSV files found in {input_dir}")
        return
        
    logger.info(f"Found {len(all_files)} raw files to merge.")
    df_list = [pd.read_csv(f) for f in all_files]
    df_merged = pd.concat(df_list, ignore_index=True)
    
    df_clean = validate_and_clean_data(df_merged)
    
    # EDA
    generate_eda_stats(df_clean, reports_path)
    
    # Versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_filename = f"dataset_{timestamp}.csv"
    output_path.mkdir(parents=True, exist_ok=True)
    
    final_output_file = output_path / versioned_filename
    df_clean.to_csv(final_output_file, index=False)
    
    # Update latest pointer (registry)
    registry_file = output_path / "latest.json"
    registry_info = {
        "latest_version": versioned_filename,
        "created_at": datetime.now().isoformat(),
        "rows": len(df_clean)
    }
    with open(registry_file, 'w') as f:
        json.dump(registry_info, f, indent=4)
        
    # Also save a stable 'processed_data.csv' for easy loading by other scripts
    # or they can read from registry
    df_clean.to_csv(output_path / "processed_data.csv", index=False)
        
    logger.info(f"Versioned dataset saved to {final_output_file}")
    logger.info(f"Registry updated.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    make_dataset("ml/data/raw", "ml/data/processed", "ml/reports/data")
