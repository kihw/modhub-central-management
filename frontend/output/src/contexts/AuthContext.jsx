import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Initialiser l'état d'authentification au chargement
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        
        if (decoded.exp && decoded.exp > currentTime) {
          setCurrentUser(decoded);
        } else {
          // Token expiré
          localStorage.removeItem('token');
          setCurrentUser(null);
        }
      } catch (err) {
        console.error('Token invalide:', err);
        localStorage.removeItem('token');
        setError('Session invalide, veuillez vous reconnecter.');
      }
    }
    setLoading(false);
  }, []);

  // Fonction de connexion
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      // Exemple d'appel API - à remplacer par votre endpoint réel
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      
      if (!response.ok) {
        throw new Error('Échec de la connexion');
      }
      
      const data = await response.json();
      localStorage.setItem('token', data.token);
      
      const decoded = jwtDecode(data.token);
      setCurrentUser(decoded);
      return true;
    } catch (err) {
      setError(err.message || 'Échec de la connexion. Vérifiez vos identifiants.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Fonction de déconnexion
  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
  };

  // Fonction d'inscription
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      // Exemple d'appel API - à remplacer par votre endpoint réel
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Échec de l\'inscription');
      }
      
      return true;
    } catch (err) {
      setError(err.message || 'Échec de l\'inscription. Veuillez réessayer.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Vérification si l'utilisateur est authentifié
  const isAuthenticated = () => {
    return !!currentUser;
  };

  // Récupération du token pour les requêtes API
  const getAuthToken = () => {
    return localStorage.getItem('token');
  };

  // Vérification des permissions de l'utilisateur
  const hasPermission = (permission) => {
    if (!currentUser || !currentUser.permissions) return false;
    return currentUser.permissions.includes(permission);
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    logout,
    register,
    isAuthenticated,
    getAuthToken,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé à l\'intérieur d\'un AuthProvider');
  }
  return context;
};

export default AuthContext;