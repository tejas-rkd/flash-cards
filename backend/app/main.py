"""
Main FastAPI application factory and configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.db import create_tables
from app.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI app instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize database tables on startup."""
        try:
            create_tables()
            logger.info("✅ Database initialization completed")
        except Exception as e:
            logger.error(f"⚠️ Database initialization failed: {e}")
            logger.error("📝 Please ensure PostgreSQL is running and properly configured")
    
    # Add health check endpoints
    @app.get("/")
    def root():
        """Root endpoint."""
        return {
            "message": f"{settings.PROJECT_NAME} is running",
            "version": settings.VERSION,
            "status": "healthy"
        }
    
    @app.get("/health")
    def health_check():
        """Health check endpoint for Cloud Run."""
        return {"status": "healthy", "service": "flashcard-backend"}
    
    return app


# Create app instance
app = create_app()
