#!/bin/bash

# Database migration script to add user support

echo "Migrating database for multiuser support..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL first."
    exit 1
fi

# Default database configuration
DB_NAME="flashcards"
DB_USER="flashcard_user"
DB_PASSWORD="flashcard_password"

echo "Adding users table and updating flashcards table..."

# Run migration SQL
sudo -u postgres psql -d $DB_NAME << 'EOF'
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT current_timestamp NOT NULL,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

-- Add user_id column to flashcards table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='flashcards' AND column_name='user_id') THEN
        ALTER TABLE flashcards ADD COLUMN user_id VARCHAR;
    END IF;
END $$;

-- Create a default user if none exist
INSERT INTO users (name) 
SELECT 'Default User' 
WHERE NOT EXISTS (SELECT 1 FROM users);

-- Update existing flashcards to belong to the default user
UPDATE flashcards 
SET user_id = (SELECT id FROM users WHERE name = 'Default User' LIMIT 1)
WHERE user_id IS NULL;

-- Make user_id NOT NULL after setting default values
ALTER TABLE flashcards ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'flashcards_user_id_fkey') THEN
        ALTER TABLE flashcards 
        ADD CONSTRAINT flashcards_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Remove unique constraint on word column since words can be duplicated across users
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
               WHERE constraint_name = 'flashcards_word_key') THEN
        ALTER TABLE flashcards DROP CONSTRAINT flashcards_word_key;
    END IF;
END $$;

-- Add index on user_id for performance
CREATE INDEX IF NOT EXISTS idx_flashcards_user_id ON flashcards(user_id);

-- Add composite unique constraint for word + user_id
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'flashcards_word_user_id_key') THEN
        ALTER TABLE flashcards 
        ADD CONSTRAINT flashcards_word_user_id_key 
        UNIQUE (word, user_id);
    END IF;
END $$;

-- Update the updated_at trigger for users table
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = current_timestamp;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully!"
    echo "- Added users table"
    echo "- Added user_id column to flashcards table"
    echo "- Created default user and assigned existing flashcards"
    echo "- Added foreign key constraint"
    echo "- Updated word uniqueness constraint to be per-user"
else
    echo "❌ Database migration failed. Please check your PostgreSQL setup."
fi
