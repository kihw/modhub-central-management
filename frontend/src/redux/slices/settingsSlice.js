import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

type Theme = 'light' | 'dark' | 'system';
type ResourceUsage = 'low' | 'medium' | 'high';
type LoggingLevel = 'minimal' | 'normal' | 'verbose';
type ConflictResolution = 'priority' | 'manual';
type DashboardLayout = 'grid' | 'list';

interface NotificationSettings {
  enabled: boolean;
  showModActivations: boolean;
  showModErrors: boolean;
  showSystemEvents: boolean;
}

interface GeneralSettings {
  startWithWindows: boolean;
  minimizeToTray: boolean;
  checkForUpdates: boolean;
  theme: Theme;
  language: string;
  notifications: NotificationSettings;
}

interface AutomationSettings {
  scanInterval: number;
  enableAutoMode: boolean;
  conflictResolution: ConflictResolution;
  applyDelay: number;
}

interface PerformanceSettings {
  resourceUsageLimit: ResourceUsage;
  loggingLevel: LoggingLevel;
  enableMetrics: boolean;
}

interface DeveloperSettings {
  enableDevTools: boolean;
  showAdvancedOptions: boolean;
  experimentalFeatures: boolean;
}

interface UISettings {
  sidebarCollapsed: boolean;
  dashboardLayout: DashboardLayout;
  showActiveModsOnTop: boolean;
  animationsEnabled: boolean;
}

interface UserPreferences {
  defaultMod: string | null;
  favoriteApps: string[];
}

interface UserSettings {
  profileId: string | null;
  userName: string;
  userEmail: string;
  preferences: UserPreferences;
}

interface SettingsState {
  general: GeneralSettings;
  automation: AutomationSettings;
  performance: PerformanceSettings;
  developer: DeveloperSettings;
  ui: UISettings;
  user: UserSettings;
}

const initialState: SettingsState = {
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
    updateGeneralSettings: (state, action: PayloadAction<Partial<GeneralSettings>>) => {
      state.general = { ...state.general, ...action.payload };
    },
    updateAutomationSettings: (state, action: PayloadAction<Partial<AutomationSettings>>) => {
      state.automation = { ...state.automation, ...action.payload };
    },
    updatePerformanceSettings: (state, action: PayloadAction<Partial<PerformanceSettings>>) => {
      state.performance = { ...state.performance, ...action.payload };
    },
    updateDeveloperSettings: (state, action: PayloadAction<Partial<DeveloperSettings>>) => {
      state.developer = { ...state.developer, ...action.payload };
    },
    updateUISettings: (state, action: PayloadAction<Partial<UISettings>>) => {
      state.ui = { ...state.ui, ...action.payload };
    },
    updateUserSettings: (state, action: PayloadAction<Partial<UserSettings>>) => {
      state.user = { ...state.user, ...action.payload };
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<NotificationSettings>>) => {
      state.general.notifications = { ...state.general.notifications, ...action.payload };
    },
    toggleTheme: (state) => {
      const themes: Theme[] = ['light', 'dark', 'system'];
      const currentIndex = themes.indexOf(state.general.theme);
      state.general.theme = themes[(currentIndex + 1) % themes.length];
    },
    toggleSidebar: (state) => {
      state.ui.sidebarCollapsed = !state.ui.sidebarCollapsed;
    },
    resetSettings: () => initialState,
    importSettings: (state, action: PayloadAction<DeepPartial<SettingsState>>) => ({
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

export const selectGeneralSettings = (state: RootState) => state.settings.general;
export const selectAutomationSettings = (state: RootState) => state.settings.automation;
export const selectPerformanceSettings = (state: RootState) => state.settings.performance;
export const selectDeveloperSettings = (state: RootState) => state.settings.developer;
export const selectUISettings = (state: RootState) => state.settings.ui;
export const selectUserSettings = (state: RootState) => state.settings.user;
export const selectTheme = (state: RootState) => state.settings.general.theme;
export const selectNotificationSettings = (state: RootState) => state.settings.general.notifications;

type DeepPartial<T> = T extends object ? { [P in keyof T]?: DeepPartial<T[P]> } : T;

export default settingsSlice.reducer;