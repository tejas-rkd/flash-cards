"""
Database models for flashcard application.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Flashcard(Base):
    """Flashcard model for storing vocabulary words and their progress."""
    
    __tablename__ = "flashcards"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to user
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    
    # Core content
    word = Column(String(255), nullable=False, index=True)
    definition = Column(Text, nullable=False)
    
    # Spaced repetition fields
    bin_number = Column(Integer, default=0, nullable=False, index=True)
    incorrect_count = Column(Integer, default=0, nullable=False)
    next_review = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_hard_to_remember = Column(Boolean, default=False, nullable=False, index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="flashcards")
    
    def __repr__(self) -> str:
        """String representation of flashcard."""
        return f"<Flashcard(id='{self.id}', word='{self.word}', bin={self.bin_number})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.word}: {self.definition[:50]}..."
