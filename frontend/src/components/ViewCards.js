import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { flashcardAPI } from '../api';

const ViewCards = () => {
  const { t } = useTranslation();
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCards();
  }, []);

  const loadCards = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Load all cards without pagination limit for ViewCards
      const cardsData = await flashcardAPI.getAllFlashcards(1, 1000, true);
      // Handle paginated response format
      const cardsArray = cardsData.flashcards || cardsData || [];
      setCards(cardsArray);
    } catch (error) {
      console.error('Error loading cards:', error);
      setError(t('common.loadingError'));
    }
    
    setLoading(false);
  };

  const formatBinNumber = (binNumber) => {
    const binKeys = {
      0: 'view.bins.new',
      1: 'view.bins.5seconds', 
      2: 'view.bins.25seconds',
      3: 'view.bins.2minutes',
      4: 'view.bins.10minutes',
      5: 'view.bins.1hour',
      6: 'view.bins.5hours',
      7: 'view.bins.1day',
      8: 'view.bins.5days',
      9: 'view.bins.25days',
      10: 'view.bins.4months',
      11: 'view.bins.completed'
    };
    return t(binKeys[binNumber]) || t('view.bins.default', { binNumber });
  };

  const formatNextReview = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    
    if (date <= now) {
      return t('view.schedule.readyNow');
    }
    
    const diffMs = date - now;
    const diffMins = Math.round(diffMs / 60000);
    const diffHours = Math.round(diffMs / 3600000);
    const diffDays = Math.round(diffMs / 86400000);
    
    if (diffMins < 60) {
      return t('view.schedule.minutes', { count: diffMins });
    } else if (diffHours < 24) {
      return t('view.schedule.hours', { count: diffHours });
    } else {
      return t('view.schedule.days', { count: diffDays });
    }
  };

  const getStatusColor = (card) => {
    if (card.is_hard_to_remember) return '#e74c3c';
    if (card.bin_number === 11) return '#2c3e50';
    if (new Date(card.next_review) <= new Date()) return '#27ae60';
    return '#3498db';
  };

  if (loading) {
    return (
      <div className="card">
        <p>{t('common.loadingCards')}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="status-message status-warning">
          {error}
        </div>
        <button 
          className="button button-info" 
          onClick={loadCards}
        >
          {t('common.retry')}
        </button>
      </div>
    );
  }

  if (cards.length === 0) {
    return (
      <div className="card">
        <p>{t('view.emptyState.noCards')}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>{t('view.title', { count: cards.length })}</h2>
        <button 
          className="button button-info" 
          onClick={loadCards}
        >
          {t('common.refresh')}
        </button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>{t('view.table.word')}</th>
            <th>{t('view.table.definition')}</th>
            <th>{t('view.table.status')}</th>
            <th>{t('view.table.nextReview')}</th>
            <th>{t('view.table.incorrectCount')}</th>
          </tr>
        </thead>
        <tbody>
          {cards.map((card) => (
            <tr key={card.id}>
              <td>
                <strong>{card.word}</strong>
              </td>
              <td style={{ maxWidth: '300px' }}>
                {card.definition.length > 100 
                  ? `${card.definition.substring(0, 100)}...` 
                  : card.definition
                }
              </td>
              <td>
                <span 
                  className={`bin-indicator bin-${card.bin_number}`}
                  style={{ backgroundColor: getStatusColor(card) }}
                >
                  {card.is_hard_to_remember 
                    ? t('view.status.hardToRemember')
                    : formatBinNumber(card.bin_number)
                  }
                </span>
              </td>
              <td>
                {card.is_hard_to_remember 
                  ? t('view.schedule.never')
                  : card.bin_number === 11 
                    ? t('view.schedule.never')
                    : formatNextReview(card.next_review)
                }
              </td>
              <td>
                <span style={{ color: card.incorrect_count > 5 ? '#e74c3c' : '#555' }}>
                  {card.incorrect_count}
                  {card.incorrect_count >= 10 && ` (${t('view.table.max')})`}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
        <p><strong>{t('view.legend.title')}:</strong></p>
        <ul>
          <li>{t('view.legend.ready')}</li>
          <li>{t('view.legend.scheduled')}</li>
          <li>{t('view.legend.completed')}</li>
          <li>{t('view.legend.hard')}</li>
        </ul>
      </div>
    </div>
  );
};

export default ViewCards;
