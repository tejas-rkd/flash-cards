import React from 'react';
import PropTypes from 'prop-types';

/**
 * Form Textarea component
 */
const Textarea = ({
  label,
  id,
  name,
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  rows = 4,
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

  const textareaId = id || name;
  const textareaClasses = ['form-textarea', error ? 'form-textarea-error' : '', className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="form-group" style={style}>
      {label && (
        <label htmlFor={textareaId} className="form-label">
          {label}
          {required && <span className="form-required">*</span>}
        </label>
      )}
      <textarea
        id={textareaId}
        name={name || textareaId}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        rows={rows}
        className={textareaClasses}
        {...props}
      />
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};

Textarea.propTypes = {
  label: PropTypes.string,
  id: PropTypes.string,
  name: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
  rows: PropTypes.number,
  error: PropTypes.string,
  className: PropTypes.string,
  style: PropTypes.object,
};

export default Textarea;
