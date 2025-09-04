import { useState, useCallback } from 'react';
import { validateFlashcard } from '../utils';
import { MESSAGES } from '../constants';

/**
 * Custom hook for form management
 * @param {Object} initialValues - Initial form values
 * @param {Function} onSubmit - Submit handler function
 * @returns {Object} Form state and operations
 */
export const useForm = (initialValues = {}, onSubmit) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  /**
   * Handle input value changes
   */
  const handleChange = useCallback((name, value) => {
    setValues(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  }, [errors]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(async (e) => {
    if (e) e.preventDefault();
    
    setIsSubmitting(true);
    setMessage('');
    setErrors({});
    
    try {
      // Validate if it's a flashcard form
      if (values.word !== undefined && values.definition !== undefined) {
        const validation = validateFlashcard(values.word, values.definition);
        if (!validation.isValid) {
          setErrors({ general: validation.errors.join(', ') });
          setMessage(MESSAGES.VALIDATION_REQUIRED_FIELDS);
          return;
        }
      }
      
      if (onSubmit) {
        await onSubmit(values);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setMessage(error.message || MESSAGES.ERROR_GENERIC);
    } finally {
      setIsSubmitting(false);
    }
  }, [values, onSubmit]);

  /**
   * Reset form to initial values
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setMessage('');
    setIsSubmitting(false);
  }, [initialValues]);

  /**
   * Set form values programmatically
   */
  const setFormValues = useCallback((newValues) => {
    setValues(prev => ({
      ...prev,
      ...newValues,
    }));
  }, []);

  /**
   * Set form message
   */
  const setFormMessage = useCallback((msg) => {
    setMessage(msg);
  }, []);

  return {
    values,
    errors,
    isSubmitting,
    message,
    handleChange,
    handleSubmit,
    resetForm,
    setFormValues,
    setFormMessage,
  };
};
