import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { flashcardService } from '../services/api';

const ManageCards = ({ selectedUser, onUserChange, onViewChange }) => {
  const { t } = useTranslation();
  
  // State for cards and pagination
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage, setPerPage] = useState(20);
  const [totalCards, setTotalCards] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [includeHard, setIncludeHard] = useState(true);
  
  // Editing state
  const [editingCard, setEditingCard] = useState(null);
  const [editForm, setEditForm] = useState({ word: '', definition: '' });
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  
  // Search/Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCards, setFilteredCards] = useState([]);

  const loadCards = useCallback(async (page = currentPage, itemsPerPage = perPage, includeHardCards = includeHard) => {
    if (!selectedUser) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await flashcardService.getAllFlashcards(selectedUser.id, page, itemsPerPage, includeHardCards);
      const cardsArray = response.flashcards || response || [];
      
      setCards(cardsArray);
      setTotalCards(response.total || 0);
      setTotalPages(Math.ceil((response.total || 0) / itemsPerPage));
      setCurrentPage(page);
      setPerPage(itemsPerPage);
      setIncludeHard(includeHardCards);
    } catch (error) {
      console.error('Error loading cards:', error);
      setError(t('common.loadingError'));
      setCards([]);
      setTotalCards(0);
      setTotalPages(0);
    }
    
    setLoading(false);
  }, [currentPage, perPage, includeHard, selectedUser, t]);

  // Filter cards based on search term
  useEffect(() => {
    if (!searchTerm) {
      setFilteredCards(cards);
    } else {
      const filtered = cards.filter(card =>
        card.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
        card.definition.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredCards(filtered);
    }
  }, [cards, searchTerm]);

  useEffect(() => {
    if (selectedUser) {
      loadCards();
    }
  }, [loadCards, selectedUser]);

  // Pagination handlers
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      loadCards(newPage, perPage, includeHard);
    }
  };

  const handlePerPageChange = (newPerPage) => {
    const newTotalPages = Math.ceil(totalCards / newPerPage);
    const safePage = Math.min(currentPage, newTotalPages) || 1;
    loadCards(safePage, newPerPage, includeHard);
  };

  const handleIncludeHardChange = (newIncludeHard) => {
    loadCards(1, perPage, newIncludeHard); // Reset to page 1 when changing filter
  };

  const handleEditClick = (card) => {
    setEditingCard(card.id);
    setEditForm({ word: card.word, definition: card.definition });
  };

  const handleEditCancel = () => {
    setEditingCard(null);
    setEditForm({ word: '', definition: '' });
  };

  const handleEditSave = async (cardId) => {
    if (!editForm.word.trim() || !editForm.definition.trim()) {
      setError(t('manage.errors.validation'));
      return;
    }

    try {
      await flashcardService.updateFlashcard(cardId, editForm.word.trim(), editForm.definition.trim());
      setEditingCard(null);
      setEditForm({ word: '', definition: '' });
      await loadCards(); // Reload current page
    } catch (error) {
      console.error('Error updating card:', error);
      if (error.response?.status === 400) {
        setError(t('manage.errors.duplicate'));
      } else {
        setError(t('manage.errors.update'));
      }
    }
  };

  const handleDeleteClick = (card) => {
    setDeleteConfirm(card);
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm(null);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return;

    try {
      await flashcardService.deleteFlashcard(deleteConfirm.id);
      setDeleteConfirm(null);
      
      // If we're on the last item of a page (and not page 1), go to previous page
      if (cards.length === 1 && currentPage > 1) {
        await loadCards(currentPage - 1, perPage, includeHard);
      } else {
        await loadCards(); // Reload current page
      }
    } catch (error) {
      console.error('Error deleting card:', error);
      setError(t('manage.errors.delete'));
    }
  };

  const formatBinNumber = (binNumber) => {
    const binNames = {
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
      11: 'Never (Completed)'
    };
    return binNames[binNumber] || `Bin ${binNumber}`;
  };

  const formatNextReview = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    
    if (date <= now) {
      return 'Ready now';
    }
    
    const diffMs = date - now;
    const diffMins = Math.round(diffMs / 60000);
    const diffHours = Math.round(diffMs / 3600000);
    const diffDays = Math.round(diffMs / 86400000);
    
    if (diffMins < 60) {
      return `${diffMins} minutes`;
    } else if (diffHours < 24) {
      return `${diffHours} hours`;
    } else {
      return `${diffDays} days`;
    }
  };

  const getStatusColor = (card) => {
    if (card.is_hard_to_remember) return '#e74c3c';
    if (card.bin_number === 11) return '#2c3e50';
    if (new Date(card.next_review) <= new Date()) return '#27ae60';
    return '#3498db';
  };

  // Pagination component
  const PaginationControls = () => {
    const getPageNumbers = () => {
      const pages = [];
      const showPages = 5; // Number of page buttons to show
      let startPage = Math.max(1, currentPage - Math.floor(showPages / 2));
      let endPage = Math.min(totalPages, startPage + showPages - 1);
      
      // Adjust start page if we're near the end
      if (endPage - startPage + 1 < showPages) {
        startPage = Math.max(1, endPage - showPages + 1);
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      return pages;
    };

    if (totalPages <= 1) return null;

    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        gap: '8px',
        marginTop: '1rem',
        flexWrap: 'wrap'
      }}>
        <button 
          className="button button-info"
          onClick={() => handlePageChange(1)}
          disabled={currentPage === 1}
          style={{ padding: '8px 12px', fontSize: '14px' }}
        >
          « First
        </button>
        <button 
          className="button button-info"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          style={{ padding: '8px 12px', fontSize: '14px' }}
        >
          ‹ Prev
        </button>
        
        {getPageNumbers().map(pageNum => (
          <button
            key={pageNum}
            className={`button ${pageNum === currentPage ? 'button-primary' : 'button-info'}`}
            onClick={() => handlePageChange(pageNum)}
            style={{ 
              padding: '8px 12px', 
              fontSize: '14px',
              minWidth: '40px'
            }}
          >
            {pageNum}
          </button>
        ))}
        
        <button 
          className="button button-info"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          style={{ padding: '8px 12px', fontSize: '14px' }}
        >
          Next ›
        </button>
        <button 
          className="button button-info"
          onClick={() => handlePageChange(totalPages)}
          disabled={currentPage === totalPages}
          style={{ padding: '8px 12px', fontSize: '14px' }}
        >
          Last »
        </button>
      </div>
    );
  };

  // Early return if no user selected
  if (!selectedUser) {
    return (
      <div className="card">
        <p>{t('common.noUserSelected')}</p>
      </div>
    );
  }

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
          onClick={() => loadCards()}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      {/* Header with title and controls */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <h2>Manage Flashcards - {selectedUser?.name}</h2>
          <p style={{ margin: '0.5rem 0', color: '#666', fontSize: '14px' }}>
            Showing {cards.length} of {totalCards} flashcards
            {searchTerm && ` (filtered: ${filteredCards.length} results)`}
          </p>
        </div>
        
        <button 
          className="button button-info" 
          onClick={() => loadCards()}
          style={{ padding: '8px 16px' }}
        >
          Refresh
        </button>
      </div>

      {/* Controls bar */}
      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: '1rem', 
        marginBottom: '1rem',
        padding: '1rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '4px',
        alignItems: 'center'
      }}>
        {/* Search */}
        <div style={{ flex: '1', minWidth: '200px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: 'bold' }}>
            Search:
          </label>
          <input
            type="text"
            placeholder="Search by word or definition..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ 
              width: '100%', 
              padding: '8px', 
              borderRadius: '4px', 
              border: '1px solid #ddd' 
            }}
          />
        </div>
        
        {/* Items per page */}
        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: 'bold' }}>
            Items per page:
          </label>
          <select 
            value={perPage} 
            onChange={(e) => handlePerPageChange(Number(e.target.value))}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
        
        {/* Include hard cards */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={includeHard}
              onChange={(e) => handleIncludeHardChange(e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            Include hard cards
          </label>
        </div>
      </div>

      {/* Pagination info */}
      {totalPages > 1 && (
        <div style={{ 
          textAlign: 'center', 
          marginBottom: '1rem', 
          fontSize: '14px', 
          color: '#666' 
        }}>
          Page {currentPage} of {totalPages}
        </div>
      )}

      {filteredCards.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          {searchTerm ? (
            <>
              <h3>{t('manage.search.noResults')}</h3>
              <p>{t('manage.search.tryAdjusting')}</p>
              <div style={{ marginTop: '1rem' }}>
                <button 
                  className="button button-info"
                  onClick={() => setSearchTerm('')}
                >
                  {t('manage.search.clearSearch')}
                </button>
              </div>
            </>
          ) : totalCards === 0 ? (
            <>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
              <h3>{t('manage.emptyState.noCards')}</h3>
              <p style={{ marginBottom: '1.5rem', maxWidth: '400px', margin: '0 auto 1.5rem' }}>
                {t('manage.emptyState.noCardsMessage', { userName: selectedUser?.name })}
              </p>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button 
                  className="button button-primary"
                  onClick={() => onViewChange && onViewChange('create')}
                  style={{ padding: '12px 24px', fontSize: '16px' }}
                >
                  {t('manage.emptyState.createFirstCard')}
                </button>
                <button 
                  className="button button-info"
                  onClick={() => loadCards()}
                  style={{ padding: '12px 24px' }}
                >
                  {t('common.refresh')}
                </button>
              </div>
              <div style={{ 
                marginTop: '2rem', 
                padding: '1rem', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '8px',
                maxWidth: '500px',
                margin: '2rem auto 0'
              }}>
                <h4 style={{ marginBottom: '0.5rem' }}>{t('manage.emptyState.tipsTitle')}</h4>
                <ul style={{ textAlign: 'left', paddingLeft: '1.5rem' }}>
                  <li>{t('manage.emptyState.tip1')}</li>
                  <li>{t('manage.emptyState.tip2')}</li>
                  <li>{t('manage.emptyState.tip3')}</li>
                  <li>{t('manage.emptyState.tip4')}</li>
                </ul>
              </div>
            </>
          ) : (
            <>
              <h3>{t('manage.emptyState.noCardsFiltered')}</h3>
              <p>{t('manage.emptyState.cardsFilteredOut')}</p>
              <div style={{ marginTop: '1rem' }}>
                <button 
                  className="button button-info"
                  onClick={() => handleIncludeHardChange(true)}
                  style={{ marginRight: '0.5rem' }}
                >
                  {t('manage.emptyState.includeAllCards')}
                </button>
                <button 
                  className="button button-info"
                  onClick={() => loadCards()}
                >
                  Refresh
                </button>
              </div>
            </>
          )}
        </div>
      ) : (
        <>
          {/* Delete Confirmation Modal */}
          {deleteConfirm && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.5)',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              zIndex: 1000
            }}>
              <div style={{
                backgroundColor: 'white',
                padding: '2rem',
                borderRadius: '8px',
                maxWidth: '400px',
                width: '90%'
              }}>
                <h3>{t('manage.deleteModal.title')}</h3>
                <p>{t('manage.deleteModal.confirmation')}</p>
                <div style={{ marginBottom: '1rem' }}>
                  <strong>{t('manage.table.word')}:</strong> {deleteConfirm.word}<br />
                  <strong>{t('manage.table.definition')}:</strong> {deleteConfirm.definition.substring(0, 100)}
                  {deleteConfirm.definition.length > 100 && '...'}
                </div>
                <div>
                  <button 
                    className="button button-secondary" 
                    onClick={handleDeleteConfirm}
                    style={{ marginRight: '10px' }}
                  >
                    {t('common.delete')}
                  </button>
                  <button 
                    className="button button-info" 
                    onClick={handleDeleteCancel}
                  >
                    {t('common.cancel')}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Table */}
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>{t('manage.table.word')}</th>
                  <th>{t('manage.table.definition')}</th>
                  <th>{t('manage.table.status')}</th>
                  <th>{t('manage.table.nextReview')}</th>
                  <th>{t('manage.table.incorrect')}</th>
                  <th>{t('manage.table.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredCards.map((card) => (
                  <tr key={card.id}>
                    <td>
                      {editingCard === card.id ? (
                        <input
                          type="text"
                          value={editForm.word}
                          onChange={(e) => setEditForm({ ...editForm, word: e.target.value })}
                          style={{ width: '100%', padding: '5px' }}
                        />
                      ) : (
                        <strong>{card.word}</strong>
                      )}
                    </td>
                    <td style={{ maxWidth: '300px' }}>
                      {editingCard === card.id ? (
                        <textarea
                          value={editForm.definition}
                          onChange={(e) => setEditForm({ ...editForm, definition: e.target.value })}
                          style={{ width: '100%', minHeight: '60px', padding: '5px' }}
                        />
                      ) : (
                        <span>
                          {card.definition.length > 100 
                            ? `${card.definition.substring(0, 100)}...` 
                            : card.definition
                          }
                        </span>
                      )}
                    </td>
                    <td>
                      <span 
                        className={`bin-indicator bin-${card.bin_number}`}
                        style={{ backgroundColor: getStatusColor(card) }}
                      >
                        {card.is_hard_to_remember 
                          ? 'Hard to Remember' 
                          : formatBinNumber(card.bin_number)
                        }
                      </span>
                    </td>
                    <td>
                      {card.is_hard_to_remember 
                        ? 'Never' 
                        : card.bin_number === 11 
                          ? 'Never' 
                          : formatNextReview(card.next_review)
                      }
                    </td>
                    <td>
                      <span style={{ color: card.incorrect_count > 5 ? '#e74c3c' : '#555' }}>
                        {card.incorrect_count}
                        {card.incorrect_count >= 10 && ' (Max)'}
                      </span>
                    </td>
                    <td>
                      {editingCard === card.id ? (
                        <div>
                          <button 
                            className="button button-primary" 
                            onClick={() => handleEditSave(card.id)}
                            style={{ marginRight: '5px', padding: '5px 10px', fontSize: '12px' }}
                          >
                            {t('common.save')}
                          </button>
                          <button 
                            className="button button-info" 
                            onClick={handleEditCancel}
                            style={{ padding: '5px 10px', fontSize: '12px' }}
                          >
                            {t('common.cancel')}
                          </button>
                        </div>
                      ) : (
                        <div>
                          <button 
                            className="button button-info" 
                            onClick={() => handleEditClick(card)}
                            style={{ marginRight: '5px', padding: '5px 10px', fontSize: '12px' }}
                          >
                            {t('common.edit')}
                          </button>
                          <button 
                            className="button button-secondary" 
                            onClick={() => handleDeleteClick(card)}
                            style={{ padding: '5px 10px', fontSize: '12px' }}
                          >
                            {t('common.delete')}
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Pagination Controls */}
      <PaginationControls />

      {/* Footer with legend and info */}
      <div style={{ marginTop: '1.5rem', fontSize: '0.9rem', color: '#666' }}>
        <p><strong>{t('manage.legend.title')}:</strong></p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', marginBottom: '10px' }}>
          <span>{t('manage.legend.ready')}</span>
          <span>{t('manage.legend.scheduled')}</span>
          <span>{t('manage.legend.completed')}</span>
          <span>{t('manage.legend.hard')}</span>
        </div>
        <p><strong>{t('manage.legend.actionsTitle')}:</strong> {t('manage.legend.actionsDesc')}</p>
        
        {searchTerm && (
          <p style={{ marginTop: '10px', fontStyle: 'italic' }}>
            <strong>{t('manage.search.noteTitle')}:</strong> {t('manage.search.noteDesc')}
          </p>
        )}
      </div>
    </div>
  );
};

export default ManageCards;
