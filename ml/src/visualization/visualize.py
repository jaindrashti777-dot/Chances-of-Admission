import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_eda_reports(df: pd.DataFrame, output_dir: str):
    """
    Generates Exploratory Data Analysis plots and saves them.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Distribution of Closing Ranks
    plt.figure(figsize=(10, 6))
    sns.histplot(df['closing_rank'], bins=50, kde=True)
    plt.title('Distribution of Closing Ranks')
    plt.xlabel('Closing Rank')
    plt.ylabel('Frequency')
    plt.savefig(out_path / 'closing_rank_distribution.png')
    plt.close()
    
    # 2. Correlation Matrix for numericals
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    if not numeric_df.empty:
        plt.figure(figsize=(8, 6))
        sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Matrix')
        plt.savefig(out_path / 'correlation_matrix.png')
        plt.close()
        
    # 3. Category Distribution
    if 'category' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(y='category', data=df, order=df['category'].value_counts().index)
        plt.title('Category Distribution')
        plt.savefig(out_path / 'category_distribution.png')
        plt.close()
        
    logger.info(f"EDA reports saved to {output_dir}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        df = pd.read_csv("ml/data/processed/processed_data.csv")
        generate_eda_reports(df, "ml/reports/eda")
    except FileNotFoundError:
        logger.warning("Processed data not found. Run make_dataset.py first.")
