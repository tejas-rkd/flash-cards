"""
API routes for user operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.db import get_db
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserList,
)
from app.services import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user: User data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user name already exists or max users exceeded
    """
    try:
        db_user = UserService.create_user(db, user)
        return UserResponse.from_orm(db_user)
    except ValueError as e:
        logger.warning(f"Failed to create user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=UserList)
def get_users(
    db: Session = Depends(get_db)
) -> UserList:
    """
    Get all users.
    
    Args:
        db: Database session
        
    Returns:
        List of all users
    """
    users = UserService.get_all_users(db)
    total = UserService.count_users(db)
    
    return UserList(
        users=[UserResponse.from_orm(user) for user in users],
        total=total
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update an existing user.
    
    Args:
        user_id: User ID
        user_update: Update data
        db: Database session
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found or name conflict
    """
    try:
        updated_user = UserService.update_user(db, user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.from_orm(updated_user)
    except ValueError as e:
        logger.warning(f"Failed to update user {user_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a user and all their flashcards.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found
    """
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}
