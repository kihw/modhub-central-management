import React, { createContext, useContext, useEffect, useState } from 'react';

const ElectronAPIContext = createContext(null);

export const useElectronAPI = () => useContext(ElectronAPIContext);

export const ElectronAPIProvider = ({ children }) => {
  const [api, setAPI] = useState(null);
  const [isElectron, setIsElectron] = useState(false);

  useEffect(() => {
    // Check if we're running in Electron
    if (window.electron) {
      setIsElectron(true);
      setAPI({
        // Process management
        getRunningProcesses: window.electron.getRunningProcesses,
        watchProcesses: window.electron.watchProcesses,
        stopWatchingProcesses: window.electron.stopWatchingProcesses,
        
        // Mod management
        getMods: window.electron.getMods,
        enableMod: window.electron.enableMod,
        disableMod: window.electron.disableMod,
        toggleMod: window.electron.toggleMod,
        createMod: window.electron.createMod,
        updateMod: window.electron.updateMod,
        deleteMod: window.electron.deleteMod,
        
        // Rule management
        getRules: window.electron.getRules,
        createRule: window.electron.createRule,
        updateRule: window.electron.updateRule,
        deleteRule: window.electron.deleteRule,
        
        // System information
        getSystemStatus: window.electron.getSystemStatus,
        
        // Settings
        getSettings: window.electron.getSettings,
        updateSettings: window.electron.updateSettings,
        
        // Event listeners
        on: (channel, callback) => {
          const subscription = window.electron.on(channel, callback);
          return () => subscription.remove();
        },
        
        // Utilities
        openExternal: window.electron.openExternal,
        showNotification: window.electron.showNotification,
        
        // Debug functions
        isDebugMode: window.electron.isDebugMode,
        logDebug: window.electron.logDebug
      });
    } else {
      console.warn('This app is running outside of Electron environment. Some features may not be available.');
      // Provide mock implementations for development outside Electron
      setAPI({
        getRunningProcesses: async () => [],
        watchProcesses: () => console.log('Mock: Watching processes'),
        stopWatchingProcesses: () => console.log('Mock: Stopped watching processes'),
        getMods: async () => [],
        enableMod: async () => console.log('Mock: Enable mod'),
        disableMod: async () => console.log('Mock: Disable mod'),
        toggleMod: async () => console.log('Mock: Toggle mod'),
        createMod: async () => console.log('Mock: Create mod'),
        updateMod: async () => console.log('Mock: Update mod'),
        deleteMod: async () => console.log('Mock: Delete mod'),
        getRules: async () => [],
        createRule: async () => console.log('Mock: Create rule'),
        updateRule: async () => console.log('Mock: Update rule'),
        deleteRule: async () => console.log('Mock: Delete rule'),
        getSystemStatus: async () => ({}),
        getSettings: async () => ({}),
        updateSettings: async () => console.log('Mock: Update settings'),
        on: () => ({ remove: () => {} }),
        openExternal: (url) => window.open(url, '_blank'),
        showNotification: (opts) => console.log('Mock notification:', opts),
        isDebugMode: () => true,
        logDebug: console.log
      });
    }
  }, []);

  return (
    <ElectronAPIContext.Provider value={{ api, isElectron }}>
      {children}
    </ElectronAPIContext.Provider>
  );
};

export default ElectronAPIContext;