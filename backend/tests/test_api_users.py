"""
Integration tests for user API endpoints.
"""
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.api]


def test_create_user_success(client):
    """Test successful user creation via API."""
    user_data = {"name": "API Test User"}
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Test User"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_user_duplicate_name(client, test_user):
    """Test creating user with duplicate name via API."""
    user_data = {"name": test_user.name}
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"]


def test_create_user_invalid_data(client):
    """Test creating user with invalid data."""
    user_data = {"name": ""}  # Empty name
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 422  # Validation error


def test_create_user_missing_name(client):
    """Test creating user without name field."""
    user_data = {}  # Missing name
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 422  # Validation error


def test_get_users_list(client, test_user, second_user):
    """Test getting users list via API."""
    response = client.get("/api/v1/users/")
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert len(data["users"]) == 2
    assert data["total"] == 2
    
    user_names = [user["name"] for user in data["users"]]
    assert test_user.name in user_names
    assert second_user.name in user_names


def test_get_users_empty_list(client):
    """Test getting users list when no users exist."""
    response = client.get("/api/v1/users/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["users"] == []
    assert data["total"] == 0


def test_get_user_by_id(client, test_user):
    """Test getting single user by ID via API."""
    response = client.get(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["name"] == test_user.name
    assert "created_at" in data
    assert "updated_at" in data


def test_get_user_by_id_not_found(client):
    """Test getting non-existent user via API."""
    response = client.get("/api/v1/users/non-existent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_user_success(client, test_user):
    """Test successful user update via API."""
    update_data = {"name": "Updated User Name"}
    
    response = client.put(f"/api/v1/users/{test_user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User Name"
    assert data["id"] == test_user.id


def test_update_user_not_found(client):
    """Test updating non-existent user via API."""
    update_data = {"name": "Non-existent User"}
    
    response = client.put("/api/v1/users/non-existent-id", json=update_data)
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_user_duplicate_name(client, test_user, second_user):
    """Test updating user to duplicate name via API."""
    update_data = {"name": second_user.name}
    
    response = client.put(f"/api/v1/users/{test_user.id}", json=update_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"]


def test_update_user_invalid_data(client, test_user):
    """Test updating user with invalid data."""
    update_data = {"name": ""}  # Empty name
    
    response = client.put(f"/api/v1/users/{test_user.id}", json=update_data)
    
    assert response.status_code == 422  # Validation error


def test_delete_user_success(client, test_user):
    """Test successful user deletion via API."""
    response = client.delete(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User deleted successfully"
    
    # Verify user is deleted
    get_response = client.get(f"/api/v1/users/{test_user.id}")
    assert get_response.status_code == 404


def test_delete_user_not_found(client):
    """Test deleting non-existent user via API."""
    response = client.delete("/api/v1/users/non-existent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_delete_user_with_flashcards(client, test_user, test_flashcard):
    """Test deleting user with flashcards via API."""
    user_id = test_user.id
    flashcard_id = test_flashcard.id
    
    # Verify flashcard exists
    flashcard_response = client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert flashcard_response.status_code == 200
    
    # Delete user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    # Verify user is deleted
    user_response = client.get(f"/api/v1/users/{user_id}")
    assert user_response.status_code == 404
    
    # Verify flashcard is also deleted (cascade)
    flashcard_response = client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert flashcard_response.status_code == 404


def test_user_workflow_integration(client):
    """Test complete user workflow: create, get, update, delete."""
    # Step 1: Create a user
    create_data = {"name": "Workflow Test User"}
    create_response = client.post("/api/v1/users/", json=create_data)
    assert create_response.status_code == 201
    user_data = create_response.json()
    user_id = user_data["id"]
    
    # Step 2: Get the user
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["name"] == "Workflow Test User"
    
    # Step 3: Update the user
    update_data = {"name": "Updated Workflow User"}
    update_response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert update_response.status_code == 200
    update_result = update_response.json()
    assert update_result["name"] == "Updated Workflow User"
    
    # Step 4: Verify the update
    verify_response = client.get(f"/api/v1/users/{user_id}")
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["name"] == "Updated Workflow User"
    
    # Step 5: Delete the user
    delete_response = client.delete(f"/api/v1/users/{user_id}")
    assert delete_response.status_code == 200
    
    # Step 6: Verify deletion
    final_get_response = client.get(f"/api/v1/users/{user_id}")
    assert final_get_response.status_code == 404


def test_user_max_limit_enforcement(client):
    """Test that user creation respects the maximum limit via API."""
    # Create 5 users
    user_ids = []
    for i in range(5):
        user_data = {"name": f"Limit Test User {i}"}
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        user_ids.append(response.json()["id"])
    
    # Try to create the 6th user (should fail)
    user_data = {"name": "Sixth User"}
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    data = response.json()
    assert "Maximum number of users" in data["detail"]
    
    # Clean up
    for user_id in user_ids:
        client.delete(f"/api/v1/users/{user_id}")


def test_users_list_ordering(client):
    """Test that users list is ordered by creation time."""
    # Create users in specific order
    users_data = [
        {"name": "First User"},
        {"name": "Second User"},
        {"name": "Third User"}
    ]
    
    created_users = []
    for user_data in users_data:
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        created_users.append(response.json())
    
    # Get users list
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    
    # Should be ordered by creation time
    assert len(data["users"]) == 3
    assert data["users"][0]["name"] == "First User"
    assert data["users"][1]["name"] == "Second User"
    assert data["users"][2]["name"] == "Third User"
    
    # Clean up
    for user in created_users:
        client.delete(f"/api/v1/users/{user['id']}")
