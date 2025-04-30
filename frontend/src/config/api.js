export const API_CONFIG = {
  BASE_URL: "/api",
  ENDPOINTS: {
    MODS: "/mods",
    MOD_TOGGLE: (id) => `/mods/${id}/toggle`,
    RULES: "/automation",
    RESOURCES: "/system/resources/current",
    PROCESSES: "/system/processes",
    SETTINGS: "/settings",
  },
  // Mappage entre les types de mod et les icônes/couleurs
  MOD_TYPES: {
    gaming: { icon: "GiConsoleController", color: "text-red-500" },
    night: { icon: "FiMoon", color: "text-blue-500" },
    media: { icon: "FiMusic", color: "text-green-500" },
    custom: { icon: "FiSettings", color: "text-purple-500" },
  },
};
