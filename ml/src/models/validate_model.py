import pandas as pd
import joblib
from backend.app.db.session import SessionLocal
from backend.app.prediction.college_recommender import college_recommender
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_predictions():
    # Test 100 random cases from 2023 dataset
    df = pd.read_csv("ml/data/processed/processed_data.csv")
    test_cases = df[df['year'] == 2023].sample(n=100, random_state=42)
    
    pipeline = joblib.load("ml/artifacts/best_model.joblib")
    
    X_test = test_cases.drop(columns=['closing_rank', 'opening_rank'], errors='ignore')
    predictions = pipeline.predict(X_test)
    
    logger.info(f"Generated {len(predictions)} ML predictions on historical holdout.")
    
    # Test recommendations using database
    # Set the DATABASE_URL if it's not set
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///./chances.db"
        
    db = SessionLocal()
    try:
        # Example: MNIT Jaipur, CSE, OPEN, OS. Base closing is ~4900.
        user_rank = 4000
        category = "OPEN"
        quota = "OS"
        recs = college_recommender.get_recommendations(db, user_rank, category, quota)
        
        mnit_found = False
        for r in recs.safe_colleges + recs.target_colleges + recs.dream_colleges:
            if "MNIT" in r.college_name and "Jaipur" in r.college_name:
                mnit_found = True
                logger.info(f"MNIT Jaipur found! Match Type: {r.match_type} (Predicted cut: {r.predicted_closing_rank})")
                break
                
        if not mnit_found:
            logger.warning("MNIT Jaipur was NOT found in recommendations for Rank 4000 OPEN OS.")
            
        # Test Impossible filtering
        user_rank_impossible = 80000
        recs_impossible = college_recommender.get_recommendations(db, user_rank_impossible, "OPEN", "AI") # IIITs
        
        impossible_count = 0
        for r in recs_impossible.dream_colleges:
            if r.predicted_closing_rank < user_rank_impossible * 0.75:
                 logger.error(f"IMPOSSIBLE RECOMMENDATION FOUND: {r.college_name} (Rank needed: {r.predicted_closing_rank})")
                 impossible_count += 1
                 
        if impossible_count == 0:
            logger.info("Impossible recommendations filter works correctly. No wildly unrealistic dreams found.")
        
        logger.info(f"Category fairness check: (Example rank 15000)")
        open_recs = college_recommender.get_recommendations(db, 15000, "OPEN", "OS")
        obc_recs = college_recommender.get_recommendations(db, 15000, "OBC-NCL", "OS")
        sc_recs = college_recommender.get_recommendations(db, 15000, "SC", "OS")
        
        logger.info(f"OPEN Target count: {len(open_recs.target_colleges)}")
        logger.info(f"OBC-NCL Target count: {len(obc_recs.target_colleges)}")
        logger.info(f"SC Target count: {len(sc_recs.target_colleges)}")
        
        logger.info("Validation complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_predictions()
