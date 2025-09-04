import React from 'react';
import { useTranslation } from 'react-i18next';
import PropTypes from 'prop-types';

/**
 * Language Selector component for switching between languages
 */
const LanguageSelector = ({ className = '', style = {} }) => {
  const { t, i18n } = useTranslation();

  const languages = [
    { code: 'en', name: t('language.english'), flag: '🇺🇸' },
    { code: 'es', name: t('language.spanish'), flag: '🇪🇸' },
    { code: 'fr', name: t('language.french'), flag: '🇫🇷' },
    { code: 'de', name: t('language.german'), flag: '🇩🇪' },
    { code: 'zh', name: t('language.chinese'), flag: '🇨🇳' },
    { code: 'ja', name: t('language.japanese'), flag: '🇯🇵' },
  ];

  const handleLanguageChange = (event) => {
    const selectedLanguage = event.target.value;
    i18n.changeLanguage(selectedLanguage);
  };

  return (
    <div className={`language-selector ${className}`} style={style}>
      <label htmlFor="language-select" className="language-label">
        {t('language.title')}:
      </label>
      <select
        id="language-select"
        value={i18n.language}
        onChange={handleLanguageChange}
        className="language-dropdown"
        aria-label={t('language.select')}
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};

LanguageSelector.propTypes = {
  className: PropTypes.string,
  style: PropTypes.object,
};

export default LanguageSelector;
