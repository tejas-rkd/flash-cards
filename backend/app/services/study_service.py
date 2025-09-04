"""
Business logic for study session operations.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.models import Flashcard
from app.schemas import StudyStatusResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class StudyService:
    """Service class for study session business logic."""
    
    @staticmethod
    def get_next_card_for_review(db: Session, user_id: str) -> Optional[Flashcard]:
        """
        Get the next card for review for a specific user based on spaced repetition logic.
        
        Priority order:
        1. Cards in higher bins that are ready for review (descending bin order)
        2. New cards from bin 0
        
        Args:
            db: Database session
            user_id: User ID to filter by
            
        Returns:
            Next flashcard to review, or None if no cards available
        """
        now = datetime.utcnow()
        
        # First, check for cards in bins 1-10 that are ready for review
        # Order by bin_number descending to prioritize higher bins
        ready_card = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.bin_number >= 1,
            Flashcard.bin_number < 11,  # Exclude completed cards (bin 11)
            Flashcard.next_review <= now,
            Flashcard.is_hard_to_remember == False
        ).order_by(Flashcard.bin_number.desc()).first()
        
        if ready_card:
            logger.info(f"Found ready card: {ready_card.word} (bin {ready_card.bin_number}) for user {user_id}")
            return ready_card
        
        # If no ready cards, get a new card from bin 0
        new_card = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.bin_number == 0,
            Flashcard.is_hard_to_remember == False
        ).first()
        
        if new_card:
            logger.info(f"Found new card: {new_card.word} for user {user_id}")
        else:
            logger.info(f"No cards available for review for user {user_id}")
            
        return new_card
    
    @staticmethod
    def update_card_after_review(
        db: Session, 
        card_id: str, 
        correct: bool
    ) -> Optional[Flashcard]:
        """
        Update a card after review based on spaced repetition algorithm.
        
        Algorithm:
        - Correct answer: Move to next bin (max 11)
        - Incorrect answer: Increment error count, move to bin 1 (or mark hard if 10+ errors)
        
        Args:
            db: Database session
            card_id: ID of the card being reviewed
            correct: Whether the answer was correct
            
        Returns:
            Updated flashcard, or None if not found
        """
        card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
        if not card:
            logger.warning(f"Card not found for review: {card_id}")
            return None
        
        old_bin = card.bin_number
        
        if correct:
            # Move to next bin (max 11)
            if card.bin_number < 11:
                card.bin_number += 1
                logger.info(f"Card '{card.word}' promoted from bin {old_bin} to {card.bin_number}")
        else:
            # Increment incorrect count
            card.incorrect_count += 1
            
            # Check if card should be marked as hard to remember
            if card.incorrect_count >= settings.MAX_INCORRECT_COUNT:
                card.is_hard_to_remember = True
                logger.info(f"Card '{card.word}' marked as hard to remember ({card.incorrect_count} errors)")
            else:
                # Move back to bin 1 (unless already in bin 0)
                if card.bin_number > 0:
                    card.bin_number = 1
                    logger.info(f"Card '{card.word}' demoted from bin {old_bin} to bin 1")
        
        # Calculate next review time
        card.next_review = StudyService._calculate_next_review_time(card.bin_number)
        card.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(card)
        
        return card
    
    @staticmethod
    def _calculate_next_review_time(bin_number: int) -> datetime:
        """
        Calculate the next review time based on bin number.
        
        Args:
            bin_number: Current bin number (0-11)
            
        Returns:
            Next review datetime
        """
        if bin_number == 0:
            # New cards are available immediately
            return datetime.utcnow()
        elif bin_number == 11:
            # Completed cards - never review again (far future)
            return datetime.utcnow() + timedelta(days=365 * 100)
        else:
            # Use configured timespan for the bin
            timespan_seconds = settings.BIN_TIMESPANS.get(bin_number, 86400)  # Default to 1 day
            return datetime.utcnow() + timedelta(seconds=timespan_seconds)
    
    @staticmethod
    def get_study_status(db: Session, user_id: str) -> StudyStatusResponse:
        """
        Get comprehensive study session status for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            
        Returns:
            Study status with detailed counts and message
        """
        now = datetime.utcnow()
        
        # Count cards ready for review (bins 1-10, ready now)
        ready_cards_count = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.bin_number >= 1,
            Flashcard.bin_number < 11,
            Flashcard.next_review <= now,
            Flashcard.is_hard_to_remember == False
        ).count()
        
        # Count new cards (bin 0)
        new_cards_count = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.bin_number == 0,
            Flashcard.is_hard_to_remember == False
        ).count()
        
        # Count total active cards (not hard to remember, not completed)
        total_active_cards = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.is_hard_to_remember == False,
            Flashcard.bin_number < 11
        ).count()
        
        # Count completed cards (bin 11)
        completed_cards = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.bin_number == 11,
            Flashcard.is_hard_to_remember == False
        ).count()
        
        # Count hard to remember cards
        hard_cards = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.is_hard_to_remember == True
        ).count()
        
        # Generate status message
        if ready_cards_count > 0 or new_cards_count > 0:
            message = f"Ready to review: {ready_cards_count} cards, New cards: {new_cards_count}"
            has_cards = True
        elif total_active_cards > 0:
            message = "You are temporarily done; please come back later to review more words."
            has_cards = False
        else:
            message = "You have no more words to review; you are permanently done!"
            has_cards = False
        
        return StudyStatusResponse(
            message=message,
            has_cards=has_cards,
            ready_cards_count=ready_cards_count,
            new_cards_count=new_cards_count,
            total_active_cards=total_active_cards,
            completed_cards=completed_cards,
            hard_cards=hard_cards
        )
