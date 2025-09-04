import React from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';
import { formatBinNumberI18n } from '../utils/i18n';

/**
 * FlipCard component for displaying flashcard with flip animation
 */
const FlipCard = ({
  card,
  showDefinition,
  isFlippingDown = false,
  onCardClick,
  onShowDefinition,
  onReview,
  loading = false,
}) => {
  const { t } = useTranslation();
  
  if (!card) return null;

  // Determine card class based on state
  const getCardClass = () => {
    if (isFlippingDown) return 'flip-card flipped flipping-down';
    if (showDefinition) return 'flip-card flipped';
    return 'flip-card';
  };

  return (
    <div className="study-container">
      <div 
        className={getCardClass()} 
        onClick={onCardClick}
      >
        <div className="flip-card-inner">
          {/* Front side - Word */}
          <div className="flip-card-front">
            <div className="word">{card.word}</div>
            
            <div style={{ marginBottom: '1rem' }}>
              <span className={`bin-indicator bin-${card.bin_number}`}>
                {formatBinNumberI18n(card.bin_number)}
              </span>
              {card.incorrect_count > 0 && (
                <span style={{ marginLeft: '10px', color: '#e74c3c' }}>
                  ❌ {card.incorrect_count}
                </span>
              )}
            </div>

            <div className="flip-instruction">{t('study.clickToReveal')}</div>
            
            <button 
              className="button button-info" 
              onClick={(e) => {
                e.stopPropagation();
                onShowDefinition();
              }}
              disabled={loading}
            >
              {t('study.showAnswer')}
            </button>
          </div>

          {/* Back side - Definition */}
          <div className="flip-card-back">
            <div className="word">{card.word}</div>
            
            <div style={{ marginBottom: '1rem' }}>
              <span className={`bin-indicator bin-${card.bin_number}`}>
                {formatBinNumberI18n(card.bin_number)}
              </span>
              {card.incorrect_count > 0 && (
                <span style={{ marginLeft: '10px', color: '#e74c3c' }}>
                  ❌ {card.incorrect_count}
                </span>
              )}
            </div>

            <div className="definition">{card.definition}</div>
            
            <div style={{ marginTop: '1rem' }}>
              <button 
                className="button button-primary" 
                onClick={(e) => {
                  e.stopPropagation();
                  onReview(true);
                }}
                disabled={loading}
              >
                {t('study.iGotIt')} ✓
              </button>
              <button 
                className="button button-secondary" 
                onClick={(e) => {
                  e.stopPropagation();
                  onReview(false);
                }}
                disabled={loading}
              >
                {t('study.iDidntGetIt')} ✗
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

FlipCard.propTypes = {
  card: PropTypes.shape({
    id: PropTypes.string.isRequired,
    word: PropTypes.string.isRequired,
    definition: PropTypes.string.isRequired,
    bin_number: PropTypes.number.isRequired,
    incorrect_count: PropTypes.number.isRequired,
  }),
  showDefinition: PropTypes.bool.isRequired,
  isFlippingDown: PropTypes.bool,
  onCardClick: PropTypes.func.isRequired,
  onShowDefinition: PropTypes.func.isRequired,
  onReview: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

FlipCard.propTypes = {
  card: PropTypes.shape({
    id: PropTypes.string.isRequired,
    word: PropTypes.string.isRequired,
    definition: PropTypes.string.isRequired,
    bin_number: PropTypes.number.isRequired,
    incorrect_count: PropTypes.number.isRequired,
  }),
  showDefinition: PropTypes.bool.isRequired,
  isFlippingDown: PropTypes.bool,
  onCardClick: PropTypes.func.isRequired,
  onShowDefinition: PropTypes.func.isRequired,
  onReview: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

export default FlipCard;
