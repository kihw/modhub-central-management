import React, { Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { store, persistor } from "./redux/store";
import { ToastContainer } from "react-toastify";
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