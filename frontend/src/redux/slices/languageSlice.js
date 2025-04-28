import { createSlice } from '@reduxjs/toolkit';

const getInitialLanguage = () => {
  // Try to get language from localStorage
  const savedLanguage = localStorage.getItem('modhub-language');
  if (savedLanguage) return savedLanguage;
  
  // Otherwise use browser language or fall back to English
  const browserLang = navigator.language.split('-')[0];
  return ['en', 'fr', 'es', 'de'].includes(browserLang) ? browserLang : 'en';
};

const initialState = {
  language: getInitialLanguage(),
  availableLanguages: [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
  ]
};

const languageSlice = createSlice({
  name: 'language',
  initialState,
  reducers: {
    setLanguage: (state, action) => {
      state.language = action.payload;
      localStorage.setItem('modhub-language', action.payload);
    },
    addLanguage: (state, action) => {
      // Only add if it doesn't already exist
      if (!state.availableLanguages.some(lang => lang.code === action.payload.code)) {
        state.availableLanguages.push(action.payload);
      }
    },
    removeLanguage: (state, action) => {
      // Can't remove the current language
      if (state.language !== action.payload) {
        state.availableLanguages = state.availableLanguages.filter(
          lang => lang.code !== action.payload
        );
      }
    }
  }
});

export const { setLanguage, addLanguage, removeLanguage } = languageSlice.actions;

export const selectLanguage = (state) => state.language.language;
export const selectAvailableLanguages = (state) => state.language.availableLanguages;

export default languageSlice.reducer;