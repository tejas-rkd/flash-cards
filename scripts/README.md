# Database and Application Scripts

This folder contains various shell scripts for managing the flashcard application's database and running the application.

## Database Scripts

### Database Setup
- **`setup_db.sh`** - Initial database setup script
- **`setup_db_dev.sh`** - Development database setup with sample data
- **`setup_dev.sh`** - Complete development environment setup

### Database Management
- **`manage_db.sh`** - Interactive database management menu with options for:
  - View all tables and their data
  - Clear all data while preserving schema
  - Create database backup
  - Restore from backup
  - Run database tests

### Database Operations
- **`clear_db.sh`** - Clears all data from the database (preserves schema)
- **`backup_db.sh`** - Creates a timestamped backup of the database
- **`test_db.sh`** - Tests database connectivity and displays table information

## Application Scripts

### Application Startup
- **`start_app.sh`** - Starts the complete application (backend + frontend)
  - Starts FastAPI backend server on port 8000
  - Starts React frontend development server on port 3000
  - Runs both services concurrently

## Usage Instructions

### Prerequisites
- PostgreSQL installed and running
- Python 3.7+ with required packages installed
- Node.js and npm installed
- Database credentials configured

### Quick Start
1. **Initial Setup**: Run `./setup_dev.sh` to set up the complete development environment
2. **Start Application**: Run `./start_app.sh` to launch both backend and frontend
3. **Manage Database**: Run `./manage_db.sh` for interactive database management

### Script Permissions
Make sure all scripts have execute permissions:
```bash
chmod +x *.sh
```

### Database Connection
All database scripts use the following default connection parameters:
- Host: localhost
- Port: 5432
- Database: flashcards_db
- User: flashcard_user
- Password: flashcard_password

You can modify these parameters in the individual script files as needed.

## Script Dependencies

### Database Scripts
- PostgreSQL client tools (`psql`)
- Database credentials properly configured

### Application Scripts
- Python with FastAPI and required backend dependencies
- Node.js with React and required frontend dependencies

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure scripts have execute permissions (`chmod +x script.sh`)
2. **Database Connection Failed**: Check PostgreSQL service and credentials
3. **Port Already in Use**: Ensure ports 3000 and 8000 are available

### Database Issues
- If database connection fails, check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database exists: `psql -U flashcard_user -d flashcards_db -c "\dt"`
- Check user permissions with `manage_db.sh` option 1

## Script Descriptions

### Development Workflow
1. Use `setup_dev.sh` for initial project setup
2. Use `start_app.sh` to run the application during development
3. Use `manage_db.sh` for database maintenance and testing
4. Use `backup_db.sh` before making significant changes

### Production Considerations
- Modify database credentials for production environment
- Consider using environment variables for sensitive data
- Test scripts in staging environment before production use
