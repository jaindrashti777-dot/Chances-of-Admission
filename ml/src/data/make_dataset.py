import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw admissions dataset.
    - Removes duplicates
    - Handles missing values
    - Normalizes string columns
    """
    logger.info(f"Initial shape: {df.shape}")
    
    # Drop full duplicates
    df = df.drop_duplicates()
    
    # Normalize string columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip().str.upper()
        
    # Drop rows where critical output is missing
    df = df.dropna(subset=['closing_rank'])
    
    # Convert ranks to numeric, coercing errors to NaN and filling/dropping
    df['opening_rank'] = pd.to_numeric(df['opening_rank'], errors='coerce')
    df['closing_rank'] = pd.to_numeric(df['closing_rank'], errors='coerce')
    df = df.dropna(subset=['closing_rank', 'opening_rank'])
    
    logger.info(f"Shape after cleaning: {df.shape}")
    return df

def make_dataset(input_path: str, output_path: str):
    """
    Reads raw data, cleans it, and saves the processed data.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        logger.error(f"Input file {input_path} not found.")
        return
        
    df = pd.read_csv(input_file)
    df_clean = clean_data(df)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_file, index=False)
    logger.info(f"Processed dataset saved to {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    make_dataset("ml/data/raw/raw_data.csv", "ml/data/processed/processed_data.csv")
