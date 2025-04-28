import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { store, persistor } from "./redux/store";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./styles/App.css";

// Context providers
import { BackendProvider } from "./context/BackendContext";

// Layout components
import MainLayout from "./components/layouts/MainLayout";
import Sidebar from "./components/sidebar/Sidebar";

// Pages
import Dashboard from "./pages/Dashboard";
import ModsManager from "./pages/ModsManager";
import RulesEditor from "./pages/RulesEditor";
import Settings from "./pages/Settings";
import ModDetail from "./pages/ModDetail";
import ActivityMonitor from "./pages/ActivityMonitor";
import ErrorBoundary from "./components/ErrorBoundary";
import ConnectionError from "./components/ConnectionError";
import { useBackend } from "./context/BackendContext";

// App content with connection check

const AppContent = () => {
  const { isConnected, isChecking, error, reconnect } = useBackend();

  if (isChecking) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        {/* loading spinner */}
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        {/* backend not connected screen */}
      </div>
    );
  }

  return (
    <MainLayout>
      <Sidebar />
      <div className="content-container flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/mods" element={<ModsManager />} />
          <Route path="/mods/:modId" element={<ModDetail />} />
          <Route path="/rules" element={<RulesEditor />} />
          <Route path="/activity" element={<ActivityMonitor />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </MainLayout>
  );
};

const App = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ErrorBoundary>
          <BackendProvider>
            <AppContent />
          </BackendProvider>
        </ErrorBoundary>
      </PersistGate>
    </Provider>
  );
};

export default App;
