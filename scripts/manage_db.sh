#!/bin/bash

# Advanced database management script

echo "🛠️  Flashcard Database Management Tool"
echo "======================================="

# Database configuration
DB_NAME="flashcards"
DB_USER="flashcard_user"
DB_PASSWORD="flashcard_password"
DB_HOST="localhost"
DB_PORT="5432"

export PGPASSWORD=$DB_PASSWORD

# Function to show database stats
show_stats() {
    echo ""
    echo "📊 Database Statistics:"
    echo "======================="
    
    # Check if tables exist
    if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d users" > /dev/null 2>&1; then
        echo "❌ Users table does not exist"
        return 1
    fi
    
    if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d flashcards" > /dev/null 2>&1; then
        echo "❌ Flashcards table does not exist"
        return 1
    fi
    
    # Total users and flashcards
    total_users=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users;")
    total_flashcards=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards;")
    echo "👤 Total users: $total_users"
    echo "📚 Total flashcards: $total_flashcards"
    
    if [ "$total_users" -gt 0 ]; then
        echo ""
        echo "👥 User Overview:"
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
        SELECT 
            u.name as \"User Name\",
            COUNT(f.id) as \"Total Cards\",
            COUNT(CASE WHEN f.is_hard_to_remember = true THEN 1 END) as \"Hard Cards\",
            COUNT(CASE WHEN f.bin_number >= 1 AND f.next_review <= NOW() AND f.is_hard_to_remember = false THEN 1 END) as \"Ready for Review\"
        FROM users u
        LEFT JOIN flashcards f ON u.id = f.user_id
        GROUP BY u.id, u.name
        ORDER BY u.name;
        "
    fi
    
    if [ "$total_flashcards" -gt 0 ]; then
        # Overall cards by bin
        echo ""
        echo "📈 All cards by bin:"
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
        SELECT 
            bin_number as bin,
            COUNT(*) as count,
            CASE 
                WHEN bin_number = 0 THEN 'New'
                WHEN bin_number = 1 THEN '5s'
                WHEN bin_number = 2 THEN '25s'
                WHEN bin_number = 3 THEN '2m'
                WHEN bin_number = 4 THEN '10m'
                WHEN bin_number = 5 THEN '1h'
                WHEN bin_number = 6 THEN '5h'
                WHEN bin_number = 7 THEN '1d'
                WHEN bin_number = 8 THEN '5d'
                WHEN bin_number = 9 THEN '25d'
                WHEN bin_number = 10 THEN '4mo'
                WHEN bin_number = 11 THEN 'Done'
                ELSE 'Unknown'
            END as interval
        FROM flashcards 
        WHERE is_hard_to_remember = false
        GROUP BY bin_number 
        ORDER BY bin_number;
        "
        
        # Hard to remember cards
        hard_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards WHERE is_hard_to_remember = true;")
        echo ""
        echo "🚫 Total hard to remember: $hard_count cards"
        
        # Cards ready for review
        ready_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards WHERE bin_number >= 1 AND next_review <= NOW() AND is_hard_to_remember = false;")
        echo "⏰ Total ready for review: $ready_count cards"
    fi
}

# Function to clear all data
clear_all_data() {
    echo ""
    echo "⚠️  WARNING: This will delete ALL users and flashcard data!"
    echo "This action cannot be undone."
    echo ""
    read -p "Type 'DELETE' to confirm: " confirm
    
    if [[ $confirm != "DELETE" ]]; then
        echo "❌ Operation cancelled."
        return 1
    fi
    
    echo ""
    echo "🗑️  Clearing all data..."
    
    # Delete in correct order (flashcards first due to foreign key)
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM flashcards; DELETE FROM users;" > /dev/null 2>&1; then
        echo "✅ All data cleared successfully!"
    else
        echo "❌ Failed to clear data"
        return 1
    fi
}

# Function to reset progress (keep words, reset bins and counters)
reset_progress() {
    echo ""
    echo "🔄 This will reset all learning progress but keep your words and definitions."
    echo "All cards will be moved to bin 0 (new) and counters will be reset."
    echo ""
    read -p "Type 'RESET' to confirm: " confirm
    
    if [[ $confirm != "RESET" ]]; then
        echo "❌ Operation cancelled."
        return 1
    fi
    
    echo ""
    echo "🔄 Resetting progress..."
    
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
    UPDATE flashcards SET 
        bin_number = 0,
        incorrect_count = 0,
        next_review = NOW(),
        is_hard_to_remember = false;
    " > /dev/null 2>&1; then
        echo "✅ Progress reset successfully!"
        echo "📝 All cards moved to bin 0 (new)"
    else
        echo "❌ Failed to reset progress"
        return 1
    fi
}

# Function to remove hard to remember cards
clear_hard_cards() {
    hard_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards WHERE is_hard_to_remember = true;")
    
    if [ "$hard_count" -eq 0 ]; then
        echo "✅ No hard to remember cards found."
        return 0
    fi
    
    echo ""
    echo "🚫 Found $hard_count hard to remember cards."
    echo "These cards have been answered incorrectly 10+ times."
    echo ""
    read -p "Remove these cards? (yes/no): " confirm
    
    if [[ $confirm != "yes" ]]; then
        echo "❌ Operation cancelled."
        return 1
    fi
    
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM flashcards WHERE is_hard_to_remember = true;" > /dev/null 2>&1; then
        echo "✅ Removed $hard_count hard to remember cards"
    else
        echo "❌ Failed to remove hard to remember cards"
        return 1
    fi
}

# Function to add sample data
add_sample_data() {
    echo ""
    echo "📝 Adding sample user and flashcards for testing..."
    
    # First check if we need to create a sample user
    user_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users WHERE name = 'Sample User';")
    
    if [ "$user_count" -eq 0 ]; then
        echo "👤 Creating sample user..."
        sample_user_id=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
        INSERT INTO users (id, name, created_at) 
        VALUES (gen_random_uuid()::text, 'Sample User', NOW()) 
        RETURNING id;
        ")
        echo "✅ Sample user created with ID: $sample_user_id"
    else
        sample_user_id=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT id FROM users WHERE name = 'Sample User' LIMIT 1;")
        echo "👤 Using existing sample user with ID: $sample_user_id"
    fi
    
    # Add sample flashcards for this user
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
INSERT INTO flashcards (id, user_id, word, definition, bin_number, incorrect_count, next_review, created_at, is_hard_to_remember) VALUES
(gen_random_uuid()::text, '$sample_user_id', 'serendipity', 'The occurrence and development of events by chance in a happy or beneficial way', 0, 0, NOW(), NOW(), false),
(gen_random_uuid()::text, '$sample_user_id', 'ephemeral', 'Lasting for a very short time', 1, 0, NOW() - INTERVAL '1 hour', NOW(), false),
(gen_random_uuid()::text, '$sample_user_id', 'ubiquitous', 'Present, appearing, or found everywhere', 2, 1, NOW() + INTERVAL '30 minutes', NOW(), false),
(gen_random_uuid()::text, '$sample_user_id', 'perspicacious', 'Having a ready insight into and understanding of things', 3, 0, NOW() + INTERVAL '2 hours', NOW(), false),
(gen_random_uuid()::text, '$sample_user_id', 'recalcitrant', 'Having an obstinately uncooperative attitude', 0, 5, NOW(), NOW(), false);
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ Sample data added successfully!"
        echo "📚 Added 5 sample flashcards for 'Sample User' with various states"
    else
        echo "❌ Failed to add sample data"
    fi
}

# Function to manage users
manage_users() {
    while true; do
        echo ""
        echo "👥 User Management:"
        echo "=================="
        
        # List current users
        user_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users;")
        
        if [ "$user_count" -eq 0 ]; then
            echo "📭 No users found in database"
        else
            echo "Current users:"
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
            SELECT 
                u.name as \"User Name\",
                COUNT(f.id) as \"Flashcards\",
                u.created_at::date as \"Created\"
            FROM users u
            LEFT JOIN flashcards f ON u.id = f.user_id
            GROUP BY u.id, u.name, u.created_at
            ORDER BY u.created_at;
            "
        fi
        
        echo ""
        echo "User Management Options:"
        echo "1. Add new user"
        echo "2. Delete user (and all their cards)"
        echo "3. Back to main menu"
        echo ""
        read -p "Choose an option (1-3): " user_choice
        
        case $user_choice in
            1)
                if [ "$user_count" -ge 5 ]; then
                    echo "❌ Maximum of 5 users allowed"
                else
                    echo ""
                    read -p "Enter new user name: " new_user_name
                    
                    if [ -z "$new_user_name" ]; then
                        echo "❌ User name cannot be empty"
                    else
                        # Check if user already exists
                        existing=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users WHERE name = '$new_user_name';")
                        
                        if [ "$existing" -gt 0 ]; then
                            echo "❌ User '$new_user_name' already exists"
                        else
                            new_id=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
                            INSERT INTO users (id, name, created_at) 
                            VALUES (gen_random_uuid()::text, '$new_user_name', NOW()) 
                            RETURNING id;
                            ")
                            echo "✅ User '$new_user_name' created successfully!"
                        fi
                    fi
                fi
                ;;
            2)
                if [ "$user_count" -eq 0 ]; then
                    echo "❌ No users to delete"
                else
                    echo ""
                    echo "Available users:"
                    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT name FROM users ORDER BY created_at;"
                    echo ""
                    read -p "Enter user name to delete: " delete_user_name
                    
                    if [ -z "$delete_user_name" ]; then
                        echo "❌ User name cannot be empty"
                    else
                        # Check if user exists and get card count
                        user_info=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
                        SELECT u.id, COUNT(f.id) 
                        FROM users u 
                        LEFT JOIN flashcards f ON u.id = f.user_id 
                        WHERE u.name = '$delete_user_name' 
                        GROUP BY u.id;
                        ")
                        
                        if [ -z "$user_info" ]; then
                            echo "❌ User '$delete_user_name' not found"
                        else
                            card_count=$(echo "$user_info" | cut -d'|' -f2)
                            echo ""
                            echo "⚠️  WARNING: This will delete user '$delete_user_name' and all $card_count of their flashcards!"
                            read -p "Type 'DELETE' to confirm: " confirm
                            
                            if [[ $confirm == "DELETE" ]]; then
                                if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM users WHERE name = '$delete_user_name';" > /dev/null 2>&1; then
                                    echo "✅ User '$delete_user_name' and their $card_count flashcards deleted successfully!"
                                else
                                    echo "❌ Failed to delete user"
                                fi
                            else
                                echo "❌ Deletion cancelled"
                            fi
                        fi
                    fi
                fi
                ;;
            3)
                return 0
                ;;
            *)
                echo "❌ Invalid option. Please choose 1-3."
                ;;
        esac
    done
}

# Main menu
while true; do
    echo ""
    echo "🛠️  Database Management Options:"
    echo "================================"
    echo "1. Show database statistics"
    echo "2. Manage users (add/delete)"
    echo "3. Clear all data (DELETE EVERYTHING)"
    echo "4. Reset learning progress (keep words)"
    echo "5. Remove 'hard to remember' cards"
    echo "6. Add sample data for testing"
    echo "7. Exit"
    echo ""
    read -p "Choose an option (1-7): " choice
    
    case $choice in
        1)
            show_stats
            ;;
        2)
            manage_users
            ;;
        3)
            clear_all_data
            ;;
        4)
            reset_progress
            ;;
        5)
            clear_hard_cards
            ;;
        6)
            add_sample_data
            ;;
        7)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-7."
            ;;
    esac
done
