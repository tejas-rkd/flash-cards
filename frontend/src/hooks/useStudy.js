import { useState, useEffect, useCallback } from 'react';
import { studyService } from '../services/api';
import { MESSAGES, UI_CONSTANTS } from '../constants';

/**
 * Custom hook for managing study session
 * @param {Object} selectedUser - The currently selected user
 * @returns {Object} Study state and operations
 */
export const useStudy = (selectedUser) => {
  const [currentCard, setCurrentCard] = useState(null);
  const [showDefinition, setShowDefinition] = useState(false);
  const [isFlippingDown, setIsFlippingDown] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [hasCards, setHasCards] = useState(true);

  /**
   * Load the next card for review
   */
  const loadNextCard = useCallback(async () => {
    if (!selectedUser) {
      setStatusMessage('Please select a user first.');
      setCurrentCard(null);
      return;
    }
    
    setLoading(true);
    setShowDefinition(false); // Reset flip state
    setIsFlippingDown(false); // Reset flip down state
    setStatusMessage('');
    
    try {
      const card = await studyService.getNextCard(selectedUser.id);
      setCurrentCard(card);
    } catch (error) {
      if (error.message?.includes('404') || error.response?.status === 404) {
        // No cards available, check status
        try {
          const status = await studyService.getStudyStatus(selectedUser.id);
          setStatusMessage(status.message);
          setHasCards(status.has_cards);
          setCurrentCard(null);
        } catch (statusError) {
          console.error('Error getting study status:', statusError);
          setStatusMessage(MESSAGES.ERROR_GENERIC);
        }
      } else {
        console.error('Error loading next card:', error);
        setStatusMessage(error.message || MESSAGES.ERROR_GENERIC);
      }
    } finally {
      setLoading(false);
    }
  }, [selectedUser]);

  /**
   * Show the definition of the current card
   */
  const showCardDefinition = useCallback(() => {
    setShowDefinition(true);
  }, []);

  /**
   * Submit a review for the current card with flip-down animation
   */
  const submitReview = useCallback(async (correct) => {
    if (!currentCard || isFlippingDown) return;
    
    setLoading(true);
    
    try {
      // Start flip-down animation
      setIsFlippingDown(true);
      
      // Submit the review
      await studyService.reviewCard(currentCard.id, correct);
      
      // Wait for flip-down animation to complete (0.6s) plus a small buffer
      await new Promise(resolve => setTimeout(resolve, UI_CONSTANTS.ANIMATION_DURATION + 100));
      
      // Load next card after animation completes
      await loadNextCard();
    } catch (error) {
      console.error('Error submitting review:', error);
      setStatusMessage(error.message || 'Error submitting review. Please try again.');
      setIsFlippingDown(false); // Reset on error
    } finally {
      setLoading(false);
    }
  }, [currentCard, isFlippingDown, loadNextCard]);

  /**
   * Reset the study session
   */
  const resetSession = useCallback(() => {
    setCurrentCard(null);
    setShowDefinition(false);
    setIsFlippingDown(false);
    setStatusMessage('');
    setHasCards(true);
  }, []);

  // Load first card when user changes or on mount
  useEffect(() => {
    if (selectedUser) {
      loadNextCard();
    } else {
      setCurrentCard(null);
      setStatusMessage('Please select a user first.');
    }
  }, [loadNextCard, selectedUser]);

  return {
    currentCard,
    showDefinition,
    isFlippingDown,
    loading,
    statusMessage,
    hasCards,
    loadNextCard,
    showCardDefinition,
    submitReview,
    resetSession,
  };
};
