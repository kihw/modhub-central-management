// src/context/BackendContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import ApiService from '../services/api';

const BackendContext = createContext();

export const BackendProvider = ({ children }) => {
  const [status, setStatus] = useState({
    isConnected: false,
    isChecking: true,
    lastChecked: null,
    version: null,
    error: null,
  });

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        setStatus(prev => ({ ...prev, isChecking: true }));
        const response = await ApiService.getSystemStatus();
        setStatus({
          isConnected: true,
          isChecking: false,
          lastChecked: new Date(),
          version: response.version || 'unknown',
          error: null,
        });
      } catch (error) {
        setStatus({
          isConnected: false,
          isChecking: false,
          lastChecked: new Date(),
          version: null,
          error: error.message || 'Failed to connect to backend',
        });
      }
    };

    // Check backend status on mount
    checkBackendStatus();

    // Set up polling
    const intervalId = setInterval(checkBackendStatus, 10000);
    return () => clearInterval(intervalId);
  }, []);

  const reconnect = async () => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    try {
      const response = await ApiService.getSystemStatus();
      setStatus({
        isConnected: true,
        isChecking: false,
        lastChecked: new Date(),
        version: response.version || 'unknown',
        error: null,
      });
      return true;
    } catch (error) {
      setStatus({
        isConnected: false,
        isChecking: false,
        lastChecked: new Date(),
        version: null,
        error: error.message || 'Failed to connect to backend',
      });
      return false;
    }
  };

  return (
    <BackendContext.Provider value={{ ...status, reconnect }}>
      {children}
    </BackendContext.Provider>
  );
};

export const useBackend = () => useContext(BackendContext);

export default BackendContext;