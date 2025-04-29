// src/context/BackendContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const BackendContext = createContext();

export const BackendProvider = ({ children }) => {
  const [status, setStatus] = useState({
    isConnected: false,
    isChecking: true,
    lastChecked: null,
    version: null,
    error: null,
  });

  const API_URL = 'http://localhost:8668';

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        setStatus(prev => ({ ...prev, isChecking: true }));
        // Use a direct status endpoint with a short timeout
        const response = await axios.get(`${API_URL}/api/status`, {
          timeout: 3000
        });
        
        setStatus({
          isConnected: true,
          isChecking: false,
          lastChecked: new Date(),
          version: response.data.version || 'unknown',
          error: null,
        });
        console.log("Backend connection successful:", response.data);
      } catch (error) {
        console.error("Backend connection error:", error.message);
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

    // Set up polling with increasing intervals on failure
    const intervalId = setInterval(() => {
      if (!status.isConnected) {
        console.log("Retrying backend connection...");
      }
      checkBackendStatus();
    }, status.isConnected ? 10000 : 5000); // Check more frequently if disconnected
    
    return () => clearInterval(intervalId);
  }, [status.isConnected]);

  const reconnect = async () => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    try {
      console.log("Manually reconnecting to backend...");
      const response = await axios.get(`${API_URL}/api/status`, {
        timeout: 3000
      });
      
      setStatus({
        isConnected: true,
        isChecking: false,
        lastChecked: new Date(),
        version: response.data.version || 'unknown',
        error: null,
      });
      
      console.log("Manual reconnection successful");
      return true;
    } catch (error) {
      console.error("Manual reconnection failed:", error.message);
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
    <BackendContext.Provider value={{ 
      ...status, 
      reconnect,
      backendUrl: API_URL
    }}>
      {children}
    </BackendContext.Provider>
  );
};

export const useBackend = () => useContext(BackendContext);

export default BackendContext;