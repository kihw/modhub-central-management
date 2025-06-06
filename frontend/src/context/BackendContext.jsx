// src/context/BackendContext.jsx
import React, { createContext, useState, useEffect, useContext } from "react";
import axios from "axios";
import useIsMounted from "../hooks/useIsMounted";

const BackendContext = createContext();

export const BackendProvider = ({ children }) => {
  const [status, setStatus] = useState({
    isConnected: false,
    isChecking: true,
    lastChecked: null,
    version: null,
    error: null,
  });

  // Use our custom hook to track component mounted state
  const isMounted = useIsMounted();

  // Définition de l'URL de l'API - corrigée pour utiliser le port 8668
  const API_BASE_URL =
    process.env.NODE_ENV === "development"
      ? "http://localhost:8668/api" // En dev, on utilise l'URL directe avec le bon port
      : "http://localhost:8668/api"; // En prod, on utilise l'URL directe avec le bon port

  const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 5000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  useEffect(() => {
    let timeoutId = null;
    let isPolling = false;

    const checkBackendStatus = async () => {
      if (isPolling) return;
      isPolling = true;

      try {
        if (isMounted.current) {
          setStatus((prev) => ({ ...prev, isChecking: true }));
        }

        const response = await axiosInstance.get("/health");

        if (isMounted.current) {
          setStatus({
            isConnected: true,
            isChecking: false,
            lastChecked: new Date(),
            version: response.data.version || "unknown",
            error: null,
          });
        }
      } catch (error) {
        if (isMounted.current) {
          setStatus({
            isConnected: false,
            isChecking: false,
            lastChecked: new Date(),
            version: null,
            error: error.message || "Failed to connect to backend",
          });
        }
      } finally {
        isPolling = false;
      }
    };

    // Check backend status on mount
    checkBackendStatus();

    // Set up polling with a safer approach
    const setupNextPoll = () => {
      if (!isMounted.current) return;

      const interval = status.isConnected ? 30000 : 10000;
      timeoutId = setTimeout(() => {
        if (!isMounted.current) return;

        if (!status.isConnected) {
          console.log("Retrying backend connection...");
        }
        checkBackendStatus().finally(() => {
          setupNextPoll();
        });
      }, interval);
    };

    setupNextPoll();

    // Cleanup function
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [status.isConnected]);

  const reconnect = async () => {
    if (!isMounted.current) return false;

    setStatus((prev) => ({ ...prev, isChecking: true }));

    try {
      console.log("Manually reconnecting to backend...");
      const response = await axiosInstance.get("/status");

      if (isMounted.current) {
        setStatus({
          isConnected: true,
          isChecking: false,
          lastChecked: new Date(),
          version: response.data.version || "unknown",
          error: null,
        });

        console.log("Manual reconnection successful");
      }
      return true;
    } catch (error) {
      if (isMounted.current) {
        console.error("Manual reconnection failed:", error.message);
        setStatus({
          isConnected: false,
          isChecking: false,
          lastChecked: new Date(),
          version: null,
          error: error.message || "Failed to connect to backend",
        });
      }
      return false;
    }
  };

  // Provide the API client to components
  const apiClient = {
    get: (endpoint, config) => axiosInstance.get(endpoint, config),
    post: (endpoint, data, config) =>
      axiosInstance.post(endpoint, data, config),
    put: (endpoint, data, config) => axiosInstance.put(endpoint, data, config),
    patch: (endpoint, data, config) =>
      axiosInstance.patch(endpoint, data, config),
    delete: (endpoint, config) => axiosInstance.delete(endpoint, config),
  };

  return (
    <BackendContext.Provider
      value={{
        ...status,
        reconnect,
        apiClient,
        backendUrl: API_BASE_URL,
      }}
    >
      {children}
    </BackendContext.Provider>
  );
};

export const useBackend = () => useContext(BackendContext);

export default BackendContext;
