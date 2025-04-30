const colors = {
  primary: {
    light: '#6366f1',
    DEFAULT: '#4f46e5',
    dark: '#4338ca'
  },
  secondary: {
    light: '#a855f7',
    DEFAULT: '#9333ea',
    dark: '#7e22ce'
  },
  gaming: {
    light: '#f43f5e',
    DEFAULT: '#e11d48',
    dark: '#be123c'  
  },
  night: {
    light: '#3b82f6',
    DEFAULT: '#2563eb',
    dark: '#1d4ed8'
  },
  media: {
    light: '#10b981',
    DEFAULT: '#059669',
    dark: '#047857'
  },
  custom: {
    light: '#f59e0b',
    DEFAULT: '#d97706',
    dark: '#b45309'
  },
  state: {
    success: {
      light: '#22c55e',
      DEFAULT: '#16a34a', 
      dark: '#15803d'
    },
    warning: {
      light: '#f97316',
      DEFAULT: '#ea580c',
      dark: '#c2410c' 
    },
    error: {
      light: '#ef4444',
      DEFAULT: '#dc2626',
      dark: '#b91c1c'
    },
    info: {
      light: '#0ea5e9',
      DEFAULT: '#0284c7',
      dark: '#0369a1'
    }
  },
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
    950: '#030712'
  },
  theme: {
    background: {
      light: '#ffffff',
      DEFAULT: '#f9fafb',
      dark: '#111827'
    },
    text: {
      light: '#374151',
      muted: '#6b7280', 
      dark: '#f9fafb'
    },
    border: {
      light: '#e5e7eb',
      DEFAULT: '#d1d5db',
      dark: '#4b5563'
    }
  },
  opacity: {
    light: 0.7,
    medium: 0.5,
    heavy: 0.3
  }
} as const;

export type ColorTheme = typeof colors;
export default colors;