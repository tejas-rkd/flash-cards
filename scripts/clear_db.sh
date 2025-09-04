#!/bin/bash

# Clear all database contents script

echo "🗑️  Clearing all database contents..."

# Database configuration (should match your .env file)
DB_NAME="flashcards"
DB_USER="flashcard_user"
DB_PASSWORD="flashcard_password"
DB_HOST="localhost"
DB_PORT="5432"

echo "📋 Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Warning prompt
echo "⚠️  WARNING: This will delete ALL users and flashcards in the database!"
echo "This action cannot be undone."
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    echo "❌ Operation cancelled."
    exit 0
fi

echo ""
echo "🔄 Clearing database contents..."

# Set password for psql commands
export PGPASSWORD=$DB_PASSWORD

# Method 1: Delete all data from tables (preserves table structure)
echo "📝 Deleting all user and flashcard data..."

# Delete flashcards first (due to foreign key constraints)
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM flashcards;" > /dev/null 2>&1; then
    echo "✅ All flashcard data deleted"
else
    echo "❌ Failed to delete flashcard data"
    exit 1
fi

# Delete users
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM users;" > /dev/null 2>&1; then
    echo "✅ All user data deleted"
else
    echo "❌ Failed to delete user data"
    exit 1
fi

# Get count of remaining records
flashcard_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards;")
user_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users;")

echo ""
echo "📊 Database Status:"
echo "  Users table: $user_count records"
echo "  Flashcards table: $flashcard_count records"

if [ "$flashcard_count" -eq 0 ] && [ "$user_count" -eq 0 ]; then
    echo "✅ Database cleared successfully!"
    echo ""
    echo "💡 The database is now empty and ready for new data."
    echo "🔄 You can start by creating users and adding flashcards through the web interface."
else
    echo "⚠️  Warning: Database may not be completely cleared."
fi

echo ""
echo "🧪 To verify the database is empty, run:"
echo "PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c 'SELECT COUNT(*) as users FROM users; SELECT COUNT(*) as flashcards FROM flashcards;'"
