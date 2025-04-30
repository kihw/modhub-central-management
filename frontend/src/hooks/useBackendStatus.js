import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const initialStatus = {
  isConnected: false,
  isChecking: true,
  lastChecked: null,
  version: null,
  error: null,
  services: {
    processScan: false,
    modEngine: false,
    deviceControl: false,
  },
};

const useBackendStatus = (url = "http://localhost:8668", interval = 5000) => {
  const [status, setStatus] = useState(initialStatus);

  const checkStatus = useCallback(async (abortSignal) => {
    try {
      const response = await axios.get(`${url}/api/status`, {
        timeout: 3000,
        signal: abortSignal,
        validateStatus: status => status === 200,
      });
      
      return {
        isConnected: true,
        isChecking: false,
        lastChecked: new Date(),
        version: response?.data?.version || "unknown",
        error: null,
        services: {
          processScan: Boolean(response?.data?.services?.processScan),
          modEngine: Boolean(response?.data?.services?.modEngine),
          deviceControl: Boolean(response?.data?.services?.deviceControl),
        },
      };
    } catch (error) {
      if (error.name === "AbortError") {
        return null;
      }
      return {
        ...initialStatus,
        isChecking: false,
        lastChecked: new Date(),
        error: error?.message || "Failed to connect to backend",
      };
    }
  }, [url]);

  const checkBackendStatus = useCallback(async (abortSignal) => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    const newStatus = await checkStatus(abortSignal);
    if (newStatus) {
      setStatus(newStatus);
    }
  }, [checkStatus]);

  const reconnect = useCallback(async () => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    const newStatus = await checkStatus();
    if (newStatus) {
      setStatus(newStatus);
    }
  }, [checkStatus]);

  useEffect(() => {
    const abortController = new AbortController();
    let timeoutId;

    const poll = async () => {
      await checkBackendStatus(abortController.signal);
      timeoutId = setTimeout(poll, interval);
    };

    poll();

    return () => {
      abortController.abort();
      clearTimeout(timeoutId);
    };
  }, [checkBackendStatus, interval]);

  return {
    ...status,
    reconnect,
  };
};

export default useBackendStatus;