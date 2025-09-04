import React from 'react';
import { useTranslation } from 'react-i18next';
import { useStudy } from '../hooks';
import { Card, LoadingSpinner, StatusMessage, Button } from './ui';
import FlipCard from './FlipCard';

/**
 * StudyInterface component for flashcard study session
 */
const StudyInterface = ({ selectedUser, onUserChange }) => {
  const { t } = useTranslation();
  const {
    currentCard,
    showDefinition,
    isFlippingDown,
    loading,
    statusMessage,
    hasCards,
    loadNextCard,
    showCardDefinition,
    submitReview,
  } = useStudy(selectedUser);

  // Early return if no user selected
  if (!selectedUser) {
    return (
      <div className="study-container">
        <Card>
          <p>{t('study.selectUserFirst')}</p>
        </Card>
      </div>
    );
  }

  /**
   * Handle card click to show definition
   */
  const handleCardClick = () => {
    if (!showDefinition) {
      showCardDefinition();
    }
  };

  /**
   * Handle review submission
   */
  const handleReview = (correct) => {
    submitReview(correct);
  };

  // Loading state
  if (loading && !currentCard) {
    return (
      <div className="study-container">
        <Card>
          <LoadingSpinner />
          <p>{t('study.loading')}</p>
        </Card>
      </div>
    );
  }

  // Status message state (no cards available, etc.)
  if (statusMessage) {
    return (
      <div className="study-container">
        <Card>
          <StatusMessage 
            message={statusMessage} 
            type={hasCards ? 'info' : 'warning'} 
          />
          {hasCards && (
            <Button 
              variant="info" 
              onClick={loadNextCard}
              loading={loading}
            >
              {t('study.checkForCards')}
            </Button>
          )}
        </Card>
      </div>
    );
  }

  // No current card state
  if (!currentCard) {
    return (
      <div className="study-container">
        <Card>
          <p>{t('study.noCards')}</p>
          <Button 
            variant="info" 
            onClick={loadNextCard}
            loading={loading}
          >
            {t('study.refresh')}
          </Button>
        </Card>
      </div>
    );
  }

  // Main study interface with flip card
  return (
    <FlipCard
      card={currentCard}
      showDefinition={showDefinition}
      isFlippingDown={isFlippingDown}
      onCardClick={handleCardClick}
      onShowDefinition={showCardDefinition}
      onReview={handleReview}
      loading={loading}
    />
  );
};

export default StudyInterface;
