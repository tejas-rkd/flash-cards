"""
API routes for study session operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.db import get_db
from app.schemas import (
    FlashcardResponse,
    ReviewRequest,
    StudyStatusResponse,
)
from app.services import StudyService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/next", response_model=FlashcardResponse)
def get_next_card(
    user_id: str = Query(..., description="User ID to get next card for"),
    db: Session = Depends(get_db)
) -> FlashcardResponse:
    """
    Get the next card for review for a specific user based on spaced repetition algorithm.
    
    Args:
        user_id: User ID to get next card for
        db: Database session
        
    Returns:
        Next flashcard to review
        
    Raises:
        HTTPException: If no cards are available for review
    """
    card = StudyService.get_next_card_for_review(db, user_id)
    if not card:
        raise HTTPException(
            status_code=404, 
            detail="No cards available for review"
        )
    
    return FlashcardResponse.from_orm(card)


@router.post("/{card_id}/review", response_model=FlashcardResponse)
def review_card(
    card_id: str,
    review: ReviewRequest,
    db: Session = Depends(get_db)
) -> FlashcardResponse:
    """
    Submit a review for a flashcard.
    
    Args:
        card_id: ID of the card being reviewed
        review: Review data (correct/incorrect)
        db: Database session
        
    Returns:
        Updated flashcard with new spaced repetition data
        
    Raises:
        HTTPException: If card not found
    """
    updated_card = StudyService.update_card_after_review(
        db, card_id, review.correct
    )
    
    if not updated_card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return FlashcardResponse.from_orm(updated_card)


@router.get("/status", response_model=StudyStatusResponse)
def get_study_status(
    user_id: str = Query(..., description="User ID to get study status for"),
    db: Session = Depends(get_db)
) -> StudyStatusResponse:
    """
    Get current study session status for a specific user.
    
    Args:
        user_id: User ID to get study status for
        db: Database session
        
    Returns:
        Comprehensive study status with card counts and availability
    """
    return StudyService.get_study_status(db, user_id)
