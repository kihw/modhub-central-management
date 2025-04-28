/**
 * ModHub Central - Palette de couleurs
 * 
 * Ce fichier définit les couleurs principales utilisées dans l'application
 * avec des variantes sombres et claires pour les différents thèmes.
 */

const colors = {
  // Couleurs de base
  primary: {
    light: '#6366f1', // Indigo plus clair
    DEFAULT: '#4f46e5', // Indigo principal
    dark: '#4338ca', // Indigo plus foncé
  },
  
  // Couleurs secondaires
  secondary: {
    light: '#a855f7', // Violet clair
    DEFAULT: '#9333ea', // Violet principal
    dark: '#7e22ce', // Violet foncé
  },
  
  // Couleurs pour Gaming Mod
  gaming: {
    light: '#f43f5e', // Rose vif
    DEFAULT: '#e11d48', // Rouge gaming
    dark: '#be123c', // Rouge foncé
  },
  
  // Couleurs pour Night Mod
  night: {
    light: '#3b82f6', // Bleu nuit clair
    DEFAULT: '#2563eb', // Bleu nuit
    dark: '#1d4ed8', // Bleu nuit foncé
  },
  
  // Couleurs pour Media Mod
  media: {
    light: '#10b981', // Vert média clair
    DEFAULT: '#059669', // Vert média
    dark: '#047857', // Vert média foncé
  },
  
  // Couleurs pour Custom Mods
  custom: {
    light: '#f59e0b', // Jaune/orange clair
    DEFAULT: '#d97706', // Jaune/orange
    dark: '#b45309', // Jaune/orange foncé
  },
  
  // Couleurs de notification/statut
  success: {
    light: '#22c55e',
    DEFAULT: '#16a34a',
    dark: '#15803d',
  },
  
  warning: {
    light: '#f97316',
    DEFAULT: '#ea580c',
    dark: '#c2410c',
  },
  
  error: {
    light: '#ef4444',
    DEFAULT: '#dc2626',
    dark: '#b91c1c',
  },
  
  info: {
    light: '#0ea5e9',
    DEFAULT: '#0284c7',
    dark: '#0369a1',
  },
  
  // Nuances de gris pour l'interface
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },
  
  // Couleurs de fond
  background: {
    light: '#ffffff',
    DEFAULT: '#f9fafb',
    dark: '#111827',
  },
  
  // Couleurs de texte
  text: {
    light: '#374151',
    muted: '#6b7280',
    dark: '#f9fafb',
  },
  
  // Couleurs pour les bordures
  border: {
    light: '#e5e7eb',
    DEFAULT: '#d1d5db',
    dark: '#4b5563',
  },
  
  // Niveau de transparence
  opacity: {
    light: 0.7,
    medium: 0.5,
    heavy: 0.3,
  }
};

export default colors;