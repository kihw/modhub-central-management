import React, { createContext, useContext, useState, useEffect } from 'react';

// Création du contexte d'authentification
const AuthContext = createContext(null);

// Hook personnalisé pour utiliser le contexte d'authentification
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Vérifier si l'utilisateur est déjà connecté au chargement
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // Fonction de connexion
  const login = async (credentials) => {
    try {
      // Cette partie serait normalement remplacée par une véritable requête API
      // Exemple fictif
      const response = await mockLoginAPI(credentials);
      
      // Stocker l'utilisateur dans localStorage et state
      localStorage.setItem('user', JSON.stringify(response.user));
      setUser(response.user);
      return response.user;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  // Fonction de déconnexion
  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  // Mock d'API pour la démonstration
  // À remplacer par une vraie requête à votre API
  const mockLoginAPI = async (credentials) => {
    return new Promise((resolve, reject) => {
      // Simuler une requête API
      setTimeout(() => {
        if (credentials.email && credentials.password) {
          resolve({
            user: {
              id: '1',
              name: 'John Doe',
              email: credentials.email,
            },
            token: 'fake-jwt-token'
          });
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 500);
    });
  };

  // Valeur fournie par le contexte
  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};