import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  general: {
    startWithWindows: true,
    minimizeToTray: true,
    checkForUpdates: true,
    theme: 'system', // 'light', 'dark', 'system'
    language: 'en', // 'en', 'fr', etc.
    notifications: {
      enabled: true,
      showModActivations: true,
      showModErrors: true,
      showSystemEvents: false,
    },
  },
  automation: {
    scanInterval: 5, // in seconds
    enableAutoMode: true,
    conflictResolution: 'priority', // 'priority', 'last-activated', 'ask'
    applyDelay: 1000, // milliseconds to wait before applying mod changes
  },
  performance: {
    resourceUsageLimit: 'medium', // 'low', 'medium', 'high'
    loggingLevel: 'normal', // 'minimal', 'normal', 'verbose', 'debug'
    enableMetrics: true,
  },
  developer: {
    enableDevTools: false,
    showAdvancedOptions: false,
    experimentalFeatures: false,
  },
  ui: {
    sidebarCollapsed: false,
    dashboardLayout: 'grid', // 'grid', 'list'
    showActiveModsOnTop: true,
    animationsEnabled: true,
  },
  user: {
    profileId: null,
    userName: '',
    userEmail: '',
    preferences: {
      defaultMod: null,
      favoriteApps: [],
    },
  },
};

export const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateGeneralSettings: (state, action) => {
      state.general = { ...state.general, ...action.payload };
    },
    updateAutomationSettings: (state, action) => {
      state.automation = { ...state.automation, ...action.payload };
    },
    updatePerformanceSettings: (state, action) => {
      state.performance = { ...state.performance, ...action.payload };
    },
    updateDeveloperSettings: (state, action) => {
      state.developer = { ...state.developer, ...action.payload };
    },
    updateUISettings: (state, action) => {
      state.ui = { ...state.ui, ...action.payload };
    },
    updateUserSettings: (state, action) => {
      state.user = { ...state.user, ...action.payload };
    },
    updateNotificationSettings: (state, action) => {
      state.general.notifications = { 
        ...state.general.notifications, 
        ...action.payload 
      };
    },
    toggleTheme: (state) => {
      if (state.general.theme === 'light') {
        state.general.theme = 'dark';
      } else if (state.general.theme === 'dark') {
        state.general.theme = 'system';
      } else {
        state.general.theme = 'light';
      }
    },
    toggleSidebar: (state) => {
      state.ui.sidebarCollapsed = !state.ui.sidebarCollapsed;
    },
    resetSettings: (state) => {
      return initialState;
    },
    importSettings: (state, action) => {
      return { ...initialState, ...action.payload };
    }
  },
});

export const {
  updateGeneralSettings,
  updateAutomationSettings,
  updatePerformanceSettings,
  updateDeveloperSettings,
  updateUISettings,
  updateUserSettings,
  updateNotificationSettings,
  toggleTheme,
  toggleSidebar,
  resetSettings,
  importSettings
} = settingsSlice.actions;

// Selectors
export const selectGeneralSettings = (state) => state.settings.general;
export const selectAutomationSettings = (state) => state.settings.automation;
export const selectPerformanceSettings = (state) => state.settings.performance;
export const selectDeveloperSettings = (state) => state.settings.developer;
export const selectUISettings = (state) => state.settings.ui;
export const selectUserSettings = (state) => state.settings.user;
export const selectTheme = (state) => state.settings.general.theme;
export const selectNotificationSettings = (state) => state.settings.general.notifications;

export default settingsSlice.reducer;