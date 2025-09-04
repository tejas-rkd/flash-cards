"""
API v1 router configuration.
"""
from fastapi import APIRouter

from .flashcards import router as flashcards_router
from .study import router as study_router
from .users import router as users_router

# Create main v1 API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    flashcards_router,
    prefix="/flashcards",
    tags=["flashcards"]
)

api_router.include_router(
    study_router,
    prefix="/study",
    tags=["study"]
)
