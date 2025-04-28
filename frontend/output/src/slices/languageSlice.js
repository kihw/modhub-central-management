import { createSlice } from '@reduxjs/toolkit';

const getBrowserLanguage = () => {
  const browserLang = navigator.language || navigator.userLanguage;
  const shortLang = browserLang.split('-')[0];
  
  // Only support English and French for now
  return ['en', 'fr'].includes(shortLang) ? shortLang : 'en';
};

const initialState = {
  language: localStorage.getItem('modHubLanguage') || getBrowserLanguage(),
  available: ['en', 'fr'],
};

export const languageSlice = createSlice({
  name: 'language',
  initialState,
  reducers: {
    setLanguage: (state, action) => {
      if (state.available.includes(action.payload)) {
        state.language = action.payload;
        localStorage.setItem('modHubLanguage', action.payload);
      }
    },
    addLanguage: (state, action) => {
      if (!state.available.includes(action.payload)) {
        state.available.push(action.payload);
      }
    },
    removeLanguage: (state, action) => {
      // Can't remove all languages
      if (state.available.length > 1 && action.payload !== state.language) {
        state.available = state.available.filter(lang => lang !== action.payload);
      }
    },
  },
});

export const { setLanguage, addLanguage, removeLanguage } = languageSlice.actions;

export const selectLanguage = (state) => state.language.language;
export const selectAvailableLanguages = (state) => state.language.available;

export default languageSlice.reducer;