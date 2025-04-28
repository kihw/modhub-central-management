/**
 * Collection de fonctions utilitaires pour l'application.
 * Ces helpers sont conçus pour être réutilisables à travers l'application.
 */

/**
 * Formate un montant en devise avec le symbole € et séparateurs.
 * @param {number} amount - Montant à formater
 * @param {string} [currency='€'] - Symbole de la devise
 * @param {boolean} [addSpace=true] - Ajoute un espace entre le montant et la devise
 * @returns {string} Montant formaté
 */
export const formatCurrency = (amount, currency = '€', addSpace = true) => {
  if (amount === null || amount === undefined) return '';
  
  const formatter = new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  return `${formatter.format(amount)}${addSpace ? ' ' : ''}${currency}`;
};

/**
 * Formate une date en chaîne de caractères selon le format spécifié.
 * @param {Date|string} date - Date à formater
 * @param {string} [format='dd/MM/yyyy'] - Format de date souhaité
 * @returns {string} Date formatée
 */
export const formatDate = (date, format = 'dd/MM/yyyy') => {
  if (!date) return '';
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  
  const options = {};
  
  if (format.includes('dd')) {
    options.day = '2-digit';
  }
  
  if (format.includes('MM')) {
    options.month = '2-digit';
  } else if (format.includes('MMMM')) {
    options.month = 'long';
  }
  
  if (format.includes('yyyy')) {
    options.year = 'numeric';
  }
  
  if (format.includes('HH') || format.includes('hh')) {
    options.hour = '2-digit';
  }
  
  if (format.includes('mm')) {
    options.minute = '2-digit';
  }
  
  if (format.includes('ss')) {
    options.second = '2-digit';
  }
  
  return new Intl.DateTimeFormat('fr-FR', options).format(d);
};

/**
 * Tronque un texte à une longueur maximale et ajoute des points de suspension.
 * @param {string} text - Texte à tronquer
 * @param {number} [maxLength=50] - Longueur maximale avant troncature
 * @param {string} [suffix='...'] - Suffixe à ajouter après la troncature
 * @returns {string} Texte tronqué
 */
export const truncateText = (text, maxLength = 50, suffix = '...') => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength).trim() + suffix;
};

/**
 * Génère un identifiant unique.
 * @returns {string} Identifiant unique
 */
export const generateUniqueId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
};

/**
 * Retourne la valeur d'un objet depuis un chemin sous forme de chaîne (ex: "user.address.city").
 * @param {Object} object - Objet source
 * @param {string} path - Chemin d'accès à la propriété
 * @param {*} [defaultValue=undefined] - Valeur par défaut si le chemin n'existe pas
 * @returns {*} Valeur de la propriété ou valeur par défaut
 */
export const getValueByPath = (object, path, defaultValue = undefined) => {
  if (!object || !path) return defaultValue;
  
  const keys = path.split('.');
  let result = object;
  
  for (const key of keys) {
    if (result === null || result === undefined || typeof result !== 'object') {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result === undefined ? defaultValue : result;
};

/**
 * Transforme un objet en paramètres d'URL.
 * @param {Object} params - Objet contenant les paramètres
 * @returns {string} Chaîne de paramètres d'URL formatée
 */
export const objectToQueryString = (params) => {
  if (!params || typeof params !== 'object') return '';
  
  return Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
};

/**
 * Attend pendant un temps spécifié.
 * @param {number} ms - Délai en millisecondes
 * @returns {Promise<void>} Promise qui se résout après le délai
 */
export const sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Vérifie si un objet est vide.
 * @param {Object} obj - Objet à vérifier
 * @returns {boolean} True si l'objet est vide
 */
export const isEmptyObject = (obj) => {
  return obj && Object.keys(obj).length === 0 && obj.constructor === Object;
};

/**
 * Filtre un tableau d'objets selon des critères de recherche.
 * @param {Array} items - Tableau d'objets à filtrer
 * @param {string} searchTerm - Terme de recherche
 * @param {Array<string>} fields - Champs dans lesquels rechercher
 * @returns {Array} Tableau filtré
 */
export const filterItems = (items, searchTerm, fields) => {
  if (!items || !Array.isArray(items) || !searchTerm || !fields || !Array.isArray(fields)) {
    return items;
  }
  
  const normalizedTerm = searchTerm.toLowerCase().trim();
  
  return items.filter(item => 
    fields.some(field => {
      const value = getValueByPath(item, field);
      if (value === null || value === undefined) return false;
      return String(value).toLowerCase().includes(normalizedTerm);
    })
  );
};

/**
 * Arrondit un nombre à un nombre spécifié de décimales.
 * @param {number} value - Valeur à arrondir
 * @param {number} [decimals=2] - Nombre de décimales
 * @returns {number} Valeur arrondie
 */
export const roundNumber = (value, decimals = 2) => {
  if (isNaN(value)) return 0;
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
};

/**
 * Vérifie si la plateforme actuelle est macOS.
 * @returns {boolean} True si la plateforme est macOS
 */
export const isMacOS = () => {
  return window.navigator.platform.toUpperCase().indexOf('MAC') >= 0;
};

/**
 * Récupère le nom du système d'exploitation actuel.
 * @returns {string} Nom du système d'exploitation
 */
export const getOSName = () => {
  const userAgent = window.navigator.userAgent;
  const platform = window.navigator.platform;
  
  if (/Mac/.test(platform)) return 'MacOS';
  if (/Win/.test(platform)) return 'Windows';
  if (/Linux/.test(platform)) return 'Linux';
  if (/iPhone|iPad|iPod/.test(userAgent)) return 'iOS';
  if (/Android/.test(userAgent)) return 'Android';
  
  return 'Unknown';
};

/**
 * Capitalise la première lettre d'une chaîne.
 * @param {string} str - Chaîne à capitaliser
 * @returns {string} Chaîne avec première lettre en majuscule
 */
export const capitalizeFirstLetter = (str) => {
  if (!str || typeof str !== 'string') return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};