#!/bin/bash

# Alternative database setup script with superuser privileges (for development)

echo "Setting up PostgreSQL database for Flashcard App (Development Mode)..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL first."
    echo "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "MacOS: brew install postgresql"
    exit 1
fi

# Default database configuration
DB_NAME="flashcards"
DB_USER="flashcard_user"
DB_PASSWORD="flashcard_password"

echo "Creating database and superuser..."

# Create superuser and database (for development convenience)
sudo -u postgres psql << EOF
-- Drop existing user and database if they exist
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Create new superuser and database
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' SUPERUSER CREATEDB;
CREATE DATABASE $DB_NAME OWNER $DB_USER;
\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully!"
    echo "Database: $DB_NAME"
    echo "User: $DB_USER (SUPERUSER)"
    echo "Password: $DB_PASSWORD"
    echo ""
    echo "📝 Update your backend/.env file with:"
    echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
    echo ""
    echo "🧪 Testing database connection..."
    
    # Test the connection
    if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
        echo "✅ Database connection test successful!"
    else
        echo "⚠️  Database connection test failed. Please check the setup."
    fi
else
    echo "❌ Database setup failed. Please check your PostgreSQL installation."
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "1. Make sure PostgreSQL is running: sudo systemctl start postgresql"
    echo "2. Check if you can connect as postgres user: sudo -u postgres psql"
    echo "3. Ensure PostgreSQL is properly installed and initialized"
fi
