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
import ErrorBoundary from "./components/errorboundary/ErrorBoundary";
import ConnectionError from "./components/connectionerror/ConnectionError";
import { useBackend } from "./context/BackendContext";

// App content with connection check
const AppContent = () => {
  const { isConnected, isChecking, error, reconnect } = useBackend();

  if (isChecking) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-white text-lg">
            Initializing ModHub Central...
          </p>
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        <div className="text-center p-8 max-w-md bg-gray-800 rounded-lg shadow-lg">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h1 className="text-xl font-bold text-white mb-4">
            Backend Connection Error
          </h1>
          <p className="text-gray-300 mb-6">
            {error ||
              "Unable to connect to the ModHub Central backend service. Please ensure the service is running."}
          </p>
          <button
            onClick={reconnect}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <Router>
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
      <ToastContainer
        position="bottom-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </Router>
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
