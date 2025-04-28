import React, { createContext, useState, useEffect, useCallback } from "react";
import axios from "axios";

// Create context
export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // State for active mods
  const [activeMods, setActiveMods] = useState([]);
  // State for available mods
  const [availableMods, setAvailableMods] = useState([]);
  // State for current processes
  const [processes, setProcesses] = useState([]);
  // State for system status
  const [systemStatus, setSystemStatus] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    timeOfDay: "day",
    userActive: true,
    lastActivityTime: Date.now(),
  });
  // Settings and user preferences
  const [settings, setSettings] = useState({
    autoSwitchMods: true,
    notifications: true,
    theme: "light",
    startOnBoot: false,
  });
  // Loading states
  const [loading, setLoading] = useState({
    mods: true,
    processes: true,
    systemStatus: true,
  });
  // Error states
  const [errors, setErrors] = useState({
    mods: null,
    processes: null,
    systemStatus: null,
    general: null,
  });

  // API base URL
  const API_URL = "http://localhost:8668";

  // Fetch mods from API
  const fetchMods = useCallback(async () => {
    try {
      setLoading((prev) => ({ ...prev, mods: true }));
      const response = await axios.get(`${API_URL}/api/mods`);
      setAvailableMods(response.data);
      setErrors((prev) => ({ ...prev, mods: null }));
    } catch (error) {
      console.error("Error fetching mods:", error);
      setErrors((prev) => ({ ...prev, mods: "Failed to fetch mods" }));
    } finally {
      setLoading((prev) => ({ ...prev, mods: false }));
    }
  }, []);

  // Fetch active processes
  const fetchProcesses = useCallback(async () => {
    try {
      setLoading((prev) => ({ ...prev, processes: true }));
      const response = await axios.get(`${API_URL}/api/processes`);
      setProcesses(response.data);
      setErrors((prev) => ({ ...prev, processes: null }));
    } catch (error) {
      console.error("Error fetching processes:", error);
      setErrors((prev) => ({
        ...prev,
        processes: "Failed to fetch processes",
      }));
    } finally {
      setLoading((prev) => ({ ...prev, processes: false }));
    }
  }, []);

  // Fetch system status
  const fetchSystemStatus = useCallback(async () => {
    try {
      setLoading((prev) => ({ ...prev, systemStatus: true }));
      const response = await axios.get(`${API_URL}/api/system-status`);
      setSystemStatus(response.data);
      setErrors((prev) => ({ ...prev, systemStatus: null }));
    } catch (error) {
      console.error("Error fetching system status:", error);
      setErrors((prev) => ({
        ...prev,
        systemStatus: "Failed to fetch system status",
      }));
    } finally {
      setLoading((prev) => ({ ...prev, systemStatus: false }));
    }
  }, []);

  // Toggle mod activation
  const toggleMod = useCallback(async (modId, active) => {
    try {
      const response = await axios.post(`${API_URL}/api/mods/${modId}/toggle`, {
        active,
      });

      if (response.status === 200) {
        // Update the active mods list
        if (active) {
          setActiveMods((prev) => [...prev, response.data]);
        } else {
          setActiveMods((prev) => prev.filter((mod) => mod.id !== modId));
        }
      }
    } catch (error) {
      console.error("Error toggling mod:", error);
      setErrors((prev) => ({
        ...prev,
        general: `Failed to ${active ? "activate" : "deactivate"} mod`,
      }));
    }
  }, []);

  // Update mod settings
  const updateModSettings = useCallback(async (modId, settings) => {
    try {
      const response = await axios.put(
        `${API_URL}/api/mods/${modId}/settings`,
        settings
      );

      if (response.status === 200) {
        // Update available mods with new settings
        setAvailableMods((prev) =>
          prev.map((mod) =>
            mod.id === modId ? { ...mod, settings: settings } : mod
          )
        );
      }
    } catch (error) {
      console.error("Error updating mod settings:", error);
      setErrors((prev) => ({
        ...prev,
        general: "Failed to update mod settings",
      }));
    }
  }, []);

  // Save user preferences
  const saveSettings = useCallback(async (newSettings) => {
    try {
      const response = await axios.put(`${API_URL}/api/settings`, newSettings);

      if (response.status === 200) {
        setSettings(newSettings);
      }
    } catch (error) {
      console.error("Error saving settings:", error);
      setErrors((prev) => ({ ...prev, general: "Failed to save settings" }));
    }
  }, []);

  // Initialize data on component mount
  useEffect(() => {
    fetchMods();
    fetchProcesses();
    fetchSystemStatus();

    // Set up periodic refresh
    const processInterval = setInterval(fetchProcesses, 5000);
    const statusInterval = setInterval(fetchSystemStatus, 5000);

    return () => {
      clearInterval(processInterval);
      clearInterval(statusInterval);
    };
  }, [fetchMods, fetchProcesses, fetchSystemStatus]);

  // Check for active mods on initial load
  useEffect(() => {
    const getActiveMods = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/mods/active`);
        setActiveMods(response.data);
      } catch (error) {
        console.error("Error fetching active mods:", error);
      }
    };

    getActiveMods();
  }, []);

  // Value object to be provided to consumers
  const contextValue = {
    activeMods,
    availableMods,
    processes,
    systemStatus,
    settings,
    loading,
    errors,
    toggleMod,
    updateModSettings,
    saveSettings,
    refreshMods: fetchMods,
    refreshProcesses: fetchProcesses,
    refreshSystemStatus: fetchSystemStatus,
  };

  return (
    <AppContext.Provider value={contextValue}>{children}</AppContext.Provider>
  );
};

export default AppProvider;
