import { create } from "zustand";
import { persist } from "zustand/middleware";

const useSettingsStore = create(
  persist(
    (set, get) => ({
      // General settings
      autoStartWithSystem: false,
      minimizeToTray: true,
      showNotifications: true,
      language: "en",
      theme: "system", // 'light', 'dark', 'system'

      // App behavior
      autoSwitchMods: true,
      modPriorityOrder: [], // ordered list of mod ids by priority
      conflictResolution: "priority", // 'priority', 'last-activated', 'ask-user'

      // Process scanning
      scanInterval: 5000, // in milliseconds
      ignoredProcesses: [], // list of process names to ignore

      // Resources
      resourceMonitoring: true,
      resourceWarningThresholds: {
        cpu: 85, // percentage
        memory: 80, // percentage
        temperature: 80, // celsius
      },

      // Performance
      performanceMode: "balanced", // 'performance', 'balanced', 'power-saving'

      // API settings
      apiPort: 8668,
      enableExternalAPI: false,
      apiAuthRequired: true,
      apiKey: "",

      // Updates
      checkForUpdates: true,
      autoInstallUpdates: false,
      betaChannel: false,

      // Debug
      debugMode: false,
      logLevel: "info", // 'debug', 'info', 'warn', 'error'

      // Helper functions
      updateSetting: (key, value) => {
        set({ [key]: value });
      },

      updateNestedSetting: (parentKey, childKey, value) => {
        set((state) => ({
          [parentKey]: {
            ...state[parentKey],
            [childKey]: value,
          },
        }));
      },

      resetSettings: () => {
        set({
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
        });
      },

      addIgnoredProcess: (processName) => {
        set((state) => ({
          ignoredProcesses: [...state.ignoredProcesses, processName],
        }));
      },

      removeIgnoredProcess: (processName) => {
        set((state) => ({
          ignoredProcesses: state.ignoredProcesses.filter(
            (p) => p !== processName
          ),
        }));
      },

      updateModPriority: (modIds) => {
        set({ modPriorityOrder: modIds });
      },

      getEffectiveTheme: () => {
        const { theme } = get();
        if (theme === "system") {
          return window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
        }
        return theme;
      },

      generateApiKey: () => {
        const randomKey = [...Array(32)]
          .map(() => Math.floor(Math.random() * 36).toString(36))
          .join("");
        set({ apiKey: randomKey });
        return randomKey;
      },
    }),
    {
      name: "modhub-settings",
      version: 1,
    }
  )
);

export default useSettingsStore;
