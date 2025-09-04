#!/bin/bash

# Start the FastAPI backend server

echo "🚀 Starting Flashcard Backend Server..."

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_dev.sh first."
    exit 1
fi

# Activate virtual environment
source ../.venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed. Please run setup_dev.sh first."
    exit 1
fi

# Start the server
echo "📚 Starting FastAPI server at http://localhost:8000"
echo "📖 API documentation will be available at http://localhost:8000/docs"
echo "🔄 Server will auto-reload on file changes"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
