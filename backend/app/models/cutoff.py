from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from backend.app.db.base_class import Base

class CounsellingBody(Base):
    __tablename__ = "counselling_body"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True) # e.g., JoSAA, CSAB, MHT-CET
    
    cutoffs = relationship("HistoricalCutoff", back_populates="counselling_body")

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True) # e.g., GEN, OBC-NCL, SC, ST, EWS
    
    cutoffs = relationship("HistoricalCutoff", back_populates="category")

class Quota(Base):
    __tablename__ = "quota"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True) # e.g., HS, OS, AI
    
    cutoffs = relationship("HistoricalCutoff", back_populates="quota")

class HistoricalCutoff(Base):
    __tablename__ = "historical_cutoff"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    college_id = Column(Integer, ForeignKey("college.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branch.id", ondelete="CASCADE"), nullable=False)
    counselling_body_id = Column(Integer, ForeignKey("counselling_body.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    quota_id = Column(Integer, ForeignKey("quota.id"), nullable=False)
    
    # Context Data
    year = Column(Integer, nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    seat_pool = Column(String(50), nullable=False) # e.g., Gender-Neutral, Female-Only
    
    # Output Data
    opening_rank = Column(Integer, nullable=True)
    closing_rank = Column(Integer, nullable=True)
    
    # Relationships
    college = relationship("College", back_populates="cutoffs")
    branch = relationship("Branch", back_populates="cutoffs")
    counselling_body = relationship("CounsellingBody", back_populates="cutoffs")
    category = relationship("Category", back_populates="cutoffs")
    quota = relationship("Quota", back_populates="cutoffs")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('college_id', 'branch_id', 'category_id', 'quota_id', 'seat_pool', 'year', 'round_number', name='uix_cutoff_record'),
        Index('ix_cutoff_lookup', 'college_id', 'branch_id', 'category_id', 'quota_id', 'year'),
    )
