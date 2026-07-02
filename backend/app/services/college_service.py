from sqlalchemy.orm import Session
from backend.app.repositories.college import college_repo
from backend.app.schemas.college import CollegeCreate
from backend.app.models.college import College

class CollegeService:
    @staticmethod
    def create_college(db: Session, college_in: CollegeCreate) -> College:
        """
        Service layer handles business transactions.
        """
        existing = college_repo.get_by_name(db, name=college_in.name)
        if existing:
            raise ValueError(f"College with name {college_in.name} already exists.")
            
        try:
            college = college_repo.create(db, obj_in=college_in)
            db.commit()
            db.refresh(college)
            return college
        except Exception:
            db.rollback()
            raise

college_service = CollegeService()
