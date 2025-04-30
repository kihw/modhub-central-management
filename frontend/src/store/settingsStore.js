import { create } from "zustand";
import { persist } from "zustand/middleware";

const DEFAULT_SETTINGS = {
  autoStartWithSystem: false,
  minimizeToTray: true,
  showNotifications: true,
  language: "en",
  theme: "system",
  autoSwitchMods: true,
  modPriorityOrder: [],
  conflictResolution: "priority",
  scanInterval: 5000,
  ignoredProcesses: [],
  resourceMonitoring: true,
  resourceWarningThresholds: {
    cpu: 85,
    memory: 80,
    temperature: 80,
  },
  performanceMode: "balanced",
  apiPort: 8668,
  enableExternalAPI: false,
  apiAuthRequired: true,
  apiKey: "",
  checkForUpdates: true,
  autoInstallUpdates: false,
  betaChannel: false,
  debugMode: false,
  logLevel: "info",
};

const useSettingsStore = create(
  persist(
    (set, get) => ({
      ...DEFAULT_SETTINGS,

      updateSetting: (key, value) => {
        if (!(key in DEFAULT_SETTINGS)) return;
        set({ [key]: value });
      },

      updateNestedSetting: (parentKey, childKey, value) => {
        if (!(parentKey in DEFAULT_SETTINGS) || !DEFAULT_SETTINGS[parentKey]?.[childKey]) return;
        set((state) => ({
          [parentKey]: {
            ...state[parentKey],
            [childKey]: value,
          },
        }));
      },

      resetSettings: () => set(DEFAULT_SETTINGS),

      addIgnoredProcess: (processName) => {
        const trimmedName = processName?.trim();
        if (!trimmedName) return;
        set((state) => ({
          ignoredProcesses: Array.from(new Set([...state.ignoredProcesses, trimmedName])),
        }));
      },

      removeIgnoredProcess: (processName) => {
        const trimmedName = processName?.trim();
        if (!trimmedName) return;
        set((state) => ({
          ignoredProcesses: state.ignoredProcesses.filter((p) => p !== trimmedName),
        }));
      },

      updateModPriority: (modIds) => {
        if (!Array.isArray(modIds)) return;
        set({ modPriorityOrder: Array.from(new Set(modIds)) });
      },

      getEffectiveTheme: () => {
        const { theme } = get();
        if (theme !== "system") return theme;
        
        const darkModeQuery = window?.matchMedia?.("(prefers-color-scheme: dark)");
        return darkModeQuery?.matches ? "dark" : "light";
      },

      generateApiKey: () => {
        let newKey;
        try {
          newKey = crypto.randomUUID().replace(/-/g, "");
        } catch {
          newKey = Math.random().toString(36).slice(2) + Date.now().toString(36);
        }
        set({ apiKey: newKey });
        return newKey;
      },
    }),
    {
      name: "modhub-settings",
      version: 1,
      skipHydration: true,
      partialize: (state) => 
        Object.fromEntries(
          Object.entries(state).filter(([key]) => key in DEFAULT_SETTINGS)
        ),
    }
  )
);

export default useSettingsStore;