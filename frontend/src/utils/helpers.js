export const formatCurrency = (amount, currency = '€', addSpace = true) => {
  if (amount == null || isNaN(amount)) return '';
  return `${new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)}${addSpace ? ' ' : ''}${currency}`;
};

export const formatDate = (date, format = 'dd/MM/yyyy') => {
  if (!date) return '';
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  
  const options = {
    ...(format.includes('dd') && { day: '2-digit' }),
    ...(format.includes('MMMM') ? { month: 'long' } : format.includes('MM') && { month: '2-digit' }),
    ...(format.includes('yyyy') && { year: 'numeric' }),
    ...(format.includes('HH') && { hour: '2-digit', hour12: false }),
    ...(format.includes('hh') && { hour: '2-digit', hour12: true }),
    ...(format.includes('mm') && { minute: '2-digit' }),
    ...(format.includes('ss') && { second: '2-digit' })
  };
  
  return new Intl.DateTimeFormat('fr-FR', options).format(d);
};

export const truncateText = (text, maxLength = 50, suffix = '...') => {
  if (!text || typeof text !== 'string') return '';
  if (maxLength < 0) return text;
  return text.length <= maxLength ? text : `${text.slice(0, maxLength).trim()}${suffix}`;
};

export const generateUniqueId = (prefix = '') => {
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 10);
  return `${prefix}${timestamp}${randomStr}`;
};

export const getValueByPath = (object, path, defaultValue = undefined) => {
  if (!object || !path) return defaultValue;
  try {
    const value = path.split('.').reduce((obj, key) => 
      (obj && typeof obj === 'object' ? obj[key] : undefined), object);
    return value === undefined ? defaultValue : value;
  } catch {
    return defaultValue;
  }
};

export const objectToQueryString = (params) => {
  if (!params || typeof params !== 'object') return '';
  return Object.entries(params)
    .filter(([_, value]) => value != null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value).trim())}`)
    .join('&');
};

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, Math.max(0, parseInt(ms) || 0)));

export const isEmptyObject = (obj) => {
  if (!obj || typeof obj !== 'object') return false;
  return Object.keys(obj).length === 0 && obj.constructor === Object;
};

export const filterItems = (items, searchTerm, fields) => {
  if (!Array.isArray(items) || !searchTerm || !Array.isArray(fields) || !fields.length) return items;
  const normalizedTerm = String(searchTerm).toLowerCase().trim();
  if (!normalizedTerm) return items;
  return items.filter(item => 
    fields.some(field => {
      const value = getValueByPath(item, field);
      return value != null && String(value).toLowerCase().includes(normalizedTerm);
    })
  );
};

export const roundNumber = (value, decimals = 2) => {
  if (typeof value !== 'number' || isNaN(value)) return 0;
  const factor = Math.pow(10, Math.max(0, Math.floor(decimals)));
  return Math.round(value * factor) / factor;
};

export const isMacOS = () => typeof navigator !== 'undefined' && /Mac/i.test(navigator?.platform || '');

export const getOSName = () => {
  if (typeof navigator === 'undefined') return 'Unknown';
  const platform = navigator.platform || '';
  const userAgent = navigator.userAgent || '';
  
  if (/Mac/i.test(platform)) return 'MacOS';
  if (/Win/i.test(platform)) return 'Windows';
  if (/Linux/i.test(platform)) return 'Linux';
  if (/iPhone|iPad|iPod/i.test(userAgent)) return 'iOS';
  if (/Android/i.test(userAgent)) return 'Android';
  return 'Unknown';
};

export const capitalizeFirstLetter = (str) => {
  if (!str || typeof str !== 'string') return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};