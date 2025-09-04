"""
Pydantic schemas for flashcard operations.
"""
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional


class FlashcardBase(BaseModel):
    """Base schema for flashcard data."""
    word: str = Field(..., min_length=1, max_length=255, description="The word to learn")
    definition: str = Field(..., min_length=1, max_length=2000, description="Definition of the word")
    user_id: str = Field(..., description="ID of the user who owns this flashcard")
    
    @validator('word')
    def word_must_not_be_empty(cls, v):
        """Ensure word is not just whitespace."""
        if not v.strip():
            raise ValueError('Word cannot be empty or just whitespace')
        return v.strip()
    
    @validator('definition')
    def definition_must_not_be_empty(cls, v):
        """Ensure definition is not just whitespace."""
        if not v.strip():
            raise ValueError('Definition cannot be empty or just whitespace')
        return v.strip()


class FlashcardCreate(FlashcardBase):
    """Schema for creating a new flashcard."""
    pass


class FlashcardUpdate(BaseModel):
    """Schema for updating an existing flashcard."""
    word: Optional[str] = Field(None, min_length=1, max_length=255)
    definition: Optional[str] = Field(None, min_length=1, max_length=2000)
    user_id: Optional[str] = Field(None, description="ID of the user who owns this flashcard")
    
    @validator('word')
    def word_must_not_be_empty(cls, v):
        """Ensure word is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Word cannot be empty or just whitespace')
        return v.strip() if v else v
    
    @validator('definition')
    def definition_must_not_be_empty(cls, v):
        """Ensure definition is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Definition cannot be empty or just whitespace')
        return v.strip() if v else v


class FlashcardResponse(FlashcardBase):
    """Schema for flashcard responses."""
    id: str = Field(..., description="Unique identifier for the flashcard")
    bin_number: int = Field(..., ge=0, le=11, description="Current spaced repetition bin (0-11)")
    incorrect_count: int = Field(..., ge=0, description="Number of incorrect attempts")
    next_review: datetime = Field(..., description="When this card should be reviewed next")
    created_at: datetime = Field(..., description="When the card was created")
    updated_at: Optional[datetime] = Field(None, description="When the card was last updated")
    is_hard_to_remember: bool = Field(False, description="Whether this card is marked as hard to remember")
    
    class Config:
        from_attributes = True


class FlashcardList(BaseModel):
    """Schema for paginated flashcard lists."""
    flashcards: list[FlashcardResponse]
    total: int = Field(..., ge=0, description="Total number of flashcards")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.per_page - 1) // self.per_page
