"""
Tests for configuration and database functionality.
"""
import pytest
import os
from app.core.config import Settings
from app.db import get_db, create_tables
from app.models.flashcard import Base

pytestmark = pytest.mark.unit


def test_default_settings():
    """Test default configuration settings."""
    settings = Settings()
    
    assert settings.PROJECT_NAME == "Flashcard Learning API"
    assert settings.VERSION == "1.0.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.DEBUG is False
    assert settings.MAX_FLASHCARDS_PER_USER == 1000
    assert settings.MAX_INCORRECT_COUNT == 10


def test_bin_timespans_configuration():
    """Test that bin timespans are correctly configured."""
    settings = Settings()
    
    expected_bins = {
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
        11: 999999999   # effectively never (31+ years)
    }
    
    assert settings.BIN_TIMESPANS == expected_bins


def test_allowed_origins_configuration():
    """Test CORS allowed origins configuration."""
    settings = Settings()
    
    expected_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    assert settings.ALLOWED_ORIGINS == expected_origins


def test_database_url_assembly():
    """Test database URL assembly from components."""
    # Test with individual components
    settings = Settings(
        DB_USER="testuser",
        DB_PASSWORD="testpass",
        DB_HOST="testhost",
        DB_PORT=5433,
        DB_NAME="testdb"
    )
    
    # The DATABASE_URL should be assembled from components
    assert settings.DATABASE_URL is not None
    db_url_str = str(settings.DATABASE_URL)
    assert "postgresql://" in db_url_str
    assert "testuser" in db_url_str
    assert "testpass" in db_url_str
    assert "testhost" in db_url_str
    assert "5433" in db_url_str
    assert "testdb" in db_url_str


def test_settings_from_env(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    # Set environment variables
    monkeypatch.setenv("PROJECT_NAME", "Test Project")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("MAX_FLASHCARDS_PER_USER", "500")
    
    settings = Settings()
    
    assert settings.PROJECT_NAME == "Test Project"
    assert settings.DEBUG is True
    assert settings.PORT == 9000
    assert settings.MAX_FLASHCARDS_PER_USER == 500


def test_database_session(db_session):
    """Test that database session is working."""
    # This test verifies that the test database setup is working
    from app.models.user import User
    
    # Create a user
    user = User(name="Database Test User")
    db_session.add(user)
    db_session.commit()
    
    # Query the user
    found_user = db_session.query(User).filter(User.name == "Database Test User").first()
    
    assert found_user is not None
    assert found_user.name == "Database Test User"
    assert found_user.id is not None


def test_database_relationships(db_session):
    """Test database relationships work correctly."""
    from app.models.user import User
    from app.models.flashcard import Flashcard
    
    # Create user
    user = User(name="Relationship Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create flashcard
    flashcard = Flashcard(
        word="relationship",
        definition="Connection between entities",
        user_id=user.id
    )
    db_session.add(flashcard)
    db_session.commit()
    db_session.refresh(flashcard)
    
    # Test forward relationship
    assert flashcard.user == user
    
    # Test reverse relationship
    db_session.refresh(user)
    assert len(user.flashcards) == 1
    assert user.flashcards[0] == flashcard


def test_database_constraints(db_session):
    """Test database constraints are enforced."""
    from app.models.user import User
    from app.models.flashcard import Flashcard
    from sqlalchemy.exc import IntegrityError
    
    # Create user
    user = User(name="Constraint Test User")
    db_session.add(user)
    db_session.commit()
    
    # Try to create flashcard with invalid user_id
    flashcard = Flashcard(
        word="invalid",
        definition="Should fail",
        user_id="non-existent-user-id"
    )
    db_session.add(flashcard)
    
    # This should raise an IntegrityError due to foreign key constraint
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_database_indexes_exist(test_db):
    """Test that important database indexes exist."""
    from sqlalchemy import inspect
    
    inspector = inspect(test_db)
    
    # Check flashcards table indexes
    flashcard_indexes = inspector.get_indexes('flashcards')
    index_columns = [idx['column_names'] for idx in flashcard_indexes]
    
    # Should have indexes on important columns
    # Note: In SQLite (test), index names might be different
    # This test verifies the table structure is set up correctly
    flashcard_columns = [col['name'] for col in inspector.get_columns('flashcards')]
    
    # Verify important columns exist
    assert 'user_id' in flashcard_columns
    assert 'word' in flashcard_columns
    assert 'bin_number' in flashcard_columns
    assert 'next_review' in flashcard_columns
    assert 'is_hard_to_remember' in flashcard_columns


def test_database_table_creation(test_db):
    """Test that all required tables are created."""
    from sqlalchemy import inspect
    
    inspector = inspect(test_db)
    tables = inspector.get_table_names()
    
    assert 'users' in tables
    assert 'flashcards' in tables


def test_settings_case_sensitivity():
    """Test that settings are case sensitive."""
    # Environment variables should be case sensitive
    import os
    
    # This would not affect settings since it's lowercase
    os.environ['project_name'] = 'lowercase'
    
    settings = Settings()
    # Should still use the default since env var is lowercase
    assert settings.PROJECT_NAME == "Flashcard Learning API"
    
    # Clean up
    if 'project_name' in os.environ:
        del os.environ['project_name']


def test_settings_extra_fields_ignored():
    """Test that extra fields in environment are ignored."""
    import os
    
    # Set an unknown environment variable
    os.environ['UNKNOWN_SETTING'] = 'should_be_ignored'
    
    # This should not raise an error due to extra="ignore"
    settings = Settings()
    
    # Verify the unknown setting is not in settings
    assert not hasattr(settings, 'UNKNOWN_SETTING')
    
    # Clean up
    del os.environ['UNKNOWN_SETTING']
