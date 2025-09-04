import React from 'react';
import PropTypes from 'prop-types';

/**
 * Status Message component for displaying info, warning, and error messages
 */
const StatusMessage = ({
  message,
  type = 'info',
  className = '',
  style = {},
  onClose,
  ...props
}) => {
  if (!message) return null;

  const baseClass = 'status-message';
  const typeClass = `status-${type}`;
  
  const classes = [baseClass, typeClass, className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classes} style={style} {...props}>
      <span>{message}</span>
      {onClose && (
        <button 
          className="status-message-close" 
          onClick={onClose}
          aria-label="Close message"
        >
          ×
        </button>
      )}
    </div>
  );
};

StatusMessage.propTypes = {
  message: PropTypes.string,
  type: PropTypes.oneOf(['info', 'warning', 'error', 'success']),
  className: PropTypes.string,
  style: PropTypes.object,
  onClose: PropTypes.func,
};

export default StatusMessage;
