import pytest
import pandas as pd
from ml.src.data.make_dataset import clean_data

def test_data_cleaning():
    # Mock raw data with duplicates and missing closing ranks
    data = {
        'college_name': ['NIT A', 'NIT A', 'NIT B'],
        'closing_rank': [1000, 1000, None],
        'opening_rank': [500, 500, 200]
    }
    df = pd.DataFrame(data)
    
    cleaned_df = clean_data(df)
    
    # Duplicate removed, missing closing_rank removed
    assert len(cleaned_df) == 1
    assert cleaned_df.iloc[0]['college_name'] == 'NIT A'
    assert cleaned_df.iloc[0]['closing_rank'] == 1000.0

# Add more tests here for feature pipeline and model inference
