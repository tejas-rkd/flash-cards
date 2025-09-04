"""
Pydantic schemas for study session operations.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ReviewRequest(BaseModel):
    """Schema for submitting a card review."""
    correct: bool = Field(..., description="Whether the user answered correctly")


class StudyStatusResponse(BaseModel):
    """Schema for study session status."""
    message: str = Field(..., description="Human-readable status message")
    has_cards: bool = Field(..., description="Whether there are cards available for study")
    ready_cards_count: int = Field(..., ge=0, description="Number of cards ready for immediate review")
    new_cards_count: int = Field(..., ge=0, description="Number of new cards (bin 0)")
    total_active_cards: int = Field(..., ge=0, description="Total number of active cards (not hard to remember)")
    completed_cards: int = Field(..., ge=0, description="Number of completed cards (bin 11)")
    hard_cards: int = Field(..., ge=0, description="Number of hard to remember cards")


class StudySessionStats(BaseModel):
    """Schema for study session statistics."""
    cards_reviewed: int = Field(..., ge=0, description="Number of cards reviewed in this session")
    correct_answers: int = Field(..., ge=0, description="Number of correct answers")
    incorrect_answers: int = Field(..., ge=0, description="Number of incorrect answers")
    session_duration_minutes: Optional[int] = Field(None, ge=0, description="Session duration in minutes")
    
    @property
    def accuracy_percentage(self) -> float:
        """Calculate accuracy percentage."""
        total = self.correct_answers + self.incorrect_answers
        if total == 0:
            return 0.0
        return round((self.correct_answers / total) * 100, 2)
