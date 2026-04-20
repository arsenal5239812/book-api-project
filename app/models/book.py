from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=False, index=True)
    published_year = Column(Integer, nullable=True)
    average_rating = Column(Float, default=0.0)
    ratings_count = Column(Integer, default=0, nullable=False)
    isbn13 = Column(String(20), nullable=True, index=True)
    language_code = Column(String(10), nullable=True, index=True)
    source = Column(String(50), nullable=False, default="manual", index=True)
    origin_type = Column(String(30), nullable=False, default="unknown", index=True)
    source_platform = Column(String(30), nullable=False, default="manual", index=True)
    original_language = Column(String(10), nullable=True, index=True)
    translation_status = Column(String(20), nullable=False, default="unknown", index=True)
    creation_disclosure = Column(String(20), nullable=False, default="unknown", index=True)
    disclosure_source = Column(String(30), nullable=True)
    moderation_status = Column(String(20), nullable=False, default="unreviewed", index=True)
    ai_risk_score = Column(Float, nullable=True)
    provenance_notes = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
