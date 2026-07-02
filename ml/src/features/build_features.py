from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
import pandas as pd
import joblib
import logging

logger = logging.getLogger(__name__)

def get_feature_pipeline() -> ColumnTransformer:
    """
    Creates and returns the feature engineering pipeline.
    """
    # Define feature groups
    categorical_features = ['institute_type', 'category', 'quota', 'seat_pool', 'counselling_body']
    # If there are many colleges/branches, TargetEncoding or OrdinalEncoding might be better
    ordinal_features = ['college_name', 'branch_name'] 
    numeric_features = ['year', 'round_number']
    
    # Numeric pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Categorical pipeline (OneHot)
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='UNKNOWN')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # High-cardinality categorical pipeline (Ordinal)
    ordinal_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='UNKNOWN')),
        ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features),
            ('ord', ordinal_transformer, ordinal_features)
        ],
        remainder='drop' # Drop any other columns like 'opening_rank' if passed
    )
    
    return preprocessor

def build_features(df: pd.DataFrame, fit: bool = True, save_path: str = None) -> pd.DataFrame:
    """
    Applies feature engineering. If fit=True, trains the preprocessor and optionally saves it.
    """
    preprocessor = get_feature_pipeline()
    
    if fit:
        X_transformed = preprocessor.fit_transform(df)
        if save_path:
            joblib.dump(preprocessor, save_path)
            logger.info(f"Preprocessor saved to {save_path}")
    else:
        # Load from path
        if not save_path:
            raise ValueError("save_path must be provided if fit=False")
        preprocessor = joblib.load(save_path)
        X_transformed = preprocessor.transform(df)
        
    return X_transformed
