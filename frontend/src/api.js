import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const flashcardAPI = {
  // Create a new flashcard for a specific user
  createFlashcard: async (userId, word, definition) => {
    const response = await api.post('/api/v1/flashcards', { 
      user_id: userId,
      word, 
      definition 
    });
    return response.data;
  },

  // Get all flashcards for a specific user
  getAllFlashcards: async (userId, page = 1, perPage = 20, includeHard = true) => {
    const params = new URLSearchParams({
      user_id: userId,
      page: page.toString(),
      per_page: perPage.toString(),
      include_hard: includeHard.toString()
    });
    const response = await api.get(`/api/v1/flashcards?${params}`);
    return response.data;
  },

  // Get a specific flashcard by ID
  getFlashcard: async (cardId) => {
    const response = await api.get(`/api/v1/flashcards/${cardId}`);
    return response.data;
  },

  // Update an existing flashcard
  updateFlashcard: async (cardId, word, definition, userId = null) => {
    const updateData = { word, definition };
    if (userId) {
      updateData.user_id = userId;
    }
    const response = await api.put(`/api/v1/flashcards/${cardId}`, updateData);
    return response.data;
  },

  // Delete a flashcard
  deleteFlashcard: async (cardId) => {
    const response = await api.delete(`/api/v1/flashcards/${cardId}`);
    return response.data;
  },

  // Get next card for review for a specific user
  getNextCard: async (userId) => {
    const response = await api.get(`/api/v1/study/next?user_id=${userId}`);
    return response.data;
  },

  // Submit review for a card
  reviewCard: async (cardId, correct) => {
    const response = await api.post(`/api/v1/study/${cardId}/review`, { correct });
    return response.data;
  },

  // Get study status for a specific user
  getStudyStatus: async (userId) => {
    const response = await api.get(`/api/v1/study/status?user_id=${userId}`);
    return response.data;
  },
};

export default api;
