import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { userService } from '../services/api';

const UserSelector = ({ selectedUser, onUserSelect, onUserChange }) => {
  const { t } = useTranslation();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUserName, setNewUserName] = useState('');
  const [creatingUser, setCreatingUser] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await userService.getAllUsers();
      setUsers(response.users || []);
      
      // Don't auto-select any user - let the user choose
      // This allows the switch user functionality to work properly
    } catch (error) {
      console.error('Error loading users:', error);
      setError(t('users.errors.load'));
    }
    
    setLoading(false);
  }, [t]); // Add t dependency for useCallback

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleCreateUser = async () => {
    if (!newUserName.trim()) {
      setError(t('users.validation.nameRequired'));
      return;
    }

    // Check if user already exists
    if (users.some(user => user.name.toLowerCase() === newUserName.trim().toLowerCase())) {
      setError(t('users.validation.nameExists', { name: newUserName.trim() }));
      return;
    }

    // Check max users limit
    if (users.length >= 5) {
      setError(t('users.maxUsersReached'));
      return;
    }

    setCreatingUser(true);
    setError(''); // Clear any previous errors
    
    try {
      const newUser = await userService.createUser(newUserName.trim());
      await loadUsers(); // Reload users
      setNewUserName('');
      setShowAddUser(false);
      onUserSelect(newUser); // Select the newly created user
      onUserChange(); // Notify parent of user changes
    } catch (error) {
      console.error('Error creating user:', error);
      setError(error.message || t('users.errors.create'));
    }
    
    setCreatingUser(false);
  };

  const handleDeleteUser = async () => {
    if (!deleteConfirm) return;

    try {
      await userService.deleteUser(deleteConfirm.id);
      await loadUsers(); // Reload users
      
      // If the deleted user was selected, select another user or null
      if (selectedUser?.id === deleteConfirm.id) {
        const remainingUsers = users.filter(u => u.id !== deleteConfirm.id);
        onUserSelect(remainingUsers.length > 0 ? remainingUsers[0] : null);
      }
      
      setDeleteConfirm(null);
      onUserChange(); // Notify parent of user changes
    } catch (error) {
      console.error('Error deleting user:', error);
      setError(error.message || t('users.errors.delete'));
    }
  };

  if (loading) {
    return (
      <div className="card">
        <h2>👤 {t('users.selectUser')}</h2>
        <p>{t('common.loadingUsers')}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2>👤 {t('users.selectUser')}</h2>
        <div className="status-message status-warning">
          {error}
        </div>
        <button className="button button-info" onClick={loadUsers}>
          {t('common.retry')}
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>👤 {t('users.userManagement')}</h2>
      
      {users.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '1rem' }}>
          <h3>{t('users.welcome.title')}</h3>
          <p>{t('users.noUsers')}</p>
          <button 
            className="button button-primary" 
            onClick={() => setShowAddUser(true)}
          >
            {t('users.createFirstUser')}
          </button>
        </div>
      ) : (
        <>
          {/* User selection */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              {t('users.chooseUser')}
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {users.map((user) => (
                <button
                  key={user.id}
                  className={`button ${selectedUser?.id === user.id ? 'button-primary' : 'button-info'}`}
                  onClick={() => onUserSelect(user)}
                  style={{ position: 'relative' }}
                >
                  {user.name}
                  {users.length > 1 && (
                    <span 
                      style={{ 
                        marginLeft: '8px', 
                        color: '#e74c3c', 
                        fontWeight: 'bold',
                        cursor: 'pointer'
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteConfirm(user);
                      }}
                    >
                      ×
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Add new user button */}
          {users.length < 5 && (
            <div style={{ marginBottom: '1rem' }}>
              <button 
                className="button button-secondary" 
                onClick={() => setShowAddUser(true)}
              >
                + {t('users.addNewUser')}
              </button>
            </div>
          )}

          {users.length >= 5 && (
            <p style={{ color: '#666', fontSize: '14px', fontStyle: 'italic' }}>
              Maximum of 5 users reached. Delete a user to add a new one.
            </p>
          )}
        </>
      )}

      {/* Add user form */}
      {showAddUser && (
        <div style={{
          backgroundColor: '#f8f9fa',
          padding: '1rem',
          borderRadius: '4px',
          marginTop: '1rem'
        }}>
          <h3>{t('users.addNewUser')}</h3>
          {error && (
            <div className="status-message status-warning" style={{ marginBottom: '1rem' }}>
              {error}
            </div>
          )}
          <div style={{ marginBottom: '1rem' }}>
            <input
              type="text"
              placeholder={t('users.enterUserName')}
              value={newUserName}
              onChange={(e) => setNewUserName(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '8px', 
                borderRadius: '4px', 
                border: '1px solid #ddd',
                marginBottom: '0.5rem'
              }}
              onKeyPress={(e) => e.key === 'Enter' && handleCreateUser()}
              disabled={creatingUser}
            />
          </div>
          <div>
            <button 
              className="button button-primary" 
              onClick={handleCreateUser}
              disabled={creatingUser || !newUserName.trim()}
              style={{ marginRight: '0.5rem' }}
            >
              {creatingUser ? t('users.creating') : t('users.createUser')}
            </button>
            <button 
              className="button button-info" 
              onClick={() => {
                setShowAddUser(false);
                setNewUserName('');
                setError(''); // Clear error when canceling
              }}
              disabled={creatingUser}
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
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
            <h3>{t('users.confirmDelete')}</h3>
            <p>{t('users.confirmDeleteMessage', { name: deleteConfirm.name })}</p>
            <p style={{ color: '#e74c3c', fontWeight: 'bold' }}>
              {t('users.confirmDeleteWarning')}
            </p>
            <div>
              <button 
                className="button button-secondary" 
                onClick={handleDeleteUser}
                style={{ marginRight: '10px' }}
              >
                {t('users.deleteUser')}
              </button>
              <button 
                className="button button-info" 
                onClick={() => setDeleteConfirm(null)}
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Selected user info */}
      {selectedUser && (
        <div style={{ 
          marginTop: '1rem', 
          padding: '0.5rem', 
          backgroundColor: '#e8f5e8', 
          borderRadius: '4px' 
        }}>
          <p style={{ margin: 0, fontSize: '14px' }}>
            <strong>Selected:</strong> {selectedUser.name}
          </p>
        </div>
      )}
    </div>
  );
};

export default UserSelector;
