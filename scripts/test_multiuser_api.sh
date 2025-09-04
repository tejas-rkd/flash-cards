#!/bin/bash

# Test script for multiuser API

echo "🧪 Testing Multiuser API..."

API_BASE="http://localhost:8000/api/v1"

echo ""
echo "1. Testing Users API..."
echo "📋 Getting all users:"
curl -s -X GET "$API_BASE/users" -H "accept: application/json" | python3 -m json.tool

echo ""
echo "2. Creating a test user..."
echo "👤 Creating user 'Test User':"
USER_RESPONSE=$(curl -s -X POST "$API_BASE/users" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User"}')
echo $USER_RESPONSE | python3 -m json.tool

# Extract user ID for further tests
USER_ID=$(echo $USER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created user ID: $USER_ID"

echo ""
echo "3. Testing Flashcards API..."
echo "📚 Creating a flashcard for the test user:"
CARD_RESPONSE=$(curl -s -X POST "$API_BASE/flashcards" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"word\": \"Hello\", \"definition\": \"A greeting\", \"user_id\": \"$USER_ID\"}")
echo $CARD_RESPONSE | python3 -m json.tool

echo ""
echo "📋 Getting flashcards for the test user:"
curl -s -X GET "$API_BASE/flashcards?user_id=$USER_ID" -H "accept: application/json" | python3 -m json.tool

echo ""
echo "4. Testing Study API..."
echo "📖 Getting study status for the test user:"
curl -s -X GET "$API_BASE/study/status?user_id=$USER_ID" -H "accept: application/json" | python3 -m json.tool

echo ""
echo "📝 Getting next card for the test user:"
curl -s -X GET "$API_BASE/study/next?user_id=$USER_ID" -H "accept: application/json" | python3 -m json.tool

echo ""
echo "✅ API testing completed!"
