#!/bin/bash

# Backend Test Runner Script
# This script runs all the tests for the flashcard backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the backend directory."
    exit 1
fi

print_status "Starting backend test suite..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
print_status "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional testing tools
pip install flake8 bandit safety black isort

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Code formatting check
print_status "Checking code formatting with black..."
black --check --diff app/ tests/ || {
    print_warning "Code formatting issues found. Run 'black app/ tests/' to fix."
}

# Import sorting check
print_status "Checking import sorting with isort..."
isort --check-only --diff app/ tests/ || {
    print_warning "Import sorting issues found. Run 'isort app/ tests/' to fix."
}

# Linting
print_status "Running linting with flake8..."
flake8 app/ tests/ --max-line-length=127 --max-complexity=10 || {
    print_warning "Linting issues found."
}

# Security checks
print_status "Running security checks with bandit..."
bandit -r app/ -ll || {
    print_warning "Security issues found."
}

# Dependency security check
print_status "Checking for known security vulnerabilities..."
safety check || {
    print_warning "Security vulnerabilities found in dependencies."
}

# Run tests
print_status "Running unit tests..."
pytest tests/ -v --tb=short || {
    print_error "Tests failed!"
    exit 1
}

# Run tests with coverage
print_status "Running tests with coverage..."
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=80 || {
    print_error "Coverage requirements not met!"
    exit 1
}

print_success "All tests passed! ✨"
print_status "Coverage report generated in htmlcov/index.html"

# Check if coverage directory exists and open it
if [ -d "htmlcov" ]; then
    print_status "You can view the coverage report by opening htmlcov/index.html in your browser"
fi

print_success "Backend test suite completed successfully! 🎉"
