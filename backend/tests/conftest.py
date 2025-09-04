"""
Test configuration and fixtures for the flashcard application tests.
"""
import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.db import get_db
from app.models.flashcard import Base
from app.models.user import User
from app.models.flashcard import Flashcard


@pytest.fixture(scope="session")
def test_db():
    """Create a test database for the session."""
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("./test.db")
    except FileNotFoundError:
        pass


@pytest.fixture
def db_session(test_db):
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with test database."""
    app = create_app()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_flashcard(db_session, test_user):
    """Create a test flashcard."""
    flashcard = Flashcard(
        word="test",
        definition="A test definition",
        user_id=test_user.id,
        bin_number=0,
        incorrect_count=0
    )
    db_session.add(flashcard)
    db_session.commit()
    db_session.refresh(flashcard)
    return flashcard


@pytest.fixture
def multiple_flashcards(db_session, test_user):
    """Create multiple test flashcards."""
    flashcards = []
    words = ["apple", "banana", "cherry", "date", "elderberry"]
    
    for i, word in enumerate(words):
        flashcard = Flashcard(
            word=word,
            definition=f"Definition for {word}",
            user_id=test_user.id,
            bin_number=i % 3,  # Mix of different bins
            incorrect_count=i % 2  # Some correct, some incorrect
        )
        db_session.add(flashcard)
        flashcards.append(flashcard)
    
    db_session.commit()
    for flashcard in flashcards:
        db_session.refresh(flashcard)
    
    return flashcards


@pytest.fixture
def second_user(db_session):
    """Create a second test user."""
    user = User(
        name="Second User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
