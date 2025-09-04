from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from database import Flashcard

# Bin timespans in seconds
BIN_TIMESPANS = {
    1: 5,           # 5 seconds
    2: 25,          # 25 seconds  
    3: 120,         # 2 minutes
    4: 600,         # 10 minutes
    5: 3600,        # 1 hour
    6: 18000,       # 5 hours
    7: 86400,       # 1 day
    8: 432000,      # 5 days
    9: 2160000,     # 25 days
    10: 10368000,   # 4 months (120 days)
    11: float('inf') # never
}

def create_flashcard(db: Session, word: str, definition: str) -> Flashcard:
    """Create a new flashcard."""
    db_card = Flashcard(
        word=word,
        definition=definition,
        bin_number=0,
        incorrect_count=0,
        next_review=datetime.utcnow()
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

def get_all_flashcards(db: Session) -> List[Flashcard]:
    """Get all flashcards."""
    return db.query(Flashcard).all()

def get_next_card_for_review(db: Session) -> Optional[Flashcard]:
    """Get the next card for review based on spaced repetition logic."""
    now = datetime.utcnow()
    
    # First, check for cards in bins 1-11 that are ready for review
    ready_cards = db.query(Flashcard).filter(
        Flashcard.bin_number >= 1,
        Flashcard.bin_number <= 11,
        Flashcard.next_review <= now,
        Flashcard.is_hard_to_remember == False
    ).order_by(Flashcard.bin_number.desc()).all()
    
    if ready_cards:
        return ready_cards[0]
    
    # If no ready cards, get a new card from bin 0
    new_card = db.query(Flashcard).filter(
        Flashcard.bin_number == 0,
        Flashcard.is_hard_to_remember == False
    ).first()
    
    return new_card

def update_card_after_review(db: Session, card_id: str, correct: bool) -> Flashcard:
    """Update card after review."""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise ValueError("Card not found")
    
    if correct:
        # Move to next bin (max 11)
        if card.bin_number < 11:
            card.bin_number += 1
    else:
        # Increment incorrect count
        card.incorrect_count += 1
        
        # Check if card should be marked as hard to remember
        if card.incorrect_count >= 10:
            card.is_hard_to_remember = True
            db.commit()
            db.refresh(card)
            return card
        
        # Move back to bin 1 (unless already in bin 0)
        if card.bin_number > 0:
            card.bin_number = 1
    
    # Calculate next review time
    if card.bin_number == 0:
        card.next_review = datetime.utcnow()
    elif card.bin_number == 11:
        # Never review again
        card.next_review = datetime.utcnow() + timedelta(days=365 * 100)  # Far future
    else:
        timespan = BIN_TIMESPANS[card.bin_number]
        card.next_review = datetime.utcnow() + timedelta(seconds=timespan)
    
    db.commit()
    db.refresh(card)
    return card

def get_study_status(db: Session) -> dict:
    """Get current study status."""
    # Count cards ready for review
    now = datetime.utcnow()
    ready_cards_count = db.query(Flashcard).filter(
        Flashcard.bin_number >= 1,
        Flashcard.next_review <= now,
        Flashcard.is_hard_to_remember == False
    ).count()
    
    # Count new cards (bin 0)
    new_cards_count = db.query(Flashcard).filter(
        Flashcard.bin_number == 0,
        Flashcard.is_hard_to_remember == False
    ).count()
    
    # Count total active cards
    total_active = db.query(Flashcard).filter(
        Flashcard.is_hard_to_remember == False,
        Flashcard.bin_number < 11
    ).count()
    
    # Count completed cards (bin 11)
    completed_cards = db.query(Flashcard).filter(
        Flashcard.bin_number == 11,
        Flashcard.is_hard_to_remember == False
    ).count()
    
    # Count hard to remember cards
    hard_cards = db.query(Flashcard).filter(
        Flashcard.is_hard_to_remember == True
    ).count()
    
    if ready_cards_count > 0 or new_cards_count > 0:
        return {
            "message": f"Ready to review: {ready_cards_count} cards, New cards: {new_cards_count}",
            "has_cards": True
        }
    elif total_active > 0:
        return {
            "message": "You are temporarily done; please come back later to review more words.",
            "has_cards": False
        }
    else:
        return {
            "message": "You have no more words to review; you are permanently done!",
            "has_cards": False
        }

def update_flashcard(db: Session, card_id: str, word: str, definition: str) -> Flashcard:
    """Update an existing flashcard."""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise ValueError("Flashcard not found")
    
    # Check if the new word already exists (and it's not the same card)
    existing_card = db.query(Flashcard).filter(
        Flashcard.word == word,
        Flashcard.id != card_id
    ).first()
    if existing_card:
        raise ValueError(f"A flashcard with the word '{word}' already exists")
    
    # Update the card
    card.word = word
    card.definition = definition
    
    db.commit()
    db.refresh(card)
    return card

def delete_flashcard(db: Session, card_id: str) -> bool:
    """Delete a flashcard."""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise ValueError("Flashcard not found")
    
    db.delete(card)
    db.commit()
    return True
