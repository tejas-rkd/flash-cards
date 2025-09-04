import React from 'react';
import PropTypes from 'prop-types';

/**
 * Loading Spinner component
 */
const LoadingSpinner = ({ 
  size = 'medium', 
  className = '',
  style = {} 
}) => {
  const sizeClass = `spinner-${size}`;
  const classes = ['spinner', sizeClass, className].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style}>
      <div className="spinner-circle"></div>
    </div>
  );
};

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  className: PropTypes.string,
  style: PropTypes.object,
};

export default LoadingSpinner;
