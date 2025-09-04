"""
Integration tests for study API endpoints.
"""
import pytest
from datetime import datetime, timedelta
from app.models.flashcard import Flashcard

pytestmark = [pytest.mark.integration, pytest.mark.api]


def test_get_next_card_success(client, test_user, db_session):
    """Test getting next card for review via API."""
    # Create a new card
    card = Flashcard(
        word="next_card_test",
        definition="Test for next card",
        user_id=test_user.id,
        bin_number=0
    )
    db_session.add(card)
    db_session.commit()
    
    response = client.get(f"/api/v1/study/next?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["word"] == "next_card_test"
    assert data["definition"] == "Test for next card"
    assert data["user_id"] == test_user.id


def test_get_next_card_no_cards_available(client, test_user):
    """Test getting next card when no cards are available."""
    response = client.get(f"/api/v1/study/next?user_id={test_user.id}")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No cards available for review"


def test_get_next_card_priority_order(client, test_user, db_session):
    """Test that next card returns higher priority cards first."""
    now = datetime.utcnow()
    past_time = now - timedelta(minutes=10)
    
    # Create cards with different priorities
    new_card = Flashcard(
        word="new_card",
        definition="New card",
        user_id=test_user.id,
        bin_number=0
    )
    ready_low_bin = Flashcard(
        word="ready_low",
        definition="Ready low bin",
        user_id=test_user.id,
        bin_number=2,
        next_review=past_time
    )
    ready_high_bin = Flashcard(
        word="ready_high",
        definition="Ready high bin",
        user_id=test_user.id,
        bin_number=5,
        next_review=past_time
    )
    
    db_session.add_all([new_card, ready_low_bin, ready_high_bin])
    db_session.commit()
    
    response = client.get(f"/api/v1/study/next?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    # Should return the highest bin ready card
    assert data["word"] == "ready_high"
    assert data["bin_number"] == 5


def test_get_next_card_missing_user_id(client):
    """Test getting next card without user_id parameter."""
    response = client.get("/api/v1/study/next")
    
    assert response.status_code == 422  # Validation error


def test_review_card_correct(client, test_user, db_session):
    """Test reviewing a card with correct answer via API."""
    card = Flashcard(
        word="review_correct",
        definition="Review correct test",
        user_id=test_user.id,
        bin_number=1
    )
    db_session.add(card)
    db_session.commit()
    
    review_data = {"correct": True}
    
    response = client.post(f"/api/v1/study/{card.id}/review", json=review_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["bin_number"] == 2  # Promoted
    assert data["incorrect_count"] == 0


def test_review_card_incorrect(client, test_user, db_session):
    """Test reviewing a card with incorrect answer via API."""
    card = Flashcard(
        word="review_incorrect",
        definition="Review incorrect test",
        user_id=test_user.id,
        bin_number=3,
        incorrect_count=1
    )
    db_session.add(card)
    db_session.commit()
    
    review_data = {"correct": False}
    
    response = client.post(f"/api/v1/study/{card.id}/review", json=review_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["bin_number"] == 1  # Demoted
    assert data["incorrect_count"] == 2


def test_review_card_not_found(client):
    """Test reviewing non-existent card via API."""
    review_data = {"correct": True}
    
    response = client.post("/api/v1/study/non-existent-id/review", json=review_data)
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Card not found"


def test_review_card_invalid_data(client, test_flashcard):
    """Test reviewing card with invalid data."""
    # Missing 'correct' field
    review_data = {}
    
    response = client.post(f"/api/v1/study/{test_flashcard.id}/review", json=review_data)
    
    assert response.status_code == 422  # Validation error


def test_get_study_status_with_cards(client, test_user, db_session):
    """Test getting study status when cards are available."""
    now = datetime.utcnow()
    past_time = now - timedelta(minutes=10)
    
    # Create various types of cards
    ready_card = Flashcard(
        word="ready_status",
        definition="Ready card",
        user_id=test_user.id,
        bin_number=2,
        next_review=past_time
    )
    new_card = Flashcard(
        word="new_status",
        definition="New card",
        user_id=test_user.id,
        bin_number=0
    )
    future_card = Flashcard(
        word="future_status",
        definition="Future card",
        user_id=test_user.id,
        bin_number=3,
        next_review=now + timedelta(hours=1)
    )
    completed_card = Flashcard(
        word="completed_status",
        definition="Completed card",
        user_id=test_user.id,
        bin_number=11
    )
    hard_card = Flashcard(
        word="hard_status",
        definition="Hard card",
        user_id=test_user.id,
        bin_number=1,
        is_hard_to_remember=True
    )
    
    db_session.add_all([ready_card, new_card, future_card, completed_card, hard_card])
    db_session.commit()
    
    response = client.get(f"/api/v1/study/status?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_cards"] is True
    assert data["ready_cards_count"] == 1
    assert data["new_cards_count"] == 1
    assert data["total_active_cards"] == 3
    assert data["completed_cards"] == 1
    assert data["hard_cards"] == 1
    assert "Ready to review: 1 cards, New cards: 1" in data["message"]


def test_get_study_status_temporarily_done(client, test_user, db_session):
    """Test study status when temporarily done."""
    now = datetime.utcnow()
    future_time = now + timedelta(hours=1)
    
    # Create a card that's not ready yet
    future_card = Flashcard(
        word="future_only",
        definition="Future card",
        user_id=test_user.id,
        bin_number=3,
        next_review=future_time
    )
    db_session.add(future_card)
    db_session.commit()
    
    response = client.get(f"/api/v1/study/status?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_cards"] is False
    assert data["ready_cards_count"] == 0
    assert data["new_cards_count"] == 0
    assert data["total_active_cards"] == 1
    assert "temporarily done" in data["message"]


def test_get_study_status_permanently_done(client, test_user, db_session):
    """Test study status when permanently done."""
    # Create only completed and hard cards
    completed_card = Flashcard(
        word="completed_only",
        definition="Completed card",
        user_id=test_user.id,
        bin_number=11
    )
    hard_card = Flashcard(
        word="hard_only",
        definition="Hard card",
        user_id=test_user.id,
        bin_number=1,
        is_hard_to_remember=True
    )
    db_session.add_all([completed_card, hard_card])
    db_session.commit()
    
    response = client.get(f"/api/v1/study/status?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_cards"] is False
    assert data["ready_cards_count"] == 0
    assert data["new_cards_count"] == 0
    assert data["total_active_cards"] == 0
    assert data["completed_cards"] == 1
    assert data["hard_cards"] == 1
    assert "permanently done" in data["message"]


def test_get_study_status_no_cards(client, test_user):
    """Test study status when no cards exist."""
    response = client.get(f"/api/v1/study/status?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_cards"] is False
    assert data["ready_cards_count"] == 0
    assert data["new_cards_count"] == 0
    assert data["total_active_cards"] == 0
    assert data["completed_cards"] == 0
    assert data["hard_cards"] == 0
    assert "permanently done" in data["message"]


def test_get_study_status_missing_user_id(client):
    """Test getting study status without user_id parameter."""
    response = client.get("/api/v1/study/status")
    
    assert response.status_code == 422  # Validation error


def test_study_workflow_integration(client, test_user, db_session):
    """Test complete study workflow: create card, get next, review, check status."""
    # Step 1: Create a flashcard
    flashcard_data = {
        "word": "workflow_test",
        "definition": "Test complete workflow",
        "user_id": test_user.id
    }
    create_response = client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    card_id = create_response.json()["id"]
    
    # Step 2: Check study status (should have new card)
    status_response = client.get(f"/api/v1/study/status?user_id={test_user.id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["has_cards"] is True
    assert status_data["new_cards_count"] == 1
    
    # Step 3: Get next card for review
    next_response = client.get(f"/api/v1/study/next?user_id={test_user.id}")
    assert next_response.status_code == 200
    next_data = next_response.json()
    assert next_data["word"] == "workflow_test"
    
    # Step 4: Review the card (correct answer)
    review_data = {"correct": True}
    review_response = client.post(f"/api/v1/study/{card_id}/review", json=review_data)
    assert review_response.status_code == 200
    review_result = review_response.json()
    assert review_result["bin_number"] == 1  # Promoted from bin 0
    
    # Step 5: Check study status again (should have no ready cards now)
    final_status_response = client.get(f"/api/v1/study/status?user_id={test_user.id}")
    assert final_status_response.status_code == 200
    final_status_data = final_status_response.json()
    assert final_status_data["new_cards_count"] == 0
    assert final_status_data["total_active_cards"] == 1
