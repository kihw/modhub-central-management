import React, { createContext, useContext } from "react";

/**
 * Exemple d'API exposée par preload.js dans Electron :
 * window.electron = {
 *   ipcRenderer: {
 *     send: (channel, data) => {},
 *     on: (channel, func) => {},
 *   },
 *   openFileDialog: () => {},
 * };
 */

const ElectronAPIContext = createContext(null);

export const ElectronAPIProvider = ({ children }) => {
  const electronAPI = window.electron || {
    ipcRenderer: {
      send: () =>
        console.warn("ipcRenderer.send called in non-Electron environment"),
      on: () =>
        console.warn("ipcRenderer.on called in non-Electron environment"),
    },
    openFileDialog: () =>
      console.warn("openFileDialog called in non-Electron environment"),
  };

  return (
    <ElectronAPIContext.Provider value={electronAPI}>
      {children}
    </ElectronAPIContext.Provider>
  );
};

export const useElectronAPI = () => {
  return useContext(ElectronAPIContext);
};
