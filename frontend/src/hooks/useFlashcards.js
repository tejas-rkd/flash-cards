import { useState, useEffect, useCallback } from 'react';
import { flashcardService } from '../services/api';
import { MESSAGES } from '../constants';

/**
 * Custom hook for managing flashcards data
 * @returns {Object} Flashcards state and operations
 */
export const useFlashcards = () => {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Load all flashcards
   * @param {number} page - Page number (1-based)
   * @param {number} perPage - Items per page
   * @param {boolean} includeHard - Include hard to remember cards
   */
  const loadCards = useCallback(async (page = 1, perPage = 20, includeHard = true) => {
    setLoading(true);
    setError('');
    
    try {
      const cardsData = await flashcardService.getAllFlashcards(page, perPage, includeHard);
      // Handle paginated response format
      const cardsArray = cardsData.flashcards || cardsData || [];
      setCards(cardsArray);
      return cardsData; // Return full response for pagination info
    } catch (err) {
      console.error('Error loading cards:', err);
      setError(err.message || MESSAGES.ERROR_GENERIC);
      setCards([]);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Create a new flashcard
   */
  const createCard = useCallback(async (word, definition) => {
    try {
      const newCard = await flashcardService.createFlashcard(word, definition);
      setCards(prevCards => [...prevCards, newCard]);
      return newCard;
    } catch (err) {
      console.error('Error creating card:', err);
      throw err;
    }
  }, []);

  /**
   * Update an existing flashcard
   */
  const updateCard = useCallback(async (cardId, word, definition) => {
    try {
      const updatedCard = await flashcardService.updateFlashcard(cardId, word, definition);
      setCards(prevCards => 
        prevCards.map(card => 
          card.id === cardId ? updatedCard : card
        )
      );
      return updatedCard;
    } catch (err) {
      console.error('Error updating card:', err);
      throw err;
    }
  }, []);

  /**
   * Delete a flashcard
   */
  const deleteCard = useCallback(async (cardId) => {
    try {
      await flashcardService.deleteFlashcard(cardId);
      setCards(prevCards => prevCards.filter(card => card.id !== cardId));
    } catch (err) {
      console.error('Error deleting card:', err);
      throw err;
    }
  }, []);

  /**
   * Refresh cards data
   */
  const refreshCards = useCallback(() => {
    loadCards();
  }, [loadCards]);

  // Load cards on mount
  useEffect(() => {
    loadCards();
  }, [loadCards]);

  return {
    cards,
    loading,
    error,
    createCard,
    updateCard,
    deleteCard,
    refreshCards,
    loadCards,
  };
};
