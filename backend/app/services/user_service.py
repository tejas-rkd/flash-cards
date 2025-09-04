"""
Service layer for user operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from app.models import User
from app.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If user name already exists or maximum users exceeded
        """
        # Check if we already have 5 users
        user_count = db.query(User).count()
        if user_count >= 5:
            raise ValueError("Maximum number of users (5) already reached")
        
        # Check if name already exists
        existing_user = db.query(User).filter(User.name == user_data.name).first()
        if existing_user:
            raise ValueError(f"User with name '{user_data.name}' already exists")
        
        db_user = User(name=user_data.name)
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"✅ Created user: {user_data.name}")
            return db_user
        except IntegrityError:
            db.rollback()
            logger.error(f"⚠️ Failed to create user due to integrity error: {user_data.name}")
            raise ValueError(f"User with name '{user_data.name}' already exists")
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """
        Get all users.
        
        Args:
            db: Database session
            
        Returns:
            List of all users
        """
        return db.query(User).order_by(User.created_at).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_name(db: Session, name: str) -> Optional[User]:
        """
        Get a user by name.
        
        Args:
            db: Database session
            name: User name
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.name == name).first()
    
    @staticmethod
    def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            db: Database session
            user_id: User ID
            user_update: Update data
            
        Returns:
            Updated user if found, None otherwise
            
        Raises:
            ValueError: If new name already exists
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        if user_update.name is not None:
            # Check if new name already exists (except for current user)
            existing_user = db.query(User).filter(
                User.name == user_update.name,
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError(f"User with name '{user_update.name}' already exists")
            
            db_user.name = user_update.name
        
        try:
            db.commit()
            db.refresh(db_user)
            logger.info(f"✅ Updated user: {user_id}")
            return db_user
        except IntegrityError:
            db.rollback()
            logger.error(f"⚠️ Failed to update user due to integrity error: {user_id}")
            raise ValueError(f"User with name '{user_update.name}' already exists")
    
    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """
        Delete a user and all their flashcards.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        try:
            db.delete(db_user)
            db.commit()
            logger.info(f"✅ Deleted user: {user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"⚠️ Failed to delete user {user_id}: {e}")
            raise
    
    @staticmethod
    def count_users(db: Session) -> int:
        """
        Count total number of users.
        
        Args:
            db: Database session
            
        Returns:
            Total number of users
        """
        return db.query(User).count()
