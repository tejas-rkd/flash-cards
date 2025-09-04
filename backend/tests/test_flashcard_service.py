"""
Unit tests for flashcard service.
"""
import pytest
from datetime import datetime, timedelta
from app.services.flashcard_service import FlashcardService
from app.schemas.flashcard import FlashcardCreate, FlashcardUpdate
from app.models.flashcard import Flashcard
from app.core.config import settings

pytestmark = pytest.mark.unit


def test_create_flashcard_success(db_session, test_user):
    """Test successful flashcard creation."""
    flashcard_data = FlashcardCreate(
        word="success",
        definition="Achievement of a goal",
        user_id=test_user.id
    )
    
    flashcard = FlashcardService.create_flashcard(db_session, flashcard_data)
    
    assert flashcard.word == "success"
    assert flashcard.definition == "Achievement of a goal"
    assert flashcard.user_id == test_user.id
    assert flashcard.bin_number == 0
    assert flashcard.incorrect_count == 0
    assert isinstance(flashcard.next_review, datetime)


def test_create_flashcard_duplicate_word(db_session, test_user, test_flashcard):
    """Test creating flashcard with duplicate word fails."""
    flashcard_data = FlashcardCreate(
        word=test_flashcard.word,  # Same word as existing flashcard
        definition="Different definition",
        user_id=test_user.id
    )
    
    with pytest.raises(ValueError) as exc_info:
        FlashcardService.create_flashcard(db_session, flashcard_data)
    
    assert "already exists" in str(exc_info.value)


def test_create_flashcard_different_users_same_word(db_session, test_user, second_user):
    """Test that different users can have flashcards with the same word."""
    word = "common"
    
    # Create flashcard for first user
    flashcard_data1 = FlashcardCreate(
        word=word,
        definition="Definition for user 1",
        user_id=test_user.id
    )
    flashcard1 = FlashcardService.create_flashcard(db_session, flashcard_data1)
    
    # Create flashcard for second user with same word
    flashcard_data2 = FlashcardCreate(
        word=word,
        definition="Definition for user 2",
        user_id=second_user.id
    )
    flashcard2 = FlashcardService.create_flashcard(db_session, flashcard_data2)
    
    assert flashcard1.word == flashcard2.word
    assert flashcard1.user_id != flashcard2.user_id
    assert flashcard1.definition != flashcard2.definition


def test_get_flashcard_by_id(db_session, test_flashcard):
    """Test getting flashcard by ID."""
    found_flashcard = FlashcardService.get_flashcard_by_id(db_session, test_flashcard.id)
    
    assert found_flashcard is not None
    assert found_flashcard.id == test_flashcard.id
    assert found_flashcard.word == test_flashcard.word


def test_get_flashcard_by_id_not_found(db_session):
    """Test getting flashcard by non-existent ID."""
    found_flashcard = FlashcardService.get_flashcard_by_id(db_session, "non-existent-id")
    assert found_flashcard is None


def test_get_flashcard_by_word(db_session, test_flashcard, test_user):
    """Test getting flashcard by word and user."""
    found_flashcard = FlashcardService.get_flashcard_by_word(
        db_session, test_flashcard.word, test_user.id
    )
    
    assert found_flashcard is not None
    assert found_flashcard.word == test_flashcard.word
    assert found_flashcard.user_id == test_user.id


def test_get_all_flashcards(db_session, multiple_flashcards, test_user):
    """Test getting all flashcards for a user."""
    flashcards = FlashcardService.get_all_flashcards(db_session, test_user.id)
    
    assert len(flashcards) == len(multiple_flashcards)
    user_ids = [card.user_id for card in flashcards]
    assert all(uid == test_user.id for uid in user_ids)


def test_get_all_flashcards_pagination(db_session, multiple_flashcards, test_user):
    """Test pagination in get_all_flashcards."""
    # Test first page
    flashcards_page1 = FlashcardService.get_all_flashcards(
        db_session, test_user.id, skip=0, limit=2
    )
    assert len(flashcards_page1) == 2
    
    # Test second page
    flashcards_page2 = FlashcardService.get_all_flashcards(
        db_session, test_user.id, skip=2, limit=2
    )
    assert len(flashcards_page2) == 2
    
    # Ensure different flashcards on different pages
    page1_ids = {card.id for card in flashcards_page1}
    page2_ids = {card.id for card in flashcards_page2}
    assert page1_ids.isdisjoint(page2_ids)


def test_get_all_flashcards_exclude_hard(db_session, test_user):
    """Test excluding hard to remember cards."""
    # Create a mix of regular and hard cards
    regular_card = Flashcard(
        word="regular",
        definition="Regular card",
        user_id=test_user.id,
        is_hard_to_remember=False
    )
    hard_card = Flashcard(
        word="hard",
        definition="Hard card",
        user_id=test_user.id,
        is_hard_to_remember=True
    )
    
    db_session.add_all([regular_card, hard_card])
    db_session.commit()
    
    # Get all cards
    all_cards = FlashcardService.get_all_flashcards(
        db_session, test_user.id, include_hard=True
    )
    assert len(all_cards) == 2
    
    # Get only non-hard cards
    easy_cards = FlashcardService.get_all_flashcards(
        db_session, test_user.id, include_hard=False
    )
    assert len(easy_cards) == 1
    assert easy_cards[0].word == "regular"


def test_count_flashcards(db_session, multiple_flashcards, test_user):
    """Test counting flashcards."""
    count = FlashcardService.count_flashcards(db_session, test_user.id)
    assert count == len(multiple_flashcards)


def test_update_flashcard_success(db_session, test_flashcard):
    """Test successful flashcard update."""
    update_data = FlashcardUpdate(
        word="updated_word",
        definition="Updated definition"
    )
    
    updated_flashcard = FlashcardService.update_flashcard(
        db_session, test_flashcard.id, update_data
    )
    
    assert updated_flashcard is not None
    assert updated_flashcard.word == "updated_word"
    assert updated_flashcard.definition == "Updated definition"
    assert updated_flashcard.updated_at > test_flashcard.updated_at


def test_update_flashcard_partial(db_session, test_flashcard):
    """Test partial flashcard update."""
    original_word = test_flashcard.word
    update_data = FlashcardUpdate(definition="Only definition updated")
    
    updated_flashcard = FlashcardService.update_flashcard(
        db_session, test_flashcard.id, update_data
    )
    
    assert updated_flashcard is not None
    assert updated_flashcard.word == original_word  # Unchanged
    assert updated_flashcard.definition == "Only definition updated"


def test_update_flashcard_not_found(db_session):
    """Test updating non-existent flashcard."""
    update_data = FlashcardUpdate(word="nonexistent")
    
    result = FlashcardService.update_flashcard(
        db_session, "non-existent-id", update_data
    )
    
    assert result is None


def test_update_flashcard_duplicate_word(db_session, test_user):
    """Test updating flashcard to duplicate word fails."""
    # Create two flashcards
    card1 = Flashcard(
        word="first",
        definition="First card",
        user_id=test_user.id
    )
    card2 = Flashcard(
        word="second",
        definition="Second card",
        user_id=test_user.id
    )
    db_session.add_all([card1, card2])
    db_session.commit()
    
    # Try to update second card to have same word as first
    update_data = FlashcardUpdate(word="first")
    
    with pytest.raises(ValueError) as exc_info:
        FlashcardService.update_flashcard(db_session, card2.id, update_data)
    
    assert "already exists" in str(exc_info.value)


def test_delete_flashcard_success(db_session, test_flashcard):
    """Test successful flashcard deletion."""
    flashcard_id = test_flashcard.id
    
    result = FlashcardService.delete_flashcard(db_session, flashcard_id)
    
    assert result is True
    
    # Verify flashcard is deleted
    deleted_flashcard = FlashcardService.get_flashcard_by_id(db_session, flashcard_id)
    assert deleted_flashcard is None


def test_delete_flashcard_not_found(db_session):
    """Test deleting non-existent flashcard."""
    result = FlashcardService.delete_flashcard(db_session, "non-existent-id")
    assert result is False


def test_get_user_flashcard_stats(db_session, test_user, multiple_flashcards):
    """Test getting user flashcard statistics."""
    stats = FlashcardService.get_user_flashcard_stats(db_session, test_user.id)
    
    assert "current_count" in stats
    assert "limit" in stats
    assert "remaining" in stats
    assert "at_limit" in stats
    
    assert stats["current_count"] == len(multiple_flashcards)
    assert stats["limit"] == settings.MAX_FLASHCARDS_PER_USER
    assert stats["remaining"] == settings.MAX_FLASHCARDS_PER_USER - len(multiple_flashcards)
    assert stats["at_limit"] is False


def test_flashcard_limit_enforcement(db_session, test_user, monkeypatch):
    """Test that flashcard creation respects user limits."""
    # Temporarily set a low limit for testing
    monkeypatch.setattr(settings, "MAX_FLASHCARDS_PER_USER", 2)
    
    # Create flashcards up to the limit
    for i in range(2):
        flashcard_data = FlashcardCreate(
            word=f"word_{i}",
            definition=f"Definition {i}",
            user_id=test_user.id
        )
        FlashcardService.create_flashcard(db_session, flashcard_data)
    
    # Try to create one more (should fail)
    flashcard_data = FlashcardCreate(
        word="overflow",
        definition="This should fail",
        user_id=test_user.id
    )
    
    with pytest.raises(ValueError) as exc_info:
        FlashcardService.create_flashcard(db_session, flashcard_data)
    
    assert "maximum limit" in str(exc_info.value)
