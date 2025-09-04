#!/bin/bash

# Database setup script

echo "Setting up PostgreSQL database for Flashcard App..."

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

echo "Creating database and user..."

# Create user and database
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

# Grant schema permissions
sudo -u postgres psql -d $DB_NAME << EOF
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- Create initial tables for multiuser support
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT current_timestamp NOT NULL,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS flashcards (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word VARCHAR(255) NOT NULL,
    definition TEXT NOT NULL,
    bin_number INTEGER DEFAULT 0 NOT NULL,
    incorrect_count INTEGER DEFAULT 0 NOT NULL,
    next_review TIMESTAMP DEFAULT current_timestamp NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp NOT NULL,
    updated_at TIMESTAMP DEFAULT current_timestamp,
    is_hard_to_remember BOOLEAN DEFAULT FALSE NOT NULL,
    UNIQUE(word, user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_flashcards_user_id ON flashcards(user_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_bin_number ON flashcards(bin_number);
CREATE INDEX IF NOT EXISTS idx_flashcards_next_review ON flashcards(next_review);
CREATE INDEX IF NOT EXISTS idx_flashcards_is_hard_to_remember ON flashcards(is_hard_to_remember);

-- Create trigger function for updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = current_timestamp;
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS update_flashcards_updated_at ON flashcards;
CREATE TRIGGER update_flashcards_updated_at
    BEFORE UPDATE ON flashcards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

\q
EOF

if [ $? -eq 0 ]; then
    echo "Database setup completed successfully!"
    echo "Database: $DB_NAME"
    echo "User: $DB_USER"
    echo "Password: $DB_PASSWORD"
    echo ""
    echo "✅ Multiuser support enabled with users and flashcards tables created"
    echo ""
    echo "Update your backend/.env file with:"
    echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
else
    echo "Database setup failed. Please check your PostgreSQL installation."
fi
