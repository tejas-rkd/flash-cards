"""
Database models for user management.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship

# Import Base from flashcard module to avoid circular imports
from app.models.flashcard import Base


class User(Base):
    """User model for managing flashcard users."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User details
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to flashcards
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User(id='{self.id}', name='{self.name}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.name
