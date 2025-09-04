// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  TIMEOUT: 10000,
  HEADERS: {
    'Content-Type': 'application/json',
  },
};

// Spaced Repetition Configuration
export const SPACED_REPETITION = {
  BIN_NAMES: {
    0: 'New',
    1: '5s',
    2: '25s',
    3: '2m',
    4: '10m',
    5: '1h',
    6: '5h',
    7: '1d',
    8: '5d',
    9: '25d',
    10: '4mo',
    11: 'Done',
  },
  
  BIN_FULL_NAMES: {
    0: 'New',
    1: '5 seconds',
    2: '25 seconds',
    3: '2 minutes',
    4: '10 minutes',
    5: '1 hour',
    6: '5 hours',
    7: '1 day',
    8: '5 days',
    9: '25 days',
    10: '4 months',
    11: 'Done',
  },
  
  MAX_INCORRECT_COUNT: 10,
  HARD_TO_REMEMBER_THRESHOLD: 10,
};

// UI Constants
export const UI_CONSTANTS = {
  ANIMATION_DURATION: 600, // ms
  CARD_HEIGHT: 350, // px
  MAX_DEFINITION_PREVIEW: 100, // characters
  DEBOUNCE_DELAY: 300, // ms
};

// Navigation Views
export const VIEWS = {
  STUDY: 'study',
  CREATE: 'create',
  MANAGE: 'manage',
  VIEW: 'view',
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

// Messages
export const MESSAGES = {
  LOADING: 'Loading...',
  NO_CARDS: 'No cards available for review.',
  ERROR_GENERIC: 'An error occurred. Please try again.',
  ERROR_NETWORK: 'Network error. Please check your connection.',
  ERROR_CREATE_CARD: 'Error creating flashcard. Please try again.',
  ERROR_UPDATE_CARD: 'Error updating flashcard. Please try again.',
  ERROR_DELETE_CARD: 'Error deleting flashcard. Please try again.',
  SUCCESS_CREATE_CARD: 'Flashcard created successfully!',
  SUCCESS_UPDATE_CARD: 'Flashcard updated successfully!',
  SUCCESS_DELETE_CARD: 'Flashcard deleted successfully!',
  VALIDATION_REQUIRED_FIELDS: 'Please fill in both word and definition.',
  VALIDATION_WORD_EXISTS: 'Word already exists or invalid data provided.',
};

// Card Status Colors
export const CARD_STATUS_COLORS = {
  READY: '#27ae60',      // Green - ready for review
  SCHEDULED: '#3498db',  // Blue - scheduled for later
  COMPLETED: '#2c3e50',  // Dark - completed (never review)
  HARD: '#e74c3c',       // Red - hard to remember
};
