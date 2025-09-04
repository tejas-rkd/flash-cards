# Makefile for Backend Development

.PHONY: help install test test-cov test-unit test-integration lint format clean coverage security

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-api      - Run API tests only"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with black and isort"
	@echo "  security      - Run security checks"
	@echo "  coverage      - Generate coverage report"
	@echo "  clean         - Clean up generated files"
	@echo "  dev-setup     - Set up development environment"

# Set up development environment
dev-setup:
	python3 -m venv venv || true
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install black isort flake8 bandit safety
	@echo "Development environment set up! Activate with: source venv/bin/activate"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run all tests
test:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v

# Run tests with coverage
test-cov:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov

# Run unit tests only
test-unit:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v -m "unit"

# Run integration tests only
test-integration:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v -m "integration"

# Run API tests only
test-api:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v -m "api"

# Run specific test file
test-file:
	@read -p "Enter test file name (e.g., test_models.py): " file; \
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/$$file -v

# Run linting
lint:
	flake8 app/ tests/ --max-line-length=127 --max-complexity=10
	black --check app/ tests/
	isort --check-only app/ tests/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Security checks
security:
	bandit -r app/ -ll
	safety check

# Generate coverage report
coverage:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ --cov=app --cov-report=html:htmlcov --cov-report=xml:coverage.xml
	@echo "Coverage report generated in htmlcov/index.html"

# Clean up generated files
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test.db
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Quick development test - just run fast tests
test-quick:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v --tb=short -x

# Run tests in parallel (if pytest-xdist is installed)
test-parallel:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && pytest tests/ -v -n auto

# Watch tests (if pytest-watch is installed)
test-watch:
	export PYTHONPATH=$$PYTHONPATH:$(PWD) && ptw tests/ app/

# All quality checks
check-all: lint security test-cov
	@echo "All quality checks completed!"

# CI pipeline (what GitHub Actions runs)
ci: lint security test-cov
	@echo "CI pipeline completed successfully!"
