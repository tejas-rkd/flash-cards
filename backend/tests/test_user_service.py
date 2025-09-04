"""
Unit tests for user service.
"""
import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

pytestmark = pytest.mark.unit


def test_create_user_success(db_session):
    """Test successful user creation."""
    user_data = UserCreate(name="Test User")
    
    user = UserService.create_user(db_session, user_data)
    
    assert user.name == "Test User"
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_create_user_duplicate_name(db_session, test_user):
    """Test creating user with duplicate name fails."""
    user_data = UserCreate(name=test_user.name)
    
    with pytest.raises(ValueError) as exc_info:
        UserService.create_user(db_session, user_data)
    
    assert "already exists" in str(exc_info.value)


def test_create_user_max_limit(db_session, monkeypatch):
    """Test that user creation respects the maximum limit."""
    # Create 5 users first
    for i in range(5):
        user_data = UserCreate(name=f"User {i}")
        UserService.create_user(db_session, user_data)
    
    # Try to create the 6th user
    user_data = UserCreate(name="Sixth User")
    with pytest.raises(ValueError) as exc_info:
        UserService.create_user(db_session, user_data)
    
    assert "Maximum number of users" in str(exc_info.value)


def test_get_all_users(db_session):
    """Test getting all users."""
    # Create multiple users
    users_data = [
        UserCreate(name="User 1"),
        UserCreate(name="User 2"), 
        UserCreate(name="User 3")
    ]
    
    created_users = []
    for user_data in users_data:
        user = UserService.create_user(db_session, user_data)
        created_users.append(user)
    
    all_users = UserService.get_all_users(db_session)
    
    assert len(all_users) == 3
    user_names = [user.name for user in all_users]
    assert "User 1" in user_names
    assert "User 2" in user_names
    assert "User 3" in user_names


def test_get_user_by_id(db_session, test_user):
    """Test getting user by ID."""
    found_user = UserService.get_user_by_id(db_session, test_user.id)
    
    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.name == test_user.name


def test_get_user_by_id_not_found(db_session):
    """Test getting user by non-existent ID."""
    found_user = UserService.get_user_by_id(db_session, "non-existent-id")
    assert found_user is None


def test_get_user_by_name(db_session, test_user):
    """Test getting user by name."""
    found_user = UserService.get_user_by_name(db_session, test_user.name)
    
    assert found_user is not None
    assert found_user.name == test_user.name
    assert found_user.id == test_user.id


def test_get_user_by_name_not_found(db_session):
    """Test getting user by non-existent name."""
    found_user = UserService.get_user_by_name(db_session, "Non-existent User")
    assert found_user is None


def test_update_user_success(db_session, test_user):
    """Test successful user update."""
    update_data = UserUpdate(name="Updated Name")
    
    updated_user = UserService.update_user(db_session, test_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.name == "Updated Name"
    assert updated_user.id == test_user.id


def test_update_user_not_found(db_session):
    """Test updating non-existent user."""
    update_data = UserUpdate(name="Non-existent")
    
    result = UserService.update_user(db_session, "non-existent-id", update_data)
    
    assert result is None


def test_update_user_duplicate_name(db_session):
    """Test updating user to duplicate name fails."""
    # Create two users
    user1 = UserService.create_user(db_session, UserCreate(name="User 1"))
    user2 = UserService.create_user(db_session, UserCreate(name="User 2"))
    
    # Try to update user2 to have same name as user1
    update_data = UserUpdate(name="User 1")
    
    with pytest.raises(ValueError) as exc_info:
        UserService.update_user(db_session, user2.id, update_data)
    
    assert "already exists" in str(exc_info.value)


def test_update_user_same_name(db_session, test_user):
    """Test updating user to the same name (should succeed)."""
    update_data = UserUpdate(name=test_user.name)
    
    updated_user = UserService.update_user(db_session, test_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.name == test_user.name


def test_delete_user_success(db_session, test_user):
    """Test successful user deletion."""
    user_id = test_user.id
    
    result = UserService.delete_user(db_session, user_id)
    
    assert result is True
    
    # Verify user is deleted
    deleted_user = UserService.get_user_by_id(db_session, user_id)
    assert deleted_user is None


def test_delete_user_not_found(db_session):
    """Test deleting non-existent user."""
    result = UserService.delete_user(db_session, "non-existent-id")
    assert result is False


def test_delete_user_with_flashcards(db_session, test_user, test_flashcard):
    """Test that deleting user also deletes their flashcards."""
    user_id = test_user.id
    flashcard_id = test_flashcard.id
    
    # Verify flashcard exists
    from app.services.flashcard_service import FlashcardService
    existing_flashcard = FlashcardService.get_flashcard_by_id(db_session, flashcard_id)
    assert existing_flashcard is not None
    
    # Delete user
    result = UserService.delete_user(db_session, user_id)
    assert result is True
    
    # Verify user is deleted
    deleted_user = UserService.get_user_by_id(db_session, user_id)
    assert deleted_user is None
    
    # Verify flashcard is also deleted (cascade)
    deleted_flashcard = FlashcardService.get_flashcard_by_id(db_session, flashcard_id)
    assert deleted_flashcard is None


def test_count_users(db_session):
    """Test counting users."""
    # Initially should be 0
    count = UserService.count_users(db_session)
    assert count == 0
    
    # Create users
    for i in range(3):
        UserService.create_user(db_session, UserCreate(name=f"User {i}"))
    
    # Count should be 3
    count = UserService.count_users(db_session)
    assert count == 3


def test_count_users_with_existing(db_session, test_user):
    """Test counting users when some already exist."""
    # Should be 1 (test_user)
    count = UserService.count_users(db_session)
    assert count == 1
    
    # Create one more
    UserService.create_user(db_session, UserCreate(name="Another User"))
    
    # Should be 2
    count = UserService.count_users(db_session)
    assert count == 2
