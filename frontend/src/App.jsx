import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Mods from "./pages/Mods";
import Automation from "./pages/Automation";
import Logs from "./pages/Logs";
import Settings from "./pages/Settings";
import { useSettingsStore } from "./store/settingsStore";
import { useBackendStatus } from "./hooks/useBackendStatus";
import ConnectionError from "./components/ConnectionError";
import Loading from "./components/Loading";

function App() {
  const { darkMode } = useSettingsStore();
  const { isConnected, loading } = useBackendStatus();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Apply dark mode class to document
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    // Set initialization after a short delay to prevent flash
    const timer = setTimeout(() => {
      setIsInitialized(true);
    }, 500);

    return () => clearTimeout(timer);
  }, [darkMode]);

  if (!isInitialized || loading) {
    return <Loading />;
  }

  if (!isConnected) {
    return <ConnectionError />;
  }

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-factorio-darker text-gray-900 dark:text-gray-100">
      <Sidebar />
      <div className="flex-1 overflow-hidden">
        <main className="h-full overflow-y-auto p-4">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/mods" element={<Mods />} />
            <Route path="/automation" element={<Automation />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
