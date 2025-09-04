#!/bin/bash

# Start the complete flashcard application

echo "🚀 Starting Flashcard Application..."
echo "===================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    exit 0
}

# Set up cleanup on script exit
trap cleanup SIGINT SIGTERM

# Check if database is available
echo "🔍 Checking database connection..."
cd /home/tejas/oss/flash
if ! ./scripts/test_db.sh > /dev/null 2>&1; then
    echo "❌ Database not properly configured."
    echo "💡 Please run: ./scripts/setup_db_dev.sh"
    exit 1
fi
echo "✅ Database connection verified"

# Start backend
echo ""
echo "🔧 Starting backend server..."
cd backend
source ../.venv/bin/activate
python main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📚 API available at: http://localhost:8000"
echo "📖 API docs at: http://localhost:8000/docs"

# Wait a moment for backend to start
sleep 3

# Start frontend
echo ""
echo "⚛️  Starting frontend server..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm start &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "🌐 Application available at: http://localhost:3000"

echo ""
echo "🎉 Application is running!"
echo "================================="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop
wait
