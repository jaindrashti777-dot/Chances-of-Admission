from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List

from backend.app.repositories.base import CRUDBase
from backend.app.models.college import College, Branch
from backend.app.schemas.college import CollegeCreate, CollegeUpdate, BranchCreate, BranchUpdate

class CRUDCollege(CRUDBase[College, CollegeCreate, CollegeUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[College]:
        stmt = select(self.model).where(self.model.name == name)
        return db.scalar(stmt)
        
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[College]:
        stmt = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        return db.scalars(stmt).all()

class CRUDBranch(CRUDBase[Branch, BranchCreate, BranchUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Branch]:
        stmt = select(self.model).where(self.model.name == name)
        return db.scalar(stmt)

college_repo = CRUDCollege(College)
branch_repo = CRUDBranch(Branch)
