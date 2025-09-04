# Backend Architecture Documentation

## Overview

The flashcard backend has been refactored to follow modern FastAPI best practices with a clean, modular architecture that separates concerns and makes the codebase maintainable and scalable.

## Architecture Overview

```
backend/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app factory
│   ├── api/                     # API route definitions
│   │   ├── __init__.py
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py      # Router configuration
│   │       ├── flashcards.py    # Flashcard endpoints
│   │       └── study.py         # Study session endpoints
│   ├── core/                    # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py            # Application settings
│   │   ├── exceptions.py        # Exception handlers
│   │   └── security.py          # Security utilities
│   ├── db/                      # Database configuration
│   │   ├── __init__.py
│   │   └── database.py          # DB session management
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── flashcard.py         # Flashcard model
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── flashcard.py         # Flashcard schemas
│   │   └── study.py             # Study schemas
│   └── services/                # Business logic
│       ├── __init__.py
│       ├── flashcard_service.py # Flashcard operations
│       └── study_service.py     # Study session logic
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

## Key Architectural Principles

### 1. Separation of Concerns
- **Models**: SQLAlchemy ORM models for database entities
- **Schemas**: Pydantic models for request/response validation
- **Services**: Business logic and data operations
- **Routes**: HTTP endpoint definitions
- **Core**: Configuration and cross-cutting concerns

### 2. Dependency Injection
- Database sessions injected via FastAPI's `Depends()`
- Configuration accessed through singleton settings object
- Service classes instantiated as needed

### 3. Clean API Design
- RESTful endpoints with proper HTTP status codes
- Versioned API routes (`/api/v1/`)
- Comprehensive request/response validation
- Detailed error handling with consistent format

### 4. Configuration Management
- Environment-based configuration using Pydantic Settings
- Type-safe configuration with validation
- Support for `.env` files and environment variables

### 5. Error Handling
- Centralized exception handling
- Proper HTTP status codes
- Structured error responses
- Logging for debugging

## Core Components

### Configuration (`app/core/config.py`)
- Centralized settings management
- Database connection configuration
- CORS and security settings
- Spaced repetition algorithm parameters

### Models (`app/models/flashcard.py`)
- SQLAlchemy ORM model for flashcards
- Proper indexing for performance
- Timestamps for auditing
- Constraints for data integrity

### Services (`app/services/`)
- **FlashcardService**: CRUD operations for flashcards
- **StudyService**: Spaced repetition algorithm implementation
- Error handling and validation
- Transaction management

### API Routes (`app/api/v1/`)
- **Flashcards API**: Full CRUD operations with pagination
- **Study API**: Spaced repetition review workflow
- Request/response validation
- Proper HTTP status codes

### Database (`app/db/database.py`)
- Connection pool management
- Session lifecycle management
- Automatic table creation
- Error handling and connection recovery

## API Endpoints

### Flashcards API (`/api/v1/flashcards`)
- `POST /` - Create new flashcard
- `GET /` - List flashcards (paginated)
- `GET /{id}` - Get specific flashcard
- `PUT /{id}` - Update flashcard
- `DELETE /{id}` - Delete flashcard

### Study API (`/api/v1/study`)
- `GET /next` - Get next card for review
- `POST /{id}/review` - Submit card review
- `GET /status` - Get study session status

## Best Practices Implemented

### 1. Type Safety
- Full type annotations throughout codebase
- Pydantic models for runtime validation
- SQLAlchemy 2.0 style with proper typing

### 2. Error Handling
- Custom exception classes
- Proper HTTP status codes
- Structured error responses
- Comprehensive logging

### 3. Database Design
- Proper foreign keys and constraints
- Indexing for performance
- Connection pooling
- Transaction management

### 4. Security
- Input validation and sanitization
- SQL injection prevention via ORM
- CORS configuration
- Prepared for future authentication

### 5. Performance
- Database connection pooling
- Efficient queries with proper indexing
- Pagination for large datasets
- Lazy loading where appropriate

### 6. Maintainability
- Clear separation of concerns
- Comprehensive documentation
- Consistent coding style
- Modular architecture

### 7. Testing Ready
- Dependency injection for easy mocking
- Separate business logic from web framework
- Clear interfaces between layers
- Configuration via environment variables

## Future Enhancements

### 1. Authentication & Authorization
- JWT token authentication
- User management
- Role-based access control
- Rate limiting

### 2. Advanced Features
- Card categories and tags
- Study session analytics
- Import/export functionality
- Search and filtering

### 3. Performance Optimizations
- Redis caching layer
- Database query optimization
- Background task processing
- API response caching

### 4. Monitoring & Observability
- Structured logging with correlation IDs
- Metrics collection (Prometheus)
- Health checks and monitoring
- Performance tracking

### 5. Testing
- Unit tests for services
- Integration tests for API endpoints
- Database migration tests
- Performance and load testing

## Development Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Run Application**
   ```bash
   python main.py
   ```

4. **Access Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Migration from Legacy Code

The refactoring maintains API compatibility while providing:
- **Better Error Handling**: Structured responses and proper status codes
- **Enhanced Validation**: Comprehensive input validation with Pydantic
- **Improved Performance**: Connection pooling and optimized queries
- **Better Maintainability**: Clean separation of concerns
- **Future Extensibility**: Prepared for authentication, caching, and scaling
