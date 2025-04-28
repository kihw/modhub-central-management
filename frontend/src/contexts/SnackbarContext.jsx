import React, { createContext, useContext, useState, useCallback } from 'react';
import { Snackbar, Alert } from '@mui/material';

// Création du contexte
const SnackbarContext = createContext();

// Types de notifications
export const SNACKBAR_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Provider du contexte
export const SnackbarProvider = ({ children }) => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [type, setType] = useState(SNACKBAR_TYPES.INFO);
  const [autoHideDuration, setAutoHideDuration] = useState(6000);

  const showSnackbar = useCallback((message, type = SNACKBAR_TYPES.INFO, duration = 6000) => {
    setMessage(message);
    setType(type);
    setAutoHideDuration(duration);
    setOpen(true);
  }, []);

  const hideSnackbar = useCallback(() => {
    setOpen(false);
  }, []);

  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    hideSnackbar();
  };

  // Fonctions d'aide pour différents types de notifications
  const showSuccess = useCallback((message, duration) => 
    showSnackbar(message, SNACKBAR_TYPES.SUCCESS, duration), [showSnackbar]);
    
  const showError = useCallback((message, duration) => 
    showSnackbar(message, SNACKBAR_TYPES.ERROR, duration), [showSnackbar]);
    
  const showWarning = useCallback((message, duration) => 
    showSnackbar(message, SNACKBAR_TYPES.WARNING, duration), [showSnackbar]);
    
  const showInfo = useCallback((message, duration) => 
    showSnackbar(message, SNACKBAR_TYPES.INFO, duration), [showSnackbar]);

  const value = {
    showSnackbar,
    hideSnackbar,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <Snackbar
        open={open}
        autoHideDuration={autoHideDuration}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleClose} severity={type} variant="filled" sx={{ width: '100%' }}>
          {message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
};

// Hook personnalisé pour utiliser le contexte Snackbar
export const useSnackbar = () => {
  const context = useContext(SnackbarContext);
  if (!context) {
    throw new Error('useSnackbar doit être utilisé à l'intérieur d'un SnackbarProvider');
  }
  return context;
};

// Export par défaut
export default SnackbarContext;