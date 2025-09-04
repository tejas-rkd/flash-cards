"""
Pydantic schemas for user operations.
"""
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional


class UserBase(BaseModel):
    """Base schema for user data."""
    name: str = Field(..., min_length=1, max_length=100, description="The user's name")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        """Ensure name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else v


class UserResponse(UserBase):
    """Schema for user responses."""
    id: str = Field(..., description="Unique identifier for the user")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: Optional[datetime] = Field(None, description="When the user was last updated")
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Schema for user lists."""
    users: list[UserResponse]
    total: int = Field(..., ge=0, description="Total number of users")
