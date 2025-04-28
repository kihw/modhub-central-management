/**
 * ModHub Central - Configuration Constants
 * Contains all system-wide constants used across the application
 */

// App Information
export const APP_NAME = "ModHub Central";
export const APP_VERSION = "0.1.0";
export const APP_STATUS = "development";

// API Endpoints
export const API_BASE_URL = "http://localhost:8668/api";
export const API_ENDPOINTS = {
  MODS: "/mods",
  PROCESSES: "/processes",
  RULES: "/rules",
  SYSTEM: "/system",
  SETTINGS: "/settings",
  PROFILES: "/profiles",
};

// Mod Types
export const MOD_TYPES = {
  GAMING: "gaming",
  NIGHT: "night",
  MEDIA: "media",
  CUSTOM: "custom",
};

// Mod Statuses
export const MOD_STATUS = {
  ACTIVE: "active",
  INACTIVE: "inactive",
  PENDING: "pending",
  ERROR: "error",
};

// Rule Conditions
export const CONDITION_TYPES = {
  PROCESS_RUNNING: "process_running",
  TIME_RANGE: "time_range",
  INACTIVITY: "inactivity",
  SYSTEM_STATE: "system_state",
  CUSTOM: "custom",
};

// Rule Actions
export const ACTION_TYPES = {
  ACTIVATE_MOD: "activate_mod",
  DEACTIVATE_MOD: "deactivate_mod",
  ADJUST_SETTING: "adjust_setting",
  RUN_COMMAND: "run_command",
  CUSTOM: "custom",
};

// Priority Levels
export const PRIORITY_LEVELS = {
  CRITICAL: 100,
  HIGH: 75,
  MEDIUM: 50,
  LOW: 25,
  BACKGROUND: 10,
};

// Theme Options
export const THEMES = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system",
};

// Default Settings
export const DEFAULT_SETTINGS = {
  theme: THEMES.SYSTEM,
  startWithSystem: true,
  minimizeToTray: true,
  notificationsEnabled: true,
  inactivityThreshold: 300, // 5 minutes in seconds
  checkIntervalMs: 5000, // 5 seconds
  logLevel: "info",
  nightModeStartTime: "22:00",
  nightModeEndTime: "07:00",
};

// Local Storage Keys
export const STORAGE_KEYS = {
  SETTINGS: "modhub-settings",
  ACTIVE_MODS: "modhub-active-mods",
  USER_RULES: "modhub-user-rules",
  LAST_STATE: "modhub-last-state",
};

// Events
export const EVENTS = {
  MOD_ACTIVATED: "mod-activated",
  MOD_DEACTIVATED: "mod-deactivated",
  RULE_TRIGGERED: "rule-triggered",
  SYSTEM_CHANGED: "system-changed",
  SETTINGS_UPDATED: "settings-updated",
  ERROR_OCCURRED: "error-occurred",
};

// Paths
export const PATHS = {
  CONFIG: "./config",
  LOGS: "./logs",
  MODULES: "./modules",
  PLUGINS: "./plugins",
  USER_DATA: "./user-data",
};

// Feature Flags
export const FEATURES = {
  CUSTOM_MODS: true,
  ADVANCED_RULES: true,
  SYSTEM_MONITORING: true,
  PLUGIN_SUPPORT: false, // Coming soon
  CLOUD_SYNC: false, // Coming soon
};
