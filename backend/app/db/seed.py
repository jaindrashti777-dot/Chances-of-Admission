import logging
from sqlalchemy.orm import Session
from backend.app.models.cutoff import CounsellingBody, Category, Quota

logger = logging.getLogger(__name__)

INITIAL_CATEGORIES = [
    "OPEN", "OPEN (PwD)", "EWS", "EWS (PwD)", 
    "OBC-NCL", "OBC-NCL (PwD)", "SC", "SC (PwD)", "ST", "ST (PwD)"
]

INITIAL_QUOTAS = [
    "AI", "HS", "OS", "GO", "JK", "LA"
]

INITIAL_BODIES = [
    "JoSAA", "CSAB"
]

def seed_reference_data(db: Session) -> None:
    """
    Seed initial reference data into the database.
    This should be run after initial migrations.
    """
    logger.info("Seeding initial reference data...")
    
    # Seed Categories
    for cat_name in INITIAL_CATEGORIES:
        if not db.query(Category).filter(Category.name == cat_name).first():
            db.add(Category(name=cat_name))
            
    # Seed Quotas
    for quota_name in INITIAL_QUOTAS:
        if not db.query(Quota).filter(Quota.name == quota_name).first():
            db.add(Quota(name=quota_name))
            
    # Seed Counselling Bodies
    for body_name in INITIAL_BODIES:
        if not db.query(CounsellingBody).filter(CounsellingBody.name == body_name).first():
            db.add(CounsellingBody(name=body_name))
            
    db.commit()
    logger.info("Reference data seeded successfully.")

if __name__ == "__main__":
    from backend.app.db.session import SessionLocal
    db = SessionLocal()
    seed_reference_data(db)
    db.close()
