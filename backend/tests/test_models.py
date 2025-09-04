"""
Unit tests for flashcard models.
"""
import pytest
from datetime import datetime
from app.models.flashcard import Flashcard
from app.models.user import User

pytestmark = pytest.mark.unit


def test_user_creation(db_session):
    """Test creating a user."""
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.name == "Test User"
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_str_representation(test_user):
    """Test user string representation."""
    assert str(test_user) == "Test User"


def test_user_repr_representation(test_user):
    """Test user repr representation."""
    repr_str = repr(test_user)
    assert "User" in repr_str
    assert test_user.id in repr_str
    assert "Test User" in repr_str


def test_flashcard_creation(db_session, test_user):
    """Test creating a flashcard."""
    flashcard = Flashcard(
        word="vocabulary",
        definition="A body of words used in a particular language",
        user_id=test_user.id
    )
    db_session.add(flashcard)
    db_session.commit()
    
    assert flashcard.id is not None
    assert flashcard.word == "vocabulary"
    assert flashcard.definition == "A body of words used in a particular language"
    assert flashcard.user_id == test_user.id
    assert flashcard.bin_number == 0
    assert flashcard.incorrect_count == 0
    assert isinstance(flashcard.created_at, datetime)
    assert isinstance(flashcard.updated_at, datetime)
    assert isinstance(flashcard.next_review, datetime)
    assert flashcard.is_hard_to_remember is False


def test_flashcard_str_representation(test_flashcard):
    """Test flashcard string representation."""
    str_repr = str(test_flashcard)
    assert "test" in str_repr
    assert "A test definition" in str_repr


def test_flashcard_repr_representation(test_flashcard):
    """Test flashcard repr representation."""
    repr_str = repr(test_flashcard)
    assert "Flashcard" in repr_str
    assert test_flashcard.id in repr_str
    assert "test" in repr_str
    assert "bin=0" in repr_str


def test_user_flashcard_relationship(db_session, test_user):
    """Test the relationship between user and flashcards."""
    # Create flashcards for the user
    flashcard1 = Flashcard(
        word="first",
        definition="First definition",
        user_id=test_user.id
    )
    flashcard2 = Flashcard(
        word="second", 
        definition="Second definition",
        user_id=test_user.id
    )
    
    db_session.add_all([flashcard1, flashcard2])
    db_session.commit()
    db_session.refresh(test_user)
    
    # Test the relationship
    assert len(test_user.flashcards) == 2
    assert flashcard1 in test_user.flashcards
    assert flashcard2 in test_user.flashcards
    
    # Test reverse relationship
    assert flashcard1.user == test_user
    assert flashcard2.user == test_user


def test_user_cascade_delete(db_session, test_user):
    """Test that deleting a user cascades to delete flashcards."""
    # Create flashcards for the user
    flashcard1 = Flashcard(
        word="cascade1",
        definition="First cascade test",
        user_id=test_user.id
    )
    flashcard2 = Flashcard(
        word="cascade2",
        definition="Second cascade test", 
        user_id=test_user.id
    )
    
    db_session.add_all([flashcard1, flashcard2])
    db_session.commit()
    
    flashcard_ids = [flashcard1.id, flashcard2.id]
    
    # Delete the user
    db_session.delete(test_user)
    db_session.commit()
    
    # Check that flashcards are also deleted
    remaining_flashcards = db_session.query(Flashcard).filter(
        Flashcard.id.in_(flashcard_ids)
    ).all()
    assert len(remaining_flashcards) == 0


def test_flashcard_defaults(db_session, test_user):
    """Test that flashcard fields have correct defaults."""
    flashcard = Flashcard(
        word="defaults_test",
        definition="Testing defaults",
        user_id=test_user.id
    )
    db_session.add(flashcard)
    db_session.commit()
    
    assert flashcard.bin_number == 0
    assert flashcard.incorrect_count == 0
    assert flashcard.is_hard_to_remember is False
    assert flashcard.next_review is not None
    assert flashcard.created_at is not None
    assert flashcard.updated_at is not None
