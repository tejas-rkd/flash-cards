"""
Business logic for flashcard operations.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.models import Flashcard
from app.schemas import FlashcardCreate, FlashcardUpdate
from app.core.config import settings

logger = logging.getLogger(__name__)


class FlashcardService:
    """Service class for flashcard business logic."""
    
    @staticmethod
    def create_flashcard(db: Session, flashcard_data: FlashcardCreate) -> Flashcard:
        """
        Create a new flashcard.
        
        Args:
            db: Database session
            flashcard_data: Flashcard creation data
            
        Returns:
            Created flashcard
            
        Raises:
            ValueError: If word already exists for this user or user has reached flashcard limit
        """
        # Check if user has reached the flashcard limit
        user_flashcard_count = db.query(Flashcard).filter(
            Flashcard.user_id == flashcard_data.user_id
        ).count()
        if user_flashcard_count >= settings.MAX_FLASHCARDS_PER_USER:
            raise ValueError(f"You have reached the maximum limit of {settings.MAX_FLASHCARDS_PER_USER} flashcards per user")
        
        # Check if word already exists for this user
        existing = db.query(Flashcard).filter(
            Flashcard.word == flashcard_data.word,
            Flashcard.user_id == flashcard_data.user_id
        ).first()
        if existing:
            raise ValueError(f"A flashcard with the word '{flashcard_data.word}' already exists for this user")
        
        try:
            db_flashcard = Flashcard(
                word=flashcard_data.word,
                definition=flashcard_data.definition,
                user_id=flashcard_data.user_id,
                bin_number=0,
                incorrect_count=0,
                next_review=datetime.utcnow()
            )
            db.add(db_flashcard)
            db.commit()
            db.refresh(db_flashcard)
            
            logger.info(f"Created flashcard: {flashcard_data.word} for user {flashcard_data.user_id}")
            return db_flashcard
            
        except IntegrityError:
            db.rollback()
            raise ValueError(f"A flashcard with the word '{flashcard_data.word}' already exists for this user")
    
    @staticmethod
    def get_flashcard_by_id(db: Session, flashcard_id: str) -> Optional[Flashcard]:
        """
        Get a flashcard by ID.
        
        Args:
            db: Database session
            flashcard_id: Flashcard ID
            
        Returns:
            Flashcard if found, None otherwise
        """
        return db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    
    @staticmethod
    def get_flashcard_by_word(db: Session, word: str, user_id: str) -> Optional[Flashcard]:
        """
        Get a flashcard by word for a specific user.
        
        Args:
            db: Database session
            word: Word to search for
            user_id: User ID
            
        Returns:
            Flashcard if found, None otherwise
        """
        return db.query(Flashcard).filter(
            Flashcard.word == word,
            Flashcard.user_id == user_id
        ).first()
    
    @staticmethod
    def get_all_flashcards(
        db: Session, 
        user_id: str,
        skip: int = 0, 
        limit: int = 100,
        include_hard: bool = True
    ) -> List[Flashcard]:
        """
        Get all flashcards for a specific user with pagination.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_hard: Whether to include hard to remember cards
            
        Returns:
            List of flashcards
        """
        query = db.query(Flashcard).filter(Flashcard.user_id == user_id)
        
        if not include_hard:
            query = query.filter(Flashcard.is_hard_to_remember == False)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count_flashcards(db: Session, user_id: str, include_hard: bool = True) -> int:
        """
        Count total number of flashcards for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            include_hard: Whether to include hard to remember cards
            
        Returns:
            Total count of flashcards
        """
        query = db.query(Flashcard).filter(Flashcard.user_id == user_id)
        
        if not include_hard:
            query = query.filter(Flashcard.is_hard_to_remember == False)
        
        return query.count()
    
    @staticmethod
    def update_flashcard(
        db: Session, 
        flashcard_id: str, 
        flashcard_data: FlashcardUpdate
    ) -> Optional[Flashcard]:
        """
        Update an existing flashcard.
        
        Args:
            db: Database session
            flashcard_id: ID of flashcard to update
            flashcard_data: Update data
            
        Returns:
            Updated flashcard if successful, None if not found
            
        Raises:
            ValueError: If word already exists for another card
        """
        flashcard = FlashcardService.get_flashcard_by_id(db, flashcard_id)
        if not flashcard:
            return None
        
        update_data = flashcard_data.dict(exclude_unset=True)
        
        # Check for word conflicts if word is being updated
        if "word" in update_data:
            existing = db.query(Flashcard).filter(
                Flashcard.word == update_data["word"],
                Flashcard.user_id == flashcard.user_id,
                Flashcard.id != flashcard_id
            ).first()
            if existing:
                raise ValueError(f"A flashcard with the word '{update_data['word']}' already exists for this user")
        
        try:
            for field, value in update_data.items():
                setattr(flashcard, field, value)
            
            flashcard.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(flashcard)
            
            logger.info(f"Updated flashcard: {flashcard.word}")
            return flashcard
            
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to update flashcard due to constraint violation")
    
    @staticmethod
    def delete_flashcard(db: Session, flashcard_id: str) -> bool:
        """
        Delete a flashcard.
        
        Args:
            db: Database session
            flashcard_id: ID of flashcard to delete
            
        Returns:
            True if deleted, False if not found
        """
        flashcard = FlashcardService.get_flashcard_by_id(db, flashcard_id)
        if not flashcard:
            return False
        
        db.delete(flashcard)
        db.commit()
        
        logger.info(f"Deleted flashcard: {flashcard.word}")
        return True
    
    @staticmethod
    def get_user_flashcard_stats(db: Session, user_id: str) -> dict:
        """
        Get flashcard statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with flashcard count, limit, and remaining slots
        """
        count = db.query(Flashcard).filter(Flashcard.user_id == user_id).count()
        limit = settings.MAX_FLASHCARDS_PER_USER
        remaining = max(0, limit - count)
        
        return {
            "current_count": count,
            "limit": limit,
            "remaining": remaining,
            "at_limit": count >= limit
        }
