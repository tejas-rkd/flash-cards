"""
Core configuration settings for the application.
"""
import os
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Basic App Config
    PROJECT_NAME: str = "Flashcard Learning API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI backend for spaced repetition flashcard learning"
    API_V1_STR: str = "/api/v1"
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Database Config
    DATABASE_URL: Optional[PostgresDsn] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "flashcard_user"
    DB_PASSWORD: str = "flashcard_password"
    DB_NAME: str = "flashcards"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        """Build database URL from individual components if not provided."""
        if isinstance(v, str):
            return v
        
        # Get values from the validation context
        values = info.data if hasattr(info, 'data') else {}
        
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("DB_USER", "flashcard_user"),
            password=values.get("DB_PASSWORD", "flashcard_password"),
            host=values.get("DB_HOST", "localhost"),
            port=values.get("DB_PORT", 5432),
            path=values.get("DB_NAME", "flashcards"),
        )
    
    # CORS Config
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Spaced Repetition Config
    MAX_INCORRECT_COUNT: int = 10
    MAX_FLASHCARDS_PER_USER: int = 1000
    BIN_TIMESPANS: dict[int, int] = {
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
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"  # Allow extra fields in .env without errors
    }


# Global settings instance
settings = Settings()
