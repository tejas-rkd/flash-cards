"""
Unit tests for study service.
"""
import pytest
from datetime import datetime, timedelta
from app.services.study_service import StudyService
from app.models.flashcard import Flashcard
from app.schemas.study import StudyStatusResponse

pytestmark = pytest.mark.unit


def test_get_next_card_for_review_new_card(db_session, test_user):
    """Test getting next card when only new cards are available."""
    # Create a new card (bin 0)
    new_card = Flashcard(
        word="new_word",
        definition="A new word to learn",
        user_id=test_user.id,
        bin_number=0
    )
    db_session.add(new_card)
    db_session.commit()
    
    next_card = StudyService.get_next_card_for_review(db_session, test_user.id)
    
    assert next_card is not None
    assert next_card.id == new_card.id
    assert next_card.bin_number == 0


def test_get_next_card_for_review_ready_card(db_session, test_user):
    """Test getting next card when review cards are ready."""
    now = datetime.utcnow()
    past_time = now - timedelta(minutes=10)
    
    # Create cards in different bins with different review times
    ready_card = Flashcard(
        word="ready_word",
        definition="Ready for review",
        user_id=test_user.id,
        bin_number=3,
        next_review=past_time  # Ready for review
    )
    future_card = Flashcard(
        word="future_word",
        definition="Not ready yet",
        user_id=test_user.id,
        bin_number=2,
        next_review=now + timedelta(hours=1)  # Not ready
    )
    new_card = Flashcard(
        word="new_word",
        definition="New word",
        user_id=test_user.id,
        bin_number=0
    )
    
    db_session.add_all([ready_card, future_card, new_card])
    db_session.commit()
    
    next_card = StudyService.get_next_card_for_review(db_session, test_user.id)
    
    # Should return the ready card (higher priority than new card)
    assert next_card is not None
    assert next_card.id == ready_card.id
    assert next_card.bin_number == 3


def test_get_next_card_for_review_priority_order(db_session, test_user):
    """Test that higher bin numbers have priority for ready cards."""
    now = datetime.utcnow()
    past_time = now - timedelta(minutes=10)
    
    # Create ready cards in different bins
    bin2_card = Flashcard(
        word="bin2_word",
        definition="Bin 2 card",
        user_id=test_user.id,
        bin_number=2,
        next_review=past_time
    )
    bin5_card = Flashcard(
        word="bin5_word",
        definition="Bin 5 card",
        user_id=test_user.id,
        bin_number=5,
        next_review=past_time
    )
    
    db_session.add_all([bin2_card, bin5_card])
    db_session.commit()
    
    next_card = StudyService.get_next_card_for_review(db_session, test_user.id)
    
    # Should return the higher bin card first
    assert next_card is not None
    assert next_card.id == bin5_card.id
    assert next_card.bin_number == 5


def test_get_next_card_for_review_skip_hard_cards(db_session, test_user):
    """Test that hard to remember cards are skipped."""
    hard_card = Flashcard(
        word="hard_word",
        definition="Hard to remember",
        user_id=test_user.id,
        bin_number=0,
        is_hard_to_remember=True
    )
    normal_card = Flashcard(
        word="normal_word",
        definition="Normal card",
        user_id=test_user.id,
        bin_number=0,
        is_hard_to_remember=False
    )
    
    db_session.add_all([hard_card, normal_card])
    db_session.commit()
    
    next_card = StudyService.get_next_card_for_review(db_session, test_user.id)
    
    assert next_card is not None
    assert next_card.id == normal_card.id
    assert next_card.is_hard_to_remember is False


def test_get_next_card_for_review_skip_completed_cards(db_session, test_user):
    """Test that completed cards (bin 11) are skipped."""
    completed_card = Flashcard(
        word="completed_word",
        definition="Completed card",
        user_id=test_user.id,
        bin_number=11,
        next_review=datetime.utcnow() - timedelta(days=1)
    )
    active_card = Flashcard(
        word="active_word",
        definition="Active card",
        user_id=test_user.id,
        bin_number=0
    )
    
    db_session.add_all([completed_card, active_card])
    db_session.commit()
    
    next_card = StudyService.get_next_card_for_review(db_session, test_user.id)
    
    assert next_card is not None
    assert next_card.id == active_card.id
    assert next_card.bin_number == 0


def test_get_next_card_for_review_no_cards(db_session, test_user):
    """Test when no cards are available for review."""
    next_card = StudyService.get_next_card_for_review(db_session, test_user.id)
    assert next_card is None


def test_update_card_after_review_correct_answer(db_session, test_user):
    """Test updating card after correct answer."""
    card = Flashcard(
        word="test_word",
        definition="Test definition",
        user_id=test_user.id,
        bin_number=2
    )
    db_session.add(card)
    db_session.commit()
    
    original_bin = card.bin_number
    updated_card = StudyService.update_card_after_review(db_session, card.id, correct=True)
    
    assert updated_card is not None
    assert updated_card.bin_number == original_bin + 1
    assert updated_card.next_review > datetime.utcnow()


def test_update_card_after_review_incorrect_answer(db_session, test_user):
    """Test updating card after incorrect answer."""
    card = Flashcard(
        word="test_word",
        definition="Test definition",
        user_id=test_user.id,
        bin_number=5,
        incorrect_count=2
    )
    db_session.add(card)
    db_session.commit()
    
    updated_card = StudyService.update_card_after_review(db_session, card.id, correct=False)
    
    assert updated_card is not None
    assert updated_card.bin_number == 1  # Demoted to bin 1
    assert updated_card.incorrect_count == 3


def test_update_card_after_review_incorrect_from_bin_zero(db_session, test_user):
    """Test updating card from bin 0 after incorrect answer."""
    card = Flashcard(
        word="test_word",
        definition="Test definition",
        user_id=test_user.id,
        bin_number=0,
        incorrect_count=0
    )
    db_session.add(card)
    db_session.commit()
    
    updated_card = StudyService.update_card_after_review(db_session, card.id, correct=False)
    
    assert updated_card is not None
    assert updated_card.bin_number == 0  # Stays in bin 0
    assert updated_card.incorrect_count == 1


def test_update_card_after_review_mark_hard(db_session, test_user, monkeypatch):
    """Test marking card as hard to remember after too many errors."""
    # Set a low threshold for testing
    monkeypatch.setattr("app.core.config.settings.MAX_INCORRECT_COUNT", 3)
    
    card = Flashcard(
        word="difficult_word",
        definition="Very difficult",
        user_id=test_user.id,
        bin_number=3,
        incorrect_count=2  # One away from threshold
    )
    db_session.add(card)
    db_session.commit()
    
    updated_card = StudyService.update_card_after_review(db_session, card.id, correct=False)
    
    assert updated_card is not None
    assert updated_card.incorrect_count == 3
    assert updated_card.is_hard_to_remember is True


def test_update_card_after_review_max_bin(db_session, test_user):
    """Test that card doesn't go beyond bin 11."""
    card = Flashcard(
        word="mastered_word",
        definition="Almost mastered",
        user_id=test_user.id,
        bin_number=10
    )
    db_session.add(card)
    db_session.commit()
    
    updated_card = StudyService.update_card_after_review(db_session, card.id, correct=True)
    
    assert updated_card is not None
    assert updated_card.bin_number == 11  # Max bin


def test_update_card_after_review_already_max_bin(db_session, test_user):
    """Test that card stays at bin 11 when already there."""
    card = Flashcard(
        word="completed_word",
        definition="Already completed",
        user_id=test_user.id,
        bin_number=11
    )
    db_session.add(card)
    db_session.commit()
    
    updated_card = StudyService.update_card_after_review(db_session, card.id, correct=True)
    
    assert updated_card is not None
    assert updated_card.bin_number == 11  # Stays at max


def test_update_card_after_review_not_found(db_session):
    """Test updating non-existent card."""
    result = StudyService.update_card_after_review(db_session, "non-existent-id", correct=True)
    assert result is None


def test_calculate_next_review_time():
    """Test next review time calculation."""
    # Test bin 0 (immediate)
    next_review = StudyService._calculate_next_review_time(0)
    assert next_review <= datetime.utcnow() + timedelta(seconds=1)
    
    # Test bin 1 (5 seconds)
    next_review = StudyService._calculate_next_review_time(1)
    expected_min = datetime.utcnow() + timedelta(seconds=4)
    expected_max = datetime.utcnow() + timedelta(seconds=6)
    assert expected_min <= next_review <= expected_max
    
    # Test bin 11 (completed - far future)
    next_review = StudyService._calculate_next_review_time(11)
    far_future = datetime.utcnow() + timedelta(days=365 * 50)
    assert next_review > far_future


def test_get_study_status_with_ready_cards(db_session, test_user):
    """Test study status when cards are ready for review."""
    now = datetime.utcnow()
    past_time = now - timedelta(minutes=10)
    
    # Create various types of cards
    ready_card = Flashcard(
        word="ready", definition="Ready", user_id=test_user.id,
        bin_number=2, next_review=past_time
    )
    new_card = Flashcard(
        word="new", definition="New", user_id=test_user.id,
        bin_number=0
    )
    future_card = Flashcard(
        word="future", definition="Future", user_id=test_user.id,
        bin_number=3, next_review=now + timedelta(hours=1)
    )
    completed_card = Flashcard(
        word="completed", definition="Completed", user_id=test_user.id,
        bin_number=11
    )
    hard_card = Flashcard(
        word="hard", definition="Hard", user_id=test_user.id,
        bin_number=1, is_hard_to_remember=True
    )
    
    db_session.add_all([ready_card, new_card, future_card, completed_card, hard_card])
    db_session.commit()
    
    status = StudyService.get_study_status(db_session, test_user.id)
    
    assert isinstance(status, StudyStatusResponse)
    assert status.has_cards is True
    assert status.ready_cards_count == 1
    assert status.new_cards_count == 1
    assert status.total_active_cards == 3  # ready + new + future
    assert status.completed_cards == 1
    assert status.hard_cards == 1
    assert "Ready to review: 1 cards, New cards: 1" in status.message


def test_get_study_status_no_ready_cards_but_has_active(db_session, test_user):
    """Test study status when no cards are ready but some exist."""
    now = datetime.utcnow()
    future_time = now + timedelta(hours=1)
    
    future_card = Flashcard(
        word="future", definition="Future", user_id=test_user.id,
        bin_number=3, next_review=future_time
    )
    db_session.add(future_card)
    db_session.commit()
    
    status = StudyService.get_study_status(db_session, test_user.id)
    
    assert status.has_cards is False
    assert status.ready_cards_count == 0
    assert status.new_cards_count == 0
    assert status.total_active_cards == 1
    assert "temporarily done" in status.message


def test_get_study_status_no_cards(db_session, test_user):
    """Test study status when no active cards exist."""
    # Only create completed and hard cards
    completed_card = Flashcard(
        word="completed", definition="Completed", user_id=test_user.id,
        bin_number=11
    )
    hard_card = Flashcard(
        word="hard", definition="Hard", user_id=test_user.id,
        bin_number=1, is_hard_to_remember=True
    )
    db_session.add_all([completed_card, hard_card])
    db_session.commit()
    
    status = StudyService.get_study_status(db_session, test_user.id)
    
    assert status.has_cards is False
    assert status.ready_cards_count == 0
    assert status.new_cards_count == 0
    assert status.total_active_cards == 0
    assert status.completed_cards == 1
    assert status.hard_cards == 1
    assert "permanently done" in status.message


def test_get_study_status_empty_user(db_session, test_user):
    """Test study status for user with no cards at all."""
    status = StudyService.get_study_status(db_session, test_user.id)
    
    assert status.has_cards is False
    assert status.ready_cards_count == 0
    assert status.new_cards_count == 0
    assert status.total_active_cards == 0
    assert status.completed_cards == 0
    assert status.hard_cards == 0
    assert "permanently done" in status.message
