import { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Custom hook to check and monitor backend API availability
 * @param {string} url - Backend API URL
 * @param {number} interval - Polling interval in milliseconds
 * @returns {Object} Object containing backend status information
 */
const useBackendStatus = (url = 'http://localhost:8000', interval = 5000) => {
  const [status, setStatus] = useState({
    isConnected: false,
    isChecking: true,
    lastChecked: null,
    version: null,
    error: null,
    services: {
      processScan: false,
      modEngine: false,
      deviceControl: false
    }
  });

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        setStatus(prev => ({ ...prev, isChecking: true }));
        
        const response = await axios.get(`${url}/api/status`, { timeout: 3000 });
        
        if (response.status === 200) {
          setStatus({
            isConnected: true,
            isChecking: false,
            lastChecked: new Date(),
            version: response.data.version || 'unknown',
            error: null,
            services: {
              processScan: response.data.services?.processScan || false,
              modEngine: response.data.services?.modEngine || false,
              deviceControl: response.data.services?.deviceControl || false
            }
          });
        } else {
          throw new Error('Backend returned non-200 status');
        }
      } catch (error) {
        setStatus({
          isConnected: false,
          isChecking: false,
          lastChecked: new Date(),
          version: null,
          error: error.message || 'Failed to connect to backend',
          services: {
            processScan: false,
            modEngine: false,
            deviceControl: false
          }
        });
      }
    };

    // Initial check
    checkBackendStatus();

    // Set up regular polling
    const intervalId = setInterval(checkBackendStatus, interval);

    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [url, interval]);

  const reconnect = () => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    // Force a new check immediately
    axios.get(`${url}/api/status`, { timeout: 3000 })
      .then(response => {
        if (response.status === 200) {
          setStatus({
            isConnected: true,
            isChecking: false,
            lastChecked: new Date(),
            version: response.data.version || 'unknown',
            error: null,
            services: {
              processScan: response.data.services?.processScan || false,
              modEngine: response.data.services?.modEngine || false,
              deviceControl: response.data.services?.deviceControl || false
            }
          });
        }
      })
      .catch(error => {
        setStatus(prev => ({
          ...prev,
          isChecking: false,
          error: error.message || 'Failed to reconnect to backend'
        }));
      });
  };

  return {
    ...status,
    reconnect
  };
};

export default useBackendStatus;