"""
API routes for flashcard operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db import get_db
from app.schemas import (
    FlashcardCreate,
    FlashcardUpdate,
    FlashcardResponse,
    FlashcardList,
)
from app.services import FlashcardService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=FlashcardResponse, status_code=201)
def create_flashcard(
    flashcard: FlashcardCreate,
    db: Session = Depends(get_db)
) -> FlashcardResponse:
    """
    Create a new flashcard.
    
    Args:
        flashcard: Flashcard data
        db: Database session
        
    Returns:
        Created flashcard
        
    Raises:
        HTTPException: If word already exists
    """
    try:
        db_flashcard = FlashcardService.create_flashcard(db, flashcard)
        return FlashcardResponse.from_orm(db_flashcard)
    except ValueError as e:
        logger.warning(f"Failed to create flashcard: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats", response_model=dict)
def get_user_flashcard_stats(
    user_id: str = Query(..., description="User ID to get statistics for"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get flashcard statistics for a user including count, limit, and remaining slots.
    
    Args:
        user_id: User ID to get statistics for
        db: Database session
        
    Returns:
        Dictionary with flashcard statistics
    """
    return FlashcardService.get_user_flashcard_stats(db, user_id)


@router.get("/", response_model=FlashcardList)
def get_flashcards(
    user_id: str = Query(..., description="User ID to filter flashcards"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    include_hard: bool = Query(True, description="Include hard to remember cards"),
    db: Session = Depends(get_db)
) -> FlashcardList:
    """
    Get all flashcards for a specific user with pagination.
    
    Args:
        user_id: User ID to filter flashcards
        page: Page number (1-based)
        per_page: Number of items per page
        include_hard: Whether to include hard to remember cards
        db: Database session
        
    Returns:
        Paginated list of flashcards
    """
    skip = (page - 1) * per_page
    
    flashcards = FlashcardService.get_all_flashcards(
        db, user_id=user_id, skip=skip, limit=per_page, include_hard=include_hard
    )
    total = FlashcardService.count_flashcards(db, user_id=user_id, include_hard=include_hard)
    
    return FlashcardList(
        flashcards=[FlashcardResponse.from_orm(card) for card in flashcards],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(
    flashcard_id: str,
    db: Session = Depends(get_db)
) -> FlashcardResponse:
    """
    Get a specific flashcard by ID.
    
    Args:
        flashcard_id: Flashcard ID
        db: Database session
        
    Returns:
        Flashcard data
        
    Raises:
        HTTPException: If flashcard not found
    """
    flashcard = FlashcardService.get_flashcard_by_id(db, flashcard_id)
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    return FlashcardResponse.from_orm(flashcard)


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
def update_flashcard(
    flashcard_id: str,
    flashcard_update: FlashcardUpdate,
    db: Session = Depends(get_db)
) -> FlashcardResponse:
    """
    Update an existing flashcard.
    
    Args:
        flashcard_id: Flashcard ID
        flashcard_update: Update data
        db: Database session
        
    Returns:
        Updated flashcard
        
    Raises:
        HTTPException: If flashcard not found or word conflict
    """
    try:
        updated_flashcard = FlashcardService.update_flashcard(
            db, flashcard_id, flashcard_update
        )
        if not updated_flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        return FlashcardResponse.from_orm(updated_flashcard)
    except ValueError as e:
        logger.warning(f"Failed to update flashcard {flashcard_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a flashcard.
    
    Args:
        flashcard_id: Flashcard ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If flashcard not found
    """
    success = FlashcardService.delete_flashcard(db, flashcard_id)
    if not success:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    return {"message": "Flashcard deleted successfully"}
