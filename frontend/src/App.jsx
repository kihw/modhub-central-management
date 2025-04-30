import React, { Suspense, useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { store, persistor } from "./redux/store";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./styles/App.css";

// Context providers
import { BackendProvider, useBackend } from "./context/BackendContext";

// Components
import MainLayout from "./components/layouts/MainLayout";
import Sidebar from "./components/sidebar/Sidebar";
import ErrorBoundary from "./components/ErrorBoundary";
import ConnectionError from "./components/ConnectionError";
import Loading from "./components/Loading";
import KeyedRender from "./components/KeyedRender";
import ConnectivityChecker from "./components/ConnectivityChecker";

// Lazily load pages for better performance
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const ModsManager = React.lazy(() => import("./pages/ModsManager"));
const RulesEditor = React.lazy(() => import("./pages/RulesEditor"));
const Settings = React.lazy(() => import("./pages/Settings"));
const ModDetail = React.lazy(() => import("./pages/ModDetail"));
const ActivityMonitor = React.lazy(() => import("./pages/ActivityMonitor"));

// Fallback for lazy loaded routes
const PageLoading = () => (
  <div className="flex h-full w-full items-center justify-center">
    <Loading text="Chargement de la page..." fullScreen={false} />
  </div>
);

// App content with connection check
const AppContent = () => {
  const { isConnected, isChecking, error, reconnect } = useBackend();
  const [showConnectivityDetails, setShowConnectivityDetails] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);

  // Handle backend connectivity events
  const handleConnectivityChange = (isConnected, details) => {
    if (isConnected) {
      if (connectionAttempts > 0) {
        toast.success("Connexion au serveur backend rétablie !", {
          position: "bottom-right",
          autoClose: 3000,
        });
      }
      setConnectionAttempts(0);
    } else {
      setConnectionAttempts(prev => prev + 1);
      
      // Show notification after failed connection
      toast.error(
        `Problème de connexion au serveur backend. ${
          details?.error ? `Erreur: ${details.error}` : ""
        }`,
        {
          position: "bottom-right",
          autoClose: 5000,
        }
      );
    }
  };

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
          
          <div className="mt-4">
            <ConnectivityChecker 
              checkInterval={5000} 
              onStatusChange={handleConnectivityChange}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <MainLayout>
      <Sidebar />
      <div className="content-container flex-1 overflow-auto">
        {/* Backend connectivity mini indicator */}
        <div 
          className="fixed top-2 right-2 z-50 cursor-pointer"
          onClick={() => setShowConnectivityDetails(!showConnectivityDetails)}
        >
          <ConnectivityChecker 
            showMiniDisplay={!showConnectivityDetails} 
            checkInterval={30000}
            onStatusChange={handleConnectivityChange}
            className="bg-white/80 dark:bg-gray-800/80 rounded-full p-1 shadow-md"
          />
        </div>
        
        {/* Detailed connectivity panel - shown when clicked */}
        {showConnectivityDetails && (
          <div className="fixed top-10 right-2 z-50 w-64 shadow-lg animate-fadeIn">
            <div className="flex justify-between items-center p-2 bg-gray-200 dark:bg-gray-700 rounded-t-lg">
              <h3 className="text-sm font-medium">Statut du Backend</h3>
              <button 
                className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
                onClick={() => setShowConnectivityDetails(false)}
              >
                ×
              </button>
            </div>
            <ConnectivityChecker 
              checkInterval={30000}
              onStatusChange={handleConnectivityChange}
              className="rounded-t-none shadow-none"
            />
          </div>
        )}
        
        {/* Use Suspense for lazy loading */}
        <Suspense fallback={<PageLoading />}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route 
              path="/dashboard" 
              element={
                <ErrorBoundary>
                  <KeyedRender value="dashboard">
                    <Dashboard />
                  </KeyedRender>
                </ErrorBoundary>
              } 
            />
            <Route 
              path="/mods" 
              element={
                <ErrorBoundary>
                  <KeyedRender value="mods">
                    <ModsManager />
                  </KeyedRender>
                </ErrorBoundary>
              } 
            />
            <Route 
              path="/mods/:modId" 
              element={
                <ErrorBoundary>
                  <ModDetail />
                </ErrorBoundary>
              } 
            />
            <Route 
              path="/rules" 
              element={
                <ErrorBoundary>
                  <KeyedRender value="rules">
                    <RulesEditor />
                  </KeyedRender>
                </ErrorBoundary>
              } 
            />
            <Route 
              path="/activity" 
              element={
                <ErrorBoundary>
                  <KeyedRender value="activity">
                    <ActivityMonitor />
                  </KeyedRender>
                </ErrorBoundary>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ErrorBoundary>
                  <KeyedRender value="settings">
                    <Settings />
                  </KeyedRender>
                </ErrorBoundary>
              } 
            />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </div>
    </MainLayout>
  );
};

const App = () => {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <PersistGate loading={<Loading text="Chargement des données..." fullScreen={true} />} persistor={persistor}>
          <BackendProvider>
            <KeyedRender value="app-content">
              <AppContent />
            </KeyedRender>
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
              limit={3}
            />
          </BackendProvider>
        </PersistGate>
      </Provider>
    </ErrorBoundary>
  );
};

export default App;