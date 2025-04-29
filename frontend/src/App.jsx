import React from "react";

import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { store, persistor } from "./redux/store";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./styles/App.css";

// Context providers
import { BackendProvider, useBackend } from "./context/BackendContext";

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
import Loading from "./components/Loading";

// App content with connection check
const AppContent = () => {
  const { isConnected, isChecking, error, reconnect } = useBackend();

  if (isChecking) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        <Loading text="Connexion au serveur backend..." fullScreen={true} />
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900 p-4">
        <div className="max-w-2xl w-full">
          <ConnectionError
            message="Impossible de se connecter au service backend"
            details="Le serveur backend n'est pas accessible. Veuillez vérifier que le script 'run.py' est en cours d'exécution."
            onRetry={reconnect}
            error={error}
          />
        </div>
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
            />
          </BackendProvider>
        </ErrorBoundary>
      </PersistGate>
    </Provider>
  );
};

export default App;
