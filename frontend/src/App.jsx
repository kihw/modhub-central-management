import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

// Layout components
import MainLayout from './components/layouts/MainLayout';
import Sidebar from '@/components/sidebar/Sidebar.jsx';

// Pages
import Dashboard from './pages/Dashboard';
import ModsManager from './pages/ModsManager';
import RulesEditor from './pages/RulesEditor';
import Settings from './pages/Settings';
import ModDetail from './pages/ModDetail';
import ActivityMonitor from './pages/ActivityMonitor';

// Context
import { AppStateProvider } from './context/AppStateContext';
import { ThemeProvider } from './context/ThemeContext';
import { ApiProvider } from './context/ApiContext';

const App = () => {
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check connection to backend on startup
    const checkBackendConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health');
        if (response.ok) {
          setIsBackendConnected(true);
        }
      } catch (error) {
        console.error('Backend connection error:', error);
        setIsBackendConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkBackendConnection();
    
    // Periodically check backend connection
    const intervalId = setInterval(checkBackendConnection, 30000);
    
    return () => clearInterval(intervalId);
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-white text-lg">Initializing ModHub Central...</p>
        </div>
      </div>
    );
  }

  if (!isBackendConnected) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900">
        <div className="text-center p-8 max-w-md bg-gray-800 rounded-lg shadow-lg">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h1 className="text-xl font-bold text-white mb-4">Backend Connection Error</h1>
          <p className="text-gray-300 mb-6">
            Unable to connect to the ModHub Central backend service. Please ensure the service is running.
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <ApiProvider>
      <ThemeProvider>
        <AppStateProvider>
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
        </AppStateProvider>
      </ThemeProvider>
    </ApiProvider>
  );
};

export default App;