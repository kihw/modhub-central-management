import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  general: {
    startWithWindows: true,
    minimizeToTray: true,
    checkForUpdates: true,
    theme: 'system',
    language: 'en',
    notifications: {
      enabled: true,
      showModActivations: true,
      showModErrors: true,
      showSystemEvents: false,
    },
  },
  automation: {
    scanInterval: 5,
    enableAutoMode: true,
    conflictResolution: 'priority',
    applyDelay: 1000,
  },
  performance: {
    resourceUsageLimit: 'medium',
    loggingLevel: 'normal',
    enableMetrics: true,
  },
  developer: {
    enableDevTools: false,
    showAdvancedOptions: false,
    experimentalFeatures: false,
  },
  ui: {
    sidebarCollapsed: false,
    dashboardLayout: 'grid',
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

const settingsSlice = createSlice({
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
      state.general.notifications = { ...state.general.notifications, ...action.payload };
    },
    toggleTheme: (state) => {
      const themes = ['light', 'dark', 'system'];
      const currentIndex = themes.indexOf(state.general.theme);
      state.general.theme = themes[(currentIndex + 1) % themes.length];
    },
    toggleSidebar: (state) => {
      state.ui.sidebarCollapsed = !state.ui.sidebarCollapsed;
    },
    resetSettings: () => initialState,
    importSettings: (state, action) => ({
      ...initialState,
      ...action.payload,
    }),
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
  importSettings,
} = settingsSlice.actions;

export const selectGeneralSettings = state => state.settings.general;
export const selectAutomationSettings = state => state.settings.automation;
export const selectPerformanceSettings = state => state.settings.performance;
export const selectDeveloperSettings = state => state.settings.developer;
export const selectUISettings = state => state.settings.ui;
export const selectUserSettings = state => state.settings.user;
export const selectTheme = state => state.settings.general.theme;
export const selectNotificationSettings = state => state.settings.general.notifications;

export default settingsSlice.reducer;