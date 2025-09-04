#!/bin/bash

# Start the complete flashcard application in development mode

echo "🚀 Starting Flashcard Application (Multiuser Version)"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if backend dependencies are met
echo "📋 Checking backend..."
cd backend
if [ ! -d "../.venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_dev.sh first."
    exit 1
fi

if ! ../.venv/bin/python -c "import fastapi" 2>/dev/null; then
    echo "❌ Backend dependencies not installed. Please run setup_dev.sh first."
    exit 1
fi

# Check if frontend dependencies are met
echo "📋 Checking frontend..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "❌ Frontend dependencies not installed. Please run setup_dev.sh first."
    exit 1
fi

echo ""
echo "✅ Starting backend server..."
cd ../backend
bash start_server.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "✅ Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Application started successfully!"
echo "📚 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Features:"
echo "   - Multiuser support (max 5 users)"
echo "   - User-specific flashcards"
echo "   - Spaced repetition learning"
echo "   - User management (add/delete users)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
