import { SPACED_REPETITION, CARD_STATUS_COLORS, UI_CONSTANTS } from '../constants';

/**
 * Format bin number to human-readable string
 * @param {number} binNumber - The bin number (0-11)
 * @param {boolean} fullName - Whether to return full name or short version
 * @returns {string} Formatted bin name
 */
export const formatBinNumber = (binNumber, fullName = false) => {
  const binNames = fullName ? SPACED_REPETITION.BIN_FULL_NAMES : SPACED_REPETITION.BIN_NAMES;
  return binNames[binNumber] || `Bin ${binNumber}`;
};

/**
 * Format next review date to human-readable string
 * @param {string|Date} dateString - ISO date string or Date object
 * @returns {string} Formatted date string
 */
export const formatNextReview = (dateString) => {
  if (!dateString) return 'Not scheduled';
  
  const date = new Date(dateString);
  const now = new Date();
  
  if (isNaN(date.getTime())) return 'Invalid date';
  if (date <= now) return 'Ready now';
  
  const diffTime = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'Tomorrow';
  if (diffDays < 7) return `In ${diffDays} days`;
  if (diffDays < 30) return `In ${Math.ceil(diffDays / 7)} weeks`;
  if (diffDays < 365) return `In ${Math.ceil(diffDays / 30)} months`;
  
  return `In ${Math.ceil(diffDays / 365)} years`;
};

/**
 * Get status color for a flashcard
 * @param {Object} card - Flashcard object
 * @returns {string} Color hex code
 */
export const getCardStatusColor = (card) => {
  if (!card) return CARD_STATUS_COLORS.SCHEDULED;
  
  if (card.is_hard_to_remember) return CARD_STATUS_COLORS.HARD;
  if (card.bin_number === 11) return CARD_STATUS_COLORS.COMPLETED;
  if (new Date(card.next_review) <= new Date()) return CARD_STATUS_COLORS.READY;
  
  return CARD_STATUS_COLORS.SCHEDULED;
};

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = UI_CONSTANTS.MAX_DEFINITION_PREVIEW) => {
  if (!text || text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, delay = UI_CONSTANTS.DEBOUNCE_DELAY) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Check if a card is ready for review
 * @param {Object} card - Flashcard object
 * @returns {boolean} Whether card is ready for review
 */
export const isCardReady = (card) => {
  if (!card || card.is_hard_to_remember || card.bin_number === 11) return false;
  return new Date(card.next_review) <= new Date();
};

/**
 * Validate flashcard input
 * @param {string} word - Word to validate
 * @param {string} definition - Definition to validate
 * @returns {Object} Validation result with isValid and errors
 */
export const validateFlashcard = (word, definition) => {
  const errors = [];
  
  if (!word || !word.trim()) {
    errors.push('Word is required');
  }
  
  if (!definition || !definition.trim()) {
    errors.push('Definition is required');
  }
  
  if (word && word.trim().length > 100) {
    errors.push('Word must be less than 100 characters');
  }
  
  if (definition && definition.trim().length > 1000) {
    errors.push('Definition must be less than 1000 characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Generate a random ID (for temporary use)
 * @returns {string} Random ID
 */
export const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Format error message from API response
 * @param {Error} error - Error object
 * @returns {string} Formatted error message
 */
export const formatErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

/**
 * Deep clone an object
 * @param {any} obj - Object to clone
 * @returns {any} Cloned object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
};
