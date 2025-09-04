import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import StudyInterface from './components/StudyInterface';
import CreateCard from './components/CreateCard';
import ManageCards from './components/ManageCards';
import UserSelector from './components/UserSelector';
import { Button, LanguageSelector } from './components/ui';
import { VIEWS } from './constants';

/**
 * Main App component
 */
function App() {
  const [currentView, setCurrentView] = useState(VIEWS.STUDY);
  const [selectedUser, setSelectedUser] = useState(null);
  const { t } = useTranslation();

  /**
   * Handle card creation callback
   */
  const handleCardCreated = () => {
    // Optional: Switch to study view after creating a card
    // setCurrentView(VIEWS.STUDY);
  };

  /**
   * Handle user change - this will be called when users are added/deleted
   * to refresh any user-dependent data
   */
  const handleUserChange = () => {
    // This can be used to trigger refreshes in child components if needed
  };

  /**
   * Navigation button component
   */
  const NavButton = ({ view, children, disabled = false }) => (
    <Button
      variant={currentView === view ? 'primary' : 'info'}
      onClick={() => setCurrentView(view)}
      className={currentView === view ? 'active' : ''}
      disabled={disabled}
    >
      {children}
    </Button>
  );

  // Show user selector if no user is selected
  if (!selectedUser) {
    return (
      <div className="container">
        <div className="header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1>📚 {t('app.title')}</h1>
              <p>{t('app.subtitle')}</p>
            </div>
            <LanguageSelector />
          </div>
        </div>

        <UserSelector 
          selectedUser={selectedUser}
          onUserSelect={setSelectedUser}
          onUserChange={handleUserChange}
        />

        <footer style={{ textAlign: 'center', marginTop: '2rem', color: '#666' }}>
          <p>
            <strong>{t('users.welcome.title')}</strong> {t('users.welcome.subtitle')}
          </p>
        </footer>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>📚 {t('app.title')}</h1>
            <p>{t('app.subtitle')}</p>
          </div>
          <LanguageSelector />
        </div>
      </div>

      {/* User info and switch user option */}
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '1rem', 
        borderRadius: '8px', 
        marginBottom: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <strong>Current User:</strong> {selectedUser.name}
        </div>
        <button 
          className="button button-info"
          onClick={() => setSelectedUser(null)}
          style={{ padding: '8px 16px' }}
        >
          Switch User
        </button>
      </div>

      <nav className="nav">
        <NavButton view={VIEWS.STUDY}>{t('navigation.study')}</NavButton>
        <NavButton view={VIEWS.CREATE}>{t('navigation.create')}</NavButton>
        <NavButton view={VIEWS.MANAGE}>{t('navigation.manage')}</NavButton>
      </nav>

      <main>
        {currentView === VIEWS.STUDY && (
          <StudyInterface 
            selectedUser={selectedUser}
            onUserChange={handleUserChange}
          />
        )}
        {currentView === VIEWS.CREATE && (
          <CreateCard 
            selectedUser={selectedUser}
            onCardCreated={handleCardCreated}
            onUserChange={handleUserChange}
          />
        )}
        {currentView === VIEWS.MANAGE && (
          <ManageCards 
            selectedUser={selectedUser}
            onUserChange={handleUserChange}
            onViewChange={setCurrentView}
          />
        )}
      </main>

      <footer style={{ textAlign: 'center', marginTop: '2rem', color: '#666' }}>
        <p>
          <strong>How it works:</strong> Start with new words (bin 0). 
          Correct answers move cards to higher bins with longer intervals. 
          Wrong answers reset cards to bin 1. 
          Cards answered incorrectly 10+ times are hidden.
        </p>
      </footer>
    </div>
  );
}

export default App;
