from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base_class import Base

class College(Base):
    __tablename__ = "college"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    state = Column(String(100), nullable=False, index=True)
    institute_type = Column(String(50), nullable=False, index=True) # e.g. NIT, IIIT, GFTI
    is_active = Column(Boolean, default=True)
    
    # Relationships
    branches = relationship("CollegeBranch", back_populates="college", cascade="all, delete-orphan")
    cutoffs = relationship("HistoricalCutoff", back_populates="college")

class Branch(Base):
    __tablename__ = "branch"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=True) # Optional standard code
    
    # Relationships
    colleges = relationship("CollegeBranch", back_populates="branch", cascade="all, delete-orphan")
    cutoffs = relationship("HistoricalCutoff", back_populates="branch")

class CollegeBranch(Base):
    __tablename__ = "college_branch"
    
    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("college.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branch.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationships
    college = relationship("College", back_populates="branches")
    branch = relationship("Branch", back_populates="colleges")
