#!/bin/bash

# Development setup script

echo "🚀 Setting up Flashcard App for development..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "../.venv" ]; then
    cd ..
    python3 -m venv .venv
    cd backend
fi

# Activate virtual environment and install dependencies
source ../.venv/bin/activate
pip install -r requirements.txt

# Test backend imports
echo "🧪 Testing backend imports..."
if python test_imports.py; then
    echo "✅ Backend setup completed successfully!"
else
    echo "❌ Backend setup failed!"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please update the DATABASE_URL in backend/.env file"
fi

cd ..

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..

echo "✅ Setup completed!"
echo ""
echo "🔧 Next steps:"
echo "1. Set up PostgreSQL database (run ./scripts/setup_db.sh)"
echo "2. Update backend/.env with your database URL"
echo "3. Start the backend: cd backend && source venv/bin/activate && python main.py"
echo "4. Start the frontend: cd frontend && npm start"
echo ""
echo "🌐 Access the app at http://localhost:3000"
echo "📚 API docs available at http://localhost:8000/docs"
