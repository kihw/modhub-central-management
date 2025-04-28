import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  general: {
    startWithWindows: true,
    minimizeToTray: true,
    theme: 'system', // 'light', 'dark', 'system'
    language: 'en',
    checkForUpdates: true,
  },
  notifications: {
    showNotifications: true,
    soundEnabled: true,
    notifyOnModChange: true,
    notifyOnProfileChange: true,
    notifyOnError: true,
  },
  advanced: {
    pollingRate: 1000, // ms
    lowPowerMode: false,
    debugMode: false,
    logLevel: 'info', // 'error', 'warn', 'info', 'debug'
    apiPort: 8000,
  },
  privacy: {
    collectAnonymousUsageData: false,
    sendErrorReports: true,
  },
  backups: {
    enableAutomaticBackups: true,
    backupFrequency: 'weekly', // 'daily', 'weekly', 'monthly'
    maxBackupCount: 5,
    backupLocation: '',
  },
  shortcuts: {
    toggleGamingMod: 'Ctrl+Alt+G',
    toggleNightMod: 'Ctrl+Alt+N',
    toggleMediaMod: 'Ctrl+Alt+M',
    openDashboard: 'Ctrl+Alt+D',
  }
};

export const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateGeneralSettings: (state, action) => {
      state.general = { ...state.general, ...action.payload };
    },
    updateNotificationSettings: (state, action) => {
      state.notifications = { ...state.notifications, ...action.payload };
    },
    updateAdvancedSettings: (state, action) => {
      state.advanced = { ...state.advanced, ...action.payload };
    },
    updatePrivacySettings: (state, action) => {
      state.privacy = { ...state.privacy, ...action.payload };
    },
    updateBackupSettings: (state, action) => {
      state.backups = { ...state.backups, ...action.payload };
    },
    updateShortcuts: (state, action) => {
      state.shortcuts = { ...state.shortcuts, ...action.payload };
    },
    setTheme: (state, action) => {
      state.general.theme = action.payload;
    },
    setLanguage: (state, action) => {
      state.general.language = action.payload;
    },
    resetToDefaults: (state) => {
      return initialState;
    },
    importSettings: (state, action) => {
      // Merge imported settings with current settings structure to ensure compatibility
      const importedSettings = action.payload;
      return {
        general: { ...state.general, ...importedSettings.general },
        notifications: { ...state.notifications, ...importedSettings.notifications },
        advanced: { ...state.advanced, ...importedSettings.advanced },
        privacy: { ...state.privacy, ...importedSettings.privacy },
        backups: { ...state.backups, ...importedSettings.backups },
        shortcuts: { ...state.shortcuts, ...importedSettings.shortcuts },
      };
    },
  },
});

export const { 
  updateGeneralSettings,
  updateNotificationSettings,
  updateAdvancedSettings, 
  updatePrivacySettings,
  updateBackupSettings,
  updateShortcuts,
  setTheme,
  setLanguage,
  resetToDefaults,
  importSettings
} = settingsSlice.actions;

// Selectors
export const selectAllSettings = (state) => state.settings;
export const selectGeneralSettings = (state) => state.settings.general;
export const selectNotificationSettings = (state) => state.settings.notifications;
export const selectAdvancedSettings = (state) => state.settings.advanced;
export const selectPrivacySettings = (state) => state.settings.privacy;
export const selectBackupSettings = (state) => state.settings.backups;
export const selectShortcuts = (state) => state.settings.shortcuts;
export const selectTheme = (state) => state.settings.general.theme;

export default settingsSlice.reducer;