# Flashcard Frontend

This is the React frontend for the flashcard application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will be available at `http://localhost:3000`

## Features

- **Study Interface**: Review flashcards with spaced repetition
- **Create Cards**: Add new vocabulary words with definitions
- **View All Cards**: See all cards and their current status

## How the Spaced Repetition Works

- Cards start in bin 0 (new)
- Correct answers move cards to higher bins (1-11) with increasing time intervals
- Wrong answers reset cards to bin 1
- Cards with 10+ incorrect answers are hidden as "hard to remember"
- Time intervals: 5s, 25s, 2min, 10min, 1hr, 5hr, 1day, 5days, 25days, 4months, never

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
