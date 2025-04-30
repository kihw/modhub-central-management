import { createSlice } from '@reduxjs/toolkit';

const SUPPORTED_LANGUAGES = Object.freeze(['en', 'fr']);
const DEFAULT_LANGUAGE = SUPPORTED_LANGUAGES[0];
const STORAGE_KEY = 'modHubLanguage';

const getBrowserLanguage = () => {
  try {
    const browserLang = navigator.language || navigator.userLanguage;
    const shortLang = browserLang?.split('-')[0]?.toLowerCase();
    return SUPPORTED_LANGUAGES.includes(shortLang) ? shortLang : DEFAULT_LANGUAGE;
  } catch {
    return DEFAULT_LANGUAGE;
  }
};

const getStoredLanguage = () => {
  try {
    const storedLang = localStorage.getItem(STORAGE_KEY);
    return SUPPORTED_LANGUAGES.includes(storedLang) ? storedLang : getBrowserLanguage();
  } catch {
    return getBrowserLanguage();
  }
};

const initialState = Object.freeze({
  language: getStoredLanguage(),
  available: [...SUPPORTED_LANGUAGES],
});

export const languageSlice = createSlice({
  name: 'language',
  initialState,
  reducers: {
    setLanguage: (state, { payload }) => {
      const newLang = payload?.toLowerCase?.();
      if (newLang && state.available.includes(newLang)) {
        state.language = newLang;
        try {
          localStorage.setItem(STORAGE_KEY, newLang);
        } catch (error) {
          console.error('Failed to store language preference:', error);
        }
      }
    },
    addLanguage: (state, { payload }) => {
      const langToAdd = payload?.toLowerCase?.();
      if (langToAdd && typeof langToAdd === 'string' && !state.available.includes(langToAdd)) {
        state.available = [...new Set([...state.available, langToAdd])].sort();
      }
    },
    removeLanguage: (state, { payload }) => {
      const langToRemove = payload?.toLowerCase?.();
      if (langToRemove && 
          state.available.length > 1 && 
          langToRemove !== state.language &&
          langToRemove !== DEFAULT_LANGUAGE) {
        state.available = state.available.filter(lang => lang !== langToRemove);
      }
    },
  },
});

export const { setLanguage, addLanguage, removeLanguage } = languageSlice.actions;

export const selectLanguage = state => state?.language?.language ?? DEFAULT_LANGUAGE;
export const selectAvailableLanguages = state => state?.language?.available ?? [DEFAULT_LANGUAGE];

export default languageSlice.reducer;