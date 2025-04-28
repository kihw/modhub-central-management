export const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export const STATUS = {
  CONNECTED: "connected",
  DISCONNECTED: "disconnected",
  UNKNOWN: "unknown",
};

export const THEMES = {
  LIGHT: "light",
  DARK: "dark",
};

export const DEFAULT_SCHEDULE = "0 0 * * *"; // Ex: Cron par défaut (tous les jours à minuit)

// Autres constantes possibles
export const APP_NAME = "ModHub Central Management";
