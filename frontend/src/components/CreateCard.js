import React from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';
import { useForm } from '../hooks';
import { Card, StatusMessage, Input, Textarea, Button } from './ui';
import { flashcardService } from '../services/api';

/**
 * CreateCard component for creating new flashcards
 */
const CreateCard = ({ selectedUser, onCardCreated, onUserChange }) => {
  const { t } = useTranslation();
  const {
    values,
    isSubmitting,
    message,
    handleChange,
    handleSubmit,
    resetForm,
    setFormMessage,
  } = useForm(
    { word: '', definition: '' },
    async (formValues) => {
      if (!selectedUser) {
        throw new Error('No user selected');
      }
      
      try {
        await flashcardService.createFlashcard(formValues.word, formValues.definition, selectedUser.id);
        setFormMessage(t('create.success'));
        resetForm();
        
        // Notify parent component if callback provided
        if (onCardCreated) {
          onCardCreated();
        }
        if (onUserChange) {
          onUserChange();
        }
      } catch (error) {
        console.error('Error creating flashcard:', error);
        throw error;
      }
    }
  );

  // Early return if no user selected
  if (!selectedUser) {
    return (
      <Card>
        <h2>{t('create.title')}</h2>
        <p>{t('create.selectUserFirst')}</p>
      </Card>
    );
  }

  const isMessageError = message?.includes('Error') || message?.includes('error');

  return (
    <Card>
      <h2>{t('create.title')} - {selectedUser.name}</h2>
      
      <StatusMessage 
        message={message} 
        type={isMessageError ? 'error' : 'success'} 
      />

      <form onSubmit={handleSubmit} className="form">
        <Input
          id="word"
          name="word"
          label={t('create.word')}
          value={values.word || ''}
          onChange={handleChange}
          placeholder={t('create.wordPlaceholder')}
          disabled={isSubmitting}
          required
        />

        <Textarea
          id="definition"
          name="definition"
          label={t('create.definition')}
          value={values.definition || ''}
          onChange={handleChange}
          placeholder={t('create.definitionPlaceholder')}
          disabled={isSubmitting}
          required
          rows={4}
        />

        <Button 
          type="submit" 
          variant="primary"
          loading={isSubmitting}
          disabled={isSubmitting}
        >
          {t('create.createButton')}
        </Button>
      </form>
    </Card>
  );
};

CreateCard.propTypes = {
  selectedUser: PropTypes.object,
  onCardCreated: PropTypes.func,
  onUserChange: PropTypes.func,
};

export default CreateCard;
