# Flashcard Backend

This is the FastAPI backend for the flashcard application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update the DATABASE_URL in `.env` file.

3. Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Endpoints

- `POST /flashcards` - Create a new flashcard
- `GET /flashcards` - Get all flashcards
- `GET /study/next` - Get next card for review
- `POST /study/{card_id}/review` - Submit review for a card
- `GET /study/status` - Get current study status
