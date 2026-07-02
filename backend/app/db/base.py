# Import all the models, so that Base has them before being
# imported by Alembic
from backend.app.db.base_class import Base

from backend.app.models.college import College, Branch, CollegeBranch
from backend.app.models.cutoff import CounsellingBody, Category, Quota, HistoricalCutoff
