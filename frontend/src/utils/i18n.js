import i18n from '../i18n';

/**
 * Format bin number to human-readable string using i18n
 * @param {number} binNumber - The bin number (0-11)
 * @param {boolean} fullName - Whether to return full name or short version
 * @returns {string} Formatted bin name
 */
export const formatBinNumberI18n = (binNumber, fullName = false) => {
  const prefix = fullName ? 'spaced_repetition.binsFull' : 'spaced_repetition.bins';
  return i18n.t(`${prefix}.${binNumber}`, { defaultValue: `Bin ${binNumber}` });
};

/**
 * Format time relative to now using i18n
 * @param {Date} date - The date to format
 * @returns {string} Formatted relative time
 */
export const formatRelativeTimeI18n = (date) => {
  if (!date) return i18n.t('time.never');
  
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) {
    return diffSeconds < 5 ? i18n.t('time.justNow') : i18n.t('time.secondsAgo', { count: diffSeconds });
  }
  
  if (diffMinutes < 60) {
    return i18n.t('time.minutesAgo', { count: diffMinutes });
  }
  
  if (diffHours < 24) {
    return i18n.t('time.hoursAgo', { count: diffHours });
  }
  
  return i18n.t('time.daysAgo', { count: diffDays });
};
