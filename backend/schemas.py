from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FlashcardCreate(BaseModel):
    word: str
    definition: str

class FlashcardResponse(BaseModel):
    id: str
    word: str
    definition: str
    bin_number: int
    incorrect_count: int
    next_review: datetime
    is_hard_to_remember: bool
    
    class Config:
        from_attributes = True

class ReviewRequest(BaseModel):
    correct: bool

class StatusResponse(BaseModel):
    message: str
    has_cards: bool
