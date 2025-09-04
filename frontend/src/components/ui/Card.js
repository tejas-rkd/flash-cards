import React from 'react';
import PropTypes from 'prop-types';

/**
 * Reusable Card component
 */
const Card = ({
  children,
  className = '',
  style = {},
  padding = true,
  ...props
}) => {
  const baseClass = 'card';
  const paddingClass = padding ? '' : 'card-no-padding';
  
  const classes = [baseClass, paddingClass, className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classes} style={style} {...props}>
      {children}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  style: PropTypes.object,
  padding: PropTypes.bool,
};

export default Card;
