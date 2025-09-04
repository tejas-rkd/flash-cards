import React from 'react';
import PropTypes from 'prop-types';

/**
 * Form Input component
 */
const Input = ({
  label,
  id,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  error,
  className = '',
  style = {},
  ...props
}) => {
  const handleChange = (e) => {
    if (onChange) {
      onChange(name || id, e.target.value);
    }
  };

  const inputId = id || name;
  const inputClasses = ['form-input', error ? 'form-input-error' : '', className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="form-group" style={style}>
      {label && (
        <label htmlFor={inputId} className="form-label">
          {label}
          {required && <span className="form-required">*</span>}
        </label>
      )}
      <input
        id={inputId}
        name={name || inputId}
        type={type}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={inputClasses}
        {...props}
      />
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};

Input.propTypes = {
  label: PropTypes.string,
  id: PropTypes.string,
  name: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
  error: PropTypes.string,
  className: PropTypes.string,
  style: PropTypes.object,
};

export default Input;
