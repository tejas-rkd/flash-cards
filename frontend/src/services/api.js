import axios from 'axios';
import { API_CONFIG, HTTP_STATUS, MESSAGES } from '../constants';
import { formatErrorMessage } from '../utils';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
});

// Request interceptor for logging and auth (if needed in future)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('🚨 API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('🚨 API Response Error:', error);
    
    // Handle network errors
    if (!error.response) {
      throw new Error(MESSAGES.ERROR_NETWORK);
    }
    
    // Special handling for study endpoints - let them handle their own 404s
    if (error.config?.url?.includes('/api/v1/study/next') && error.response.status === HTTP_STATUS.NOT_FOUND) {
      throw error; // Pass through the original error for study logic
    }
    
    // Handle specific status codes
    switch (error.response.status) {
      case HTTP_STATUS.BAD_REQUEST:
        throw new Error(formatErrorMessage(error));
      case HTTP_STATUS.NOT_FOUND:
        throw new Error('Requested resource not found');
      case HTTP_STATUS.INTERNAL_SERVER_ERROR:
        throw new Error('Server error. Please try again later.');
      default:
        throw new Error(formatErrorMessage(error));
    }
  }
);

/**
 * Flashcard API service
 */
export const flashcardService = {
  /**
   * Create a new flashcard
   * @param {string} word - The word to learn
   * @param {string} definition - The definition of the word
   * @param {string} userId - The user ID
   * @returns {Promise<Object>} Created flashcard
   */
  async createFlashcard(word, definition, userId) {
    try {
      const response = await apiClient.post('/api/v1/flashcards', { 
        word: word.trim(), 
        definition: definition.trim(),
        user_id: userId
      });
      return response.data;
    } catch (error) {
      throw new Error(MESSAGES.ERROR_CREATE_CARD);
    }
  },

  /**
   * Get all flashcards for a user
   * @param {string} userId - The user ID
   * @param {number} page - Page number (1-based)
   * @param {number} perPage - Items per page
   * @param {boolean} includeHard - Include hard to remember cards
   * @returns {Promise<Object>} Paginated flashcards response
   */
  async getAllFlashcards(userId, page = 1, perPage = 20, includeHard = true) {
    try {
      const params = new URLSearchParams({
        user_id: userId,
        page: page.toString(),
        per_page: perPage.toString(),
        include_hard: includeHard.toString()
      });
      const response = await apiClient.get(`/api/v1/flashcards?${params}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get a specific flashcard by ID
   * @param {string} cardId - The flashcard ID
   * @returns {Promise<Object>} Flashcard data
   */
  async getFlashcard(cardId) {
    try {
      const response = await apiClient.get(`/api/v1/flashcards/${cardId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update an existing flashcard
   * @param {string} cardId - The flashcard ID
   * @param {string} word - Updated word
   * @param {string} definition - Updated definition
   * @returns {Promise<Object>} Updated flashcard
   */
  async updateFlashcard(cardId, word, definition) {
    try {
      const response = await apiClient.put(`/api/v1/flashcards/${cardId}`, { 
        word: word.trim(), 
        definition: definition.trim() 
      });
      return response.data;
    } catch (error) {
      throw new Error(MESSAGES.ERROR_UPDATE_CARD);
    }
  },

  /**
   * Delete a flashcard
   * @param {string} cardId - The flashcard ID
   * @returns {Promise<void>}
   */
  async deleteFlashcard(cardId) {
    try {
      await apiClient.delete(`/api/v1/flashcards/${cardId}`);
    } catch (error) {
      throw new Error(MESSAGES.ERROR_DELETE_CARD);
    }
  },
};

/**
 * Study API service
 */
export const studyService = {
  /**
   * Get next card for review for a user
   * @param {string} userId - The user ID
   * @returns {Promise<Object>} Next flashcard for study
   */
  async getNextCard(userId) {
    try {
      const response = await apiClient.get(`/api/v1/study/next?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Submit review for a card
   * @param {string} cardId - The flashcard ID
   * @param {boolean} correct - Whether the answer was correct
   * @returns {Promise<Object>} Review result
   */
  async reviewCard(cardId, correct) {
    try {
      const response = await apiClient.post(`/api/v1/study/${cardId}/review`, { correct });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get study status for a user
   * @param {string} userId - The user ID
   * @returns {Promise<Object>} Study status information
   */
  async getStudyStatus(userId) {
    try {
      const response = await apiClient.get(`/api/v1/study/status?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

/**
 * User API service
 */
export const userService = {
  /**
   * Create a new user
   * @param {string} name - The user's name
   * @returns {Promise<Object>} Created user
   */
  async createUser(name) {
    try {
      const response = await apiClient.post('/api/v1/users', { 
        name: name.trim()
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to create user. Please try again.');
    }
  },

  /**
   * Get all users
   * @returns {Promise<Object>} List of all users
   */
  async getAllUsers() {
    try {
      const response = await apiClient.get('/api/v1/users');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get a specific user by ID
   * @param {string} userId - The user ID
   * @returns {Promise<Object>} User data
   */
  async getUser(userId) {
    try {
      const response = await apiClient.get(`/api/v1/users/${userId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update an existing user
   * @param {string} userId - The user ID
   * @param {string} name - Updated name
   * @returns {Promise<Object>} Updated user
   */
  async updateUser(userId, name) {
    try {
      const response = await apiClient.put(`/api/v1/users/${userId}`, { 
        name: name.trim()
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to update user. Please try again.');
    }
  },

  /**
   * Delete a user
   * @param {string} userId - The user ID
   * @returns {Promise<void>}
   */
  async deleteUser(userId) {
    try {
      await apiClient.delete(`/api/v1/users/${userId}`);
    } catch (error) {
      throw new Error('Failed to delete user. Please try again.');
    }
  },
};

/**
 * Combined API service (for backward compatibility)
 */
export const flashcardAPI = {
  ...flashcardService,
  ...studyService,
  ...userService,
};

export default apiClient;
