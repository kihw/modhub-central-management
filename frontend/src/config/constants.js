export const APP_NAME = "ModHub Central";
export const APP_VERSION = "0.1.0";
export const APP_STATUS = "development";

export const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8668/api";

export const API_ENDPOINTS = Object.freeze({
  MODS: "/mods",
  PROCESSES: "/processes",
  RULES: "/rules", 
  SYSTEM: "/system",
  SETTINGS: "/settings",
  PROFILES: "/profiles",
  HEALTH: "/health"
});

export const MOD_TYPES = Object.freeze({
  GAMING: "gaming",
  NIGHT: "night", 
  MEDIA: "media",
  CUSTOM: "custom",
  SYSTEM: "system"
});

export const MOD_STATUS = Object.freeze({
  ACTIVE: "active",
  INACTIVE: "inactive",
  PENDING: "pending",
  ERROR: "error",
  DISABLED: "disabled"
});

export const CONDITION_TYPES = Object.freeze({
  PROCESS_RUNNING: "process_running",
  TIME_RANGE: "time_range",
  INACTIVITY: "inactivity", 
  SYSTEM_STATE: "system_state",
  BATTERY_LEVEL: "battery_level",
  NETWORK_STATUS: "network_status",
  CUSTOM: "custom"
});

export const ACTION_TYPES = Object.freeze({
  ACTIVATE_MOD: "activate_mod",
  DEACTIVATE_MOD: "deactivate_mod",
  ADJUST_SETTING: "adjust_setting",
  RUN_COMMAND: "run_command",
  TOGGLE_FEATURE: "toggle_feature",
  NOTIFY: "notify",
  CUSTOM: "custom"
});

export const PRIORITY_LEVELS = Object.freeze({
  CRITICAL: 100,
  HIGH: 75,
  MEDIUM: 50,
  LOW: 25,
  BACKGROUND: 10,
  DISABLED: 0
});

export const THEMES = Object.freeze({
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system",
  CUSTOM: "custom"
});

export const DEFAULT_SETTINGS = Object.freeze({
  theme: THEMES.SYSTEM,
  startWithSystem: true,
  minimizeToTray: true,
  notificationsEnabled: true,
  inactivityThreshold: 300,
  checkIntervalMs: 5000,
  logLevel: "info",
  nightModeStartTime: "22:00",
  nightModeEndTime: "07:00",
  backupEnabled: true,
  backupIntervalHours: 24,
  maxLogSize: 10485760,
  maxBackupCount: 5,
  autoUpdate: true
});

export const STORAGE_KEYS = Object.freeze({
  SETTINGS: "modhub-settings",
  ACTIVE_MODS: "modhub-active-mods", 
  USER_RULES: "modhub-user-rules",
  LAST_STATE: "modhub-last-state",
  BACKUP: "modhub-backup",
  CACHE: "modhub-cache",
  ERRORS: "modhub-errors"
});

export const EVENTS = Object.freeze({
  MOD_ACTIVATED: "mod-activated",
  MOD_DEACTIVATED: "mod-deactivated",
  RULE_TRIGGERED: "rule-triggered",
  SYSTEM_CHANGED: "system-changed",
  SETTINGS_UPDATED: "settings-updated",
  ERROR_OCCURRED: "error-occurred",
  BACKUP_CREATED: "backup-created",
  CACHE_CLEARED: "cache-cleared",
  UPDATE_AVAILABLE: "update-available"
});

export const PATHS = Object.freeze({
  CONFIG: "./config",
  LOGS: "./logs",
  MODULES: "./modules",
  PLUGINS: "./plugins",
  USER_DATA: "./user-data",
  BACKUP: "./backup",
  CACHE: "./cache",
  TEMP: "./temp"
});

export const FEATURES = Object.freeze({
  CUSTOM_MODS: true,
  ADVANCED_RULES: true,
  SYSTEM_MONITORING: true,
  PLUGIN_SUPPORT: false,
  CLOUD_SYNC: false,
  AUTO_BACKUP: true,
  ERROR_REPORTING: true,
  AUTO_UPDATE: true
});