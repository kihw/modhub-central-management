import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { ThemeProvider } from '@mui/material/styles';

import App from './App';
import { store, persistor } from './redux/store';
import theme from './theme';
import './styles/index.css';

// Enable hot module replacement for development
if (process.env.NODE_ENV === 'development' && module.hot) {
  module.hot.accept();
}

// Create root element for React 18
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the application
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ThemeProvider theme={theme}>
          <Router>
            <App />
          </Router>
        </ThemeProvider>
      </PersistGate>
    </Provider>
  </React.StrictMode>
);

// Handle Electron-specific setup if running in Electron
if (window.electron) {
  window.electron.ipcRenderer.on('app-update', (event, message) => {
    console.log('Update event:', message);
    // Handle app updates here if needed
  });
}