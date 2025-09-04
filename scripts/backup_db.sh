#!/bin/bash

# Database backup and restore script

echo "💾 Flashcard Database Backup & Restore Tool"
echo "==========================================="

# Database configuration
DB_NAME="flashcards"
DB_USER="flashcard_user"
DB_PASSWORD="flashcard_password"
DB_HOST="localhost"
DB_PORT="5432"

export PGPASSWORD=$DB_PASSWORD

# Create backups directory
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Function to create backup
create_backup() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="$BACKUP_DIR/flashcards_backup_$timestamp.sql"
    
    echo ""
    echo "💾 Creating backup..."
    echo "📁 Backup file: $backup_file"
    
    if pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > "$backup_file" 2>/dev/null; then
        echo "✅ Backup created successfully!"
        
        # Show backup info
        size=$(du -h "$backup_file" | cut -f1)
        echo "📊 Backup size: $size"
        
        # Count records in backup
        flashcard_count=$(grep -c "INSERT INTO flashcards" "$backup_file" 2>/dev/null || echo "0")
        user_count=$(grep -c "INSERT INTO users" "$backup_file" 2>/dev/null || echo "0")
        echo "👤 Users backed up: $user_count"
        echo "📚 Flashcards backed up: $flashcard_count"
        
        return 0
    else
        echo "❌ Backup failed!"
        rm -f "$backup_file" 2>/dev/null
        return 1
    fi
}

# Function to list backups
list_backups() {
    echo ""
    echo "📁 Available backups:"
    echo "===================="
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        echo "📭 No backups found in $BACKUP_DIR"
        return 1
    fi
    
    echo ""
    printf "%-3s %-25s %-10s %-20s\n" "No." "Filename" "Size" "Date"
    echo "------------------------------------------------------------"
    
    i=1
    for file in $BACKUP_DIR/flashcards_backup_*.sql; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(du -h "$file" | cut -f1)
            date=$(date -r "$file" "+%Y-%m-%d %H:%M:%S")
            printf "%-3s %-25s %-10s %-20s\n" "$i" "$filename" "$size" "$date"
            backup_files[$i]="$file"
            ((i++))
        fi
    done
    
    if [ $i -eq 1 ]; then
        echo "📭 No backup files found"
        return 1
    fi
    
    return 0
}

# Function to restore backup
restore_backup() {
    if ! list_backups; then
        return 1
    fi
    
    echo ""
    read -p "Enter backup number to restore (or 'cancel'): " choice
    
    if [[ $choice == "cancel" ]]; then
        echo "❌ Restore cancelled."
        return 1
    fi
    
    if [[ ! $choice =~ ^[0-9]+$ ]] || [ -z "${backup_files[$choice]}" ]; then
        echo "❌ Invalid backup number."
        return 1
    fi
    
    backup_file="${backup_files[$choice]}"
    echo ""
    echo "⚠️  WARNING: This will replace ALL current data with backup data!"
    echo "📁 Restoring from: $(basename "$backup_file")"
    echo ""
    read -p "Type 'RESTORE' to confirm: " confirm
    
    if [[ $confirm != "RESTORE" ]]; then
        echo "❌ Restore cancelled."
        return 1
    fi
    
    echo ""
    echo "🔄 Restoring backup..."
    
    # Clear current data first (order matters due to foreign keys)
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DELETE FROM flashcards; DELETE FROM users;" > /dev/null 2>&1; then
        echo "✅ Current data cleared"
    else
        echo "❌ Failed to clear current data"
        return 1
    fi
    
    # Restore from backup
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < "$backup_file" > /dev/null 2>&1; then
        echo "✅ Backup restored successfully!"
        
        # Show restore statistics
        user_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users;")
        flashcard_count=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM flashcards;")
        echo "� Restored users: $user_count"
        echo "📚 Restored flashcards: $flashcard_count"
        
        return 0
    else
        echo "❌ Restore failed!"
        return 1
    fi
}

# Function to delete old backups
cleanup_backups() {
    if ! list_backups; then
        return 1
    fi
    
    echo ""
    echo "🗑️  Backup Cleanup Options:"
    echo "1. Delete backups older than 7 days"
    echo "2. Keep only last 5 backups"
    echo "3. Delete all backups"
    echo "4. Cancel"
    echo ""
    read -p "Choose cleanup option (1-4): " choice
    
    case $choice in
        1)
            echo "🗑️  Deleting backups older than 7 days..."
            find $BACKUP_DIR -name "flashcards_backup_*.sql" -mtime +7 -delete
            echo "✅ Old backups deleted"
            ;;
        2)
            echo "🗑️  Keeping only last 5 backups..."
            ls -t $BACKUP_DIR/flashcards_backup_*.sql 2>/dev/null | tail -n +6 | xargs rm -f
            echo "✅ Old backups deleted, kept last 5"
            ;;
        3)
            echo ""
            read -p "Delete ALL backups? Type 'DELETE ALL' to confirm: " confirm
            if [[ $confirm == "DELETE ALL" ]]; then
                rm -f $BACKUP_DIR/flashcards_backup_*.sql
                echo "✅ All backups deleted"
            else
                echo "❌ Cleanup cancelled"
            fi
            ;;
        4)
            echo "❌ Cleanup cancelled"
            ;;
        *)
            echo "❌ Invalid option"
            ;;
    esac
}

# Main menu
declare -A backup_files

while true; do
    echo ""
    echo "💾 Backup & Restore Options:"
    echo "============================="
    echo "1. Create new backup"
    echo "2. List available backups"
    echo "3. Restore from backup"
    echo "4. Cleanup old backups"
    echo "5. Exit"
    echo ""
    read -p "Choose an option (1-5): " choice
    
    case $choice in
        1)
            create_backup
            ;;
        2)
            list_backups
            ;;
        3)
            restore_backup
            ;;
        4)
            cleanup_backups
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-5."
            ;;
    esac
done
