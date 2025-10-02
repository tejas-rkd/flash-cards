# Flashcard Learning App
A full-stack flashcard application implementing spaced repetition learning with multiuser support, using React frontend, FastAPI backend, and PostgreSQL database.

## Deliverables

### ✅ Basic Requirements
- ✅ **Basic Functionality**: Complete spaced repetition flashcard system
- ✅ **Relational Database**: PostgreSQL with proper relationships and constraints
- ✅ **Data Persistence**: Robust data storage with backup and migration scripts

### ✅ Optional Enhancements
- ✅ **Better Looking UI**: Modern, responsive React interface with clean design
- ✅ **Full Flashcard CRUD Capabilities**: Complete admin interface for managing flashcards
- ✅ **Implementing Multiple Users**: Full multiuser support with isolated data per user
- ✅ **Documentation**: Comprehensive README, API docs, and code documentation
- ⚠️ **Automated Testing**: (In Progress) Complete test suite with 120+ tests and GitHub Actions
- ⚠️ **Automated Deployment/CI Work**: (In Progress) Partial implementation with GitHub Actions (in progress)

## Features

### Core Functionality
- **🤝 Multiuser Support**: Up to 5 users with individual flashcard collections
- **📚 User Management**: Create, switch between, and delete users
- **🧠 Spaced Repetition Algorithm**: 12-bin system with increasing time intervals
- **📈 Smart Review Logic**: Prioritizes cards ready for review per user
- **📊 Progress Tracking**: Monitors correct/incorrect answers for each user
- **🚫 Automatic Filtering**: Hides cards that are too difficult (10+ wrong answers)
- **🌍 Language Support**: Supports vocabulary learning in multiple languages with Unicode support

### User Interface
- **👤 User Selection**: Clean user switching and management interface
- **📝 Study Mode**: Focused flashcard review interface per user
- **⚙️ Admin Tools**: Create, edit, and delete user-specific flashcards
- **🎨 Modern UI**: Responsive design with visual bin indicators
- **⏱️ Real-time Status**: Shows review progress and completion messages
- **📄 Pagination**: Navigate through large flashcard collections efficiently
- **🔍 Search & Filter**: Find specific flashcards with search functionality
- **📊 Sorting Options**: Sort flashcards by various criteria (word, bin, date, difficulty)

### Multiuser Features
- **Maximum 5 Users**: Enforced limit to prevent overcrowding
- **User-Specific Data**: Each user has their own flashcards and progress
- **Isolated Learning**: Progress and cards are completely separate per user
- **Quick User Switch**: Easy switching between users without losing progress
- **Bulk Operations**: Delete user removes all their flashcards automatically

## Architecture

```
├── frontend/          # React application (port 3000)
├── backend/          # FastAPI application (port 8000)
├── database/         # PostgreSQL database
├── deployment/       # Deployment configurations and scripts
└── scripts/          # Database and management scripts
```

## Quick Start

### Prerequisites
- Node.js (16+)
- Python (3.8+)
- PostgreSQL

### Complete Setup (New Installation)
```bash
# Setup database and development environment
./scripts/setup_dev.sh      # Complete setup for new installations

# Start the application
./scripts/start_multiuser_app.sh
```

### Manual Setup

#### Database Setup
```bash
# For new databases
./scripts/setup_db.sh       # Create database with multiuser support

# For existing databases (migration)
./scripts/migrate_to_multiuser.sh  # Add multiuser support to existing DB
```

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Update DATABASE_URL in .env file
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Management Scripts
```bash
./scripts/test_multiuser_api.sh  # Test multiuser API endpoints
./scripts/clear_db.sh           # Clear all data (with confirmation)
./scripts/manage_db.sh          # Interactive database management
./scripts/backup_db.sh          # Backup and restore database
```

## Multiuser Workflow

### Initial Setup
1. **Landing Page**: Shows user selection interface
2. **Create Users**: Add users (up to 5 maximum)
3. **Select User**: Choose active user for session

### User Management
- **Add User**: Create new user (if under 5 limit)
- **Switch User**: Change active user anytime
- **Delete User**: Remove user and all their flashcards
- **User Validation**: Prevents duplicate names and enforces limits

### Per-User Features
- **Individual Progress**: Each user's learning progress is isolated
- **Personal Flashcards**: Cards belong to specific users
- **Separate Statistics**: Study status calculated per user
- **Independent Reviews**: Spaced repetition timing per user

## Spaced Repetition Logic (Per User)

### Bin System
- **Bin 0**: New cards (immediate review)
- **Bins 1-11**: Graduated cards with increasing intervals
  - Bin 1: 5 seconds
  - Bin 2: 25 seconds  
  - Bin 3: 2 minutes
  - Bin 4: 10 minutes
  - Bin 5: 1 hour
  - Bin 6: 5 hours
  - Bin 7: 1 day
  - Bin 8: 5 days
  - Bin 9: 25 days
  - Bin 10: 4 months
  - Bin 11: Never (completed)

### Review Priority (Per User)
1. Ready cards from bins 1-11 (higher bins first)
2. New cards from bin 0  
3. Status messages when no cards available

### Card Progression
- ✅ **Correct answer**: Move to next bin
- ❌ **Wrong answer**: Reset to bin 1, increment error count
- 🚫 **10+ errors**: Move to "hard to remember" (hidden)

## API Endpoints

### User Management
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/` - Get all users  
- `GET /api/v1/users/{id}` - Get specific user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user and all flashcards

### Flashcard Management (User-Specific)
- `POST /api/v1/flashcards/` - Create new flashcard for user
- `GET /api/v1/flashcards?user_id={id}` - Get user's flashcards
- `GET /api/v1/flashcards/{id}` - Get specific flashcard
- `PUT /api/v1/flashcards/{id}` - Update existing flashcard
- `DELETE /api/v1/flashcards/{id}` - Delete flashcard

### Study System (User-Specific)
- `GET /api/v1/study/next?user_id={id}` - Get next card for user
- `POST /api/v1/study/{card_id}/review` - Submit review result
- `GET /api/v1/study/status?user_id={id}` - Get user's study status

## Development

### Backend Development
```bash
cd backend
bash start_server.sh
```
API documentation available at `http://localhost:8000/docs`

### Frontend Development
```bash
cd frontend  
npm start
```
Application available at `http://localhost:3000`

### Complete Development Environment
```bash
# Start both frontend and backend
./scripts/start_multiuser_app.sh
```

## Database Schema

### Users Table
- `id` (VARCHAR, Primary Key)
- `name` (VARCHAR, Unique)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Flashcards Table  
- `id` (VARCHAR, Primary Key)
- `user_id` (VARCHAR, Foreign Key → users.id)
- `word` (VARCHAR)
- `definition` (TEXT)
- `bin_number` (INTEGER)
- `incorrect_count` (INTEGER)
- `next_review` (TIMESTAMP)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `is_hard_to_remember` (BOOLEAN)
- **Unique Constraint**: (word, user_id) - same word allowed for different users

## Migration from Single User

If you have an existing single-user installation:

1. **Backup your data**:
   ```bash
   ./scripts/backup_db.sh
   ```

2. **Run migration**:
   ```bash
   ./scripts/migrate_to_multiuser.sh
   ```

3. **Verify migration**:
   - Creates "Default User" 
   - Assigns existing flashcards to default user
   - Updates database schema for multiuser support

## Database Management

The project includes several useful database management scripts:

### 🧪 `scripts/test_multiuser_api.sh` - API Testing
Tests all multiuser API endpoints:
- User creation and management
- User-specific flashcard operations
- Study functionality per user

### 🗑️ `scripts/clear_db.sh` - Clear Database Contents
Simple script to delete all user and flashcard data with confirmation.

### 🛠️ `scripts/manage_db.sh` - Interactive Database Management
Comprehensive database management tool with multiuser support:
- View user statistics and card distribution per user
- Clear all data with confirmation
- Reset learning progress per user
- Remove "hard to remember" cards per user
- Add sample data for multiple users

### 💾 `scripts/backup_db.sh` - Backup and Restore
Full backup and restore functionality with multiuser data.

### 🔄 `scripts/migrate_to_multiuser.sh` - Migration Script
Migrates existing single-user installations to multiuser support.

## Technology Stack

### Frontend
- React 18 with Hooks
- Axios for API calls
- CSS3 with modern design
- Responsive multiuser interface

### Backend
- FastAPI (Python) with async support
- SQLAlchemy ORM with relationships
- Pydantic for data validation
- PostgreSQL with foreign keys

### Features
- CORS enabled for development
- Environment-based configuration
- Comprehensive error handling
- Real-time user switching
- Isolated user data

## License

MIT License

---

*This project has been developed with the assistance of Visual Studio Code and GitHub Copilot.*


