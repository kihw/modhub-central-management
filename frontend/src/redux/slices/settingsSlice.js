import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  theme: "light", // 'light' | 'dark'
  language: "en",
  notifications: true,
  autoUpdate: false,
  advancedMode: false,
  // Autres réglages selon les besoins de l'application
};

const settingsSlice = createSlice({
  name: "settings",
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action) => {
      state.language = action.payload;
    },
    toggleNotifications: (state) => {
      state.notifications = !state.notifications;
    },
    toggleAutoUpdate: (state) => {
      state.autoUpdate = !state.autoUpdate;
    },
    toggleAdvancedMode: (state) => {
      state.advancedMode = !state.advancedMode;
    },
    updateSettings: (state, action) => {
      return { ...state, ...action.payload };
    },
    resetSettings: () => {
      return initialState;
    },
  },
});

export const {
  setTheme,
  setLanguage,
  toggleNotifications,
  toggleAutoUpdate,
  toggleAdvancedMode,
  updateSettings,
  resetSettings,
} = settingsSlice.actions;

// Sélecteurs
export const selectTheme = (state) => state.settings.theme;
export const selectLanguage = (state) => state.settings.language;
export const selectNotifications = (state) => state.settings.notifications;
export const selectAutoUpdate = (state) => state.settings.autoUpdate;
export const selectAdvancedMode = (state) => state.settings.advancedMode;
export const selectAllSettings = (state) => state.settings;

export default settingsSlice.reducer;
