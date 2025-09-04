#!/bin/bash

# Database connection test script

echo "🔍 Testing PostgreSQL Database Setup..."

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

# Test 1: Check if PostgreSQL is running
echo "🧪 Test 1: Checking if PostgreSQL is running..."
if sudo systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL service is running"
else
    echo "❌ PostgreSQL service is not running"
    echo "💡 Try: sudo systemctl start postgresql"
    exit 1
fi

# Test 2: Check if we can connect as postgres user
echo ""
echo "🧪 Test 2: Testing postgres superuser connection..."
if sudo -u postgres psql -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Can connect as postgres user"
else
    echo "❌ Cannot connect as postgres user"
    echo "💡 PostgreSQL may not be properly configured"
    exit 1
fi

# Test 3: Check if our database exists
echo ""
echo "🧪 Test 3: Checking if database '$DB_NAME' exists..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "✅ Database '$DB_NAME' exists"
else
    echo "❌ Database '$DB_NAME' does not exist"
    echo "💡 Run: ./setup_db_dev.sh to create it"
    exit 1
fi

# Test 4: Check if our user exists
echo ""
echo "🧪 Test 4: Checking if user '$DB_USER' exists..."
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "✅ User '$DB_USER' exists"
else
    echo "❌ User '$DB_USER' does not exist"
    echo "💡 Run: ./setup_db_dev.sh to create it"
    exit 1
fi

# Test 5: Test connection with our user
echo ""
echo "🧪 Test 5: Testing connection as '$DB_USER'..."
export PGPASSWORD=$DB_PASSWORD
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT current_user, current_database();" > /dev/null 2>&1; then
    echo "✅ Can connect as '$DB_USER' to database '$DB_NAME'"
else
    echo "❌ Cannot connect as '$DB_USER' to database '$DB_NAME'"
    echo "💡 Check password and user permissions"
    exit 1
fi

# Test 6: Test table creation permissions
echo ""
echo "🧪 Test 6: Testing table creation permissions..."
export PGPASSWORD=$DB_PASSWORD
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE TABLE test_permissions (id INTEGER); DROP TABLE test_permissions;" > /dev/null 2>&1; then
    echo "✅ User has permission to create tables"
else
    echo "❌ User does not have permission to create tables"
    echo "💡 Run: ./setup_db_dev.sh to fix permissions"
    exit 1
fi

# Test 7: Check if required tables exist (multiuser schema)
echo ""
echo "🧪 Test 7: Checking if required tables exist..."
export PGPASSWORD=$DB_PASSWORD

# Check for users table
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d users" > /dev/null 2>&1; then
    echo "✅ Users table exists"
else
    echo "❌ Users table does not exist"
    echo "💡 Run: ./migrate_to_multiuser.sh to create multiuser schema"
    exit 1
fi

# Check for flashcards table
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d flashcards" > /dev/null 2>&1; then
    echo "✅ Flashcards table exists"
else
    echo "❌ Flashcards table does not exist"
    echo "💡 Run: ./setup_db_dev.sh to create tables"
    exit 1
fi

# Test 8: Check table structure (multiuser schema)
echo ""
echo "🧪 Test 8: Verifying table structure..."
export PGPASSWORD=$DB_PASSWORD

# Check if flashcards table has user_id column (multiuser feature)
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d flashcards" | grep -q "user_id"; then
    echo "✅ Flashcards table has user_id column (multiuser ready)"
else
    echo "❌ Flashcards table missing user_id column"
    echo "💡 Run: ./migrate_to_multiuser.sh to upgrade to multiuser schema"
    exit 1
fi

# Check foreign key relationship
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d flashcards" | grep -q "FOREIGN KEY"; then
    echo "✅ Foreign key relationship exists between users and flashcards"
else
    echo "⚠️  Warning: Foreign key relationship might be missing"
fi

# Test 9: Test basic operations
echo ""
echo "🧪 Test 9: Testing basic database operations..."
export PGPASSWORD=$DB_PASSWORD

# Test user creation
test_user_id=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
INSERT INTO users (id, name, created_at) 
VALUES (gen_random_uuid()::text, 'Test User', NOW()) 
RETURNING id;
" 2>/dev/null)

if [ ! -z "$test_user_id" ]; then
    echo "✅ Can create users"
    
    # Test flashcard creation for user
    test_card_id=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
    INSERT INTO flashcards (id, user_id, word, definition, bin_number, incorrect_count, next_review, created_at, is_hard_to_remember) 
    VALUES (gen_random_uuid()::text, '$test_user_id', 'test', 'test definition', 0, 0, NOW(), NOW(), false) 
    RETURNING id;
    " 2>/dev/null)
    
    if [ ! -z "$test_card_id" ]; then
        echo "✅ Can create flashcards for users"
        
        # Clean up test data
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM flashcards WHERE id = '$test_card_id'; DELETE FROM users WHERE id = '$test_user_id';" > /dev/null 2>&1
        echo "✅ Test data cleaned up"
    else
        echo "❌ Cannot create flashcards for users"
        # Clean up user if card creation failed
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM users WHERE id = '$test_user_id';" > /dev/null 2>&1
        exit 1
    fi
else
    echo "❌ Cannot create users"
    exit 1
fi

echo ""
echo "🎉 All database tests passed!"
echo "✅ Your database is properly configured for the multiuser flashcard app"
echo ""
echo "📊 Database Status:"
export PGPASSWORD=$DB_PASSWORD
user_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
card_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards;" 2>/dev/null || echo "0")
echo "👤 Users: $user_count"
echo "📚 Flashcards: $card_count"
echo ""
echo "📝 Your .env file should contain:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
