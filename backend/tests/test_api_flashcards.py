"""
Integration tests for flashcard API endpoints.
"""
import pytest
import json
from app.models.flashcard import Flashcard

pytestmark = [pytest.mark.integration, pytest.mark.api]


def test_create_flashcard_success(client, test_user):
    """Test successful flashcard creation via API."""
    flashcard_data = {
        "word": "api_test",
        "definition": "A test via API",
        "user_id": test_user.id
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["word"] == "api_test"
    assert data["definition"] == "A test via API"
    assert data["user_id"] == test_user.id
    assert data["bin_number"] == 0
    assert data["incorrect_count"] == 0


def test_create_flashcard_duplicate_word(client, test_user, test_flashcard):
    """Test creating flashcard with duplicate word via API."""
    flashcard_data = {
        "word": test_flashcard.word,
        "definition": "Different definition",
        "user_id": test_user.id
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"]


def test_create_flashcard_invalid_data(client, test_user):
    """Test creating flashcard with invalid data."""
    flashcard_data = {
        "word": "",  # Empty word
        "definition": "Valid definition",
        "user_id": test_user.id
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_data)
    
    assert response.status_code == 422  # Validation error


def test_get_flashcards_list(client, test_user, multiple_flashcards):
    """Test getting flashcards list via API."""
    response = client.get(f"/api/v1/flashcards/?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert len(data["flashcards"]) == len(multiple_flashcards)
    assert data["total"] == len(multiple_flashcards)


def test_get_flashcards_pagination(client, test_user, multiple_flashcards):
    """Test flashcards pagination via API."""
    response = client.get(f"/api/v1/flashcards/?user_id={test_user.id}&page=1&per_page=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["flashcards"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] == len(multiple_flashcards)


def test_get_flashcards_exclude_hard(client, test_user, db_session):
    """Test excluding hard cards via API."""
    # Create a mix of regular and hard cards
    regular_card = Flashcard(
        word="regular_api",
        definition="Regular card",
        user_id=test_user.id,
        is_hard_to_remember=False
    )
    hard_card = Flashcard(
        word="hard_api",
        definition="Hard card",
        user_id=test_user.id,
        is_hard_to_remember=True
    )
    db_session.add_all([regular_card, hard_card])
    db_session.commit()
    
    # Test including hard cards
    response = client.get(f"/api/v1/flashcards/?user_id={test_user.id}&include_hard=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    
    # Test excluding hard cards
    response = client.get(f"/api/v1/flashcards/?user_id={test_user.id}&include_hard=false")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["flashcards"][0]["word"] == "regular_api"


def test_get_flashcard_by_id(client, test_flashcard):
    """Test getting single flashcard by ID via API."""
    response = client.get(f"/api/v1/flashcards/{test_flashcard.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_flashcard.id
    assert data["word"] == test_flashcard.word
    assert data["definition"] == test_flashcard.definition


def test_get_flashcard_not_found(client):
    """Test getting non-existent flashcard via API."""
    response = client.get("/api/v1/flashcards/non-existent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Flashcard not found"


def test_update_flashcard(client, test_flashcard):
    """Test updating flashcard via API."""
    update_data = {
        "word": "updated_word",
        "definition": "Updated definition"
    }
    
    response = client.put(f"/api/v1/flashcards/{test_flashcard.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["word"] == "updated_word"
    assert data["definition"] == "Updated definition"


def test_update_flashcard_partial(client, test_flashcard):
    """Test partial update of flashcard via API."""
    original_word = test_flashcard.word
    update_data = {
        "definition": "Only definition updated"
    }
    
    response = client.put(f"/api/v1/flashcards/{test_flashcard.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["word"] == original_word  # Unchanged
    assert data["definition"] == "Only definition updated"


def test_update_flashcard_not_found(client):
    """Test updating non-existent flashcard via API."""
    update_data = {"word": "nonexistent"}
    
    response = client.put("/api/v1/flashcards/non-existent-id", json=update_data)
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Flashcard not found"


def test_update_flashcard_duplicate_word(client, test_user, db_session):
    """Test updating flashcard to duplicate word via API."""
    # Create two flashcards
    card1 = Flashcard(
        word="first_api",
        definition="First card",
        user_id=test_user.id
    )
    card2 = Flashcard(
        word="second_api",
        definition="Second card",
        user_id=test_user.id
    )
    db_session.add_all([card1, card2])
    db_session.commit()
    
    # Try to update second card to have same word as first
    update_data = {"word": "first_api"}
    
    response = client.put(f"/api/v1/flashcards/{card2.id}", json=update_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"]


def test_delete_flashcard(client, test_flashcard):
    """Test deleting flashcard via API."""
    response = client.delete(f"/api/v1/flashcards/{test_flashcard.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Flashcard deleted successfully"
    
    # Verify flashcard is deleted
    get_response = client.get(f"/api/v1/flashcards/{test_flashcard.id}")
    assert get_response.status_code == 404


def test_delete_flashcard_not_found(client):
    """Test deleting non-existent flashcard via API."""
    response = client.delete("/api/v1/flashcards/non-existent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Flashcard not found"


def test_get_flashcard_stats(client, test_user, multiple_flashcards):
    """Test getting flashcard statistics via API."""
    response = client.get(f"/api/v1/flashcards/stats?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "current_count" in data
    assert "limit" in data
    assert "remaining" in data
    assert "at_limit" in data
    assert data["current_count"] == len(multiple_flashcards)
    assert data["at_limit"] is False


def test_missing_user_id_parameter(client):
    """Test API endpoints that require user_id parameter."""
    # Test flashcards list without user_id
    response = client.get("/api/v1/flashcards/")
    assert response.status_code == 422  # Validation error
    
    # Test stats without user_id
    response = client.get("/api/v1/flashcards/stats")
    assert response.status_code == 422  # Validation error


def test_invalid_pagination_parameters(client, test_user):
    """Test invalid pagination parameters."""
    # Test negative page number
    response = client.get(f"/api/v1/flashcards/?user_id={test_user.id}&page=0")
    assert response.status_code == 422
    
    # Test excessive per_page
    response = client.get(f"/api/v1/flashcards/?user_id={test_user.id}&per_page=1000")
    assert response.status_code == 422
