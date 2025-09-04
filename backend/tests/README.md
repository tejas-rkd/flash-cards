# Backend Tests

This directory contains comprehensive tests for the Flashcard Learning API backend.

## Test Structure

```
tests/
├── __init__.py                  # Test package initialization
├── conftest.py                  # Pytest configuration and fixtures
├── test_main.py                 # Main application tests
├── test_models.py               # Database model tests
├── test_config.py               # Configuration and database tests
├── test_flashcard_service.py    # Flashcard service unit tests
├── test_study_service.py        # Study service unit tests
├── test_user_service.py         # User service unit tests
├── test_api_flashcards.py       # Flashcard API endpoint tests
├── test_api_study.py           # Study API endpoint tests
└── test_api_users.py           # User API endpoint tests
```

## Test Categories

### Unit Tests
- **Models** (`test_models.py`): Database model functionality
- **Services** (`test_*_service.py`): Business logic layer tests
- **Configuration** (`test_config.py`): Settings and database setup

### Integration Tests
- **API Endpoints** (`test_api_*.py`): Full HTTP request/response testing
- **Workflows** (within API tests): Complete user workflows

## Running Tests

### Quick Start
```bash
# Make the test script executable and run it
chmod +x run_tests.sh
./run_tests.sh
```

### Using Make Commands
```bash
# Set up development environment
make dev-setup

# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test categories
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-api          # API tests only

# Code quality checks
make lint              # Linting
make format            # Code formatting
make security          # Security checks
make check-all         # All quality checks

# Clean up
make clean
```

### Using Pytest Directly
```bash
# Set up environment
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run tests by marker
pytest tests/ -v -m "unit"
pytest tests/ -v -m "integration"
pytest tests/ -v -m "api"
```

## Test Configuration

Tests are configured through `pytest.ini`:
- Coverage threshold: 80%
- Test discovery patterns
- Markers for categorizing tests
- Coverage reporting options

## Test Database

Tests use SQLite in-memory database for speed and isolation:
- Each test gets a fresh database
- Fixtures provide common test data
- Automatic cleanup after tests

## Key Test Fixtures

### Database Fixtures
- `test_db`: Test database engine (session-scoped)
- `db_session`: Database session (function-scoped)

### Data Fixtures
- `test_user`: Creates a test user
- `second_user`: Creates a second test user
- `test_flashcard`: Creates a test flashcard
- `multiple_flashcards`: Creates multiple test flashcards

### Application Fixtures
- `client`: FastAPI test client with test database

## Test Coverage

The test suite aims for comprehensive coverage:

### Models (test_models.py)
- User and Flashcard model creation
- Relationships and constraints
- String representations
- Cascade deletions

### Services
- **Flashcard Service**: CRUD operations, validation, user limits
- **Study Service**: Spaced repetition algorithm, card selection
- **User Service**: User management, uniqueness constraints

### API Endpoints
- **Flashcard API**: All CRUD operations, pagination, filtering
- **Study API**: Next card retrieval, reviews, study status
- **User API**: User management operations

### Configuration
- Settings loading and validation
- Database setup and relationships
- Environment variable handling

## GitHub Actions Integration

The tests are integrated with GitHub Actions (`.github/workflows/backend-tests.yml`):

### Test Matrix
- Multiple Python versions (3.9, 3.10, 3.11, 3.12)
- Unit tests with SQLite
- Integration tests with PostgreSQL

### Quality Gates
- Code linting with flake8
- Security scanning with bandit
- Dependency security checks with safety
- Coverage reporting to Codecov

### Workflow Triggers
- Push to main/develop/prod branches
- Pull requests targeting main/develop/prod
- Only runs when backend files change

## Best Practices

### Writing Tests
1. **Descriptive Names**: Test function names should describe what they test
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Isolation**: Each test should be independent
4. **Mock External Dependencies**: Use fixtures for test data

### Test Data
1. **Use Fixtures**: Create reusable test data with fixtures
2. **Minimal Data**: Only create the minimum data needed for each test
3. **Clean State**: Each test starts with a clean database

### Assertions
1. **Specific Assertions**: Test exact values when possible
2. **Error Cases**: Test both success and failure scenarios
3. **Edge Cases**: Test boundary conditions and limits

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

**Database Issues**
```bash
# Clean up any leftover test databases
make clean
```

**Dependency Issues**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Running Specific Tests
```bash
# Run a specific test function
pytest tests/test_models.py::test_user_creation -v

# Run tests matching a pattern
pytest tests/ -k "test_create" -v

# Run tests and stop on first failure
pytest tests/ -x
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:
- Fast execution with parallel test support
- Comprehensive coverage reporting
- Security and quality checks
- Integration with external services (PostgreSQL)

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain coverage above 80%
4. Follow existing test patterns
5. Add appropriate test markers
