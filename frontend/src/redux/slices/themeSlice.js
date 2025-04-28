import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  mode: 'system', // 'light', 'dark', 'system'
  systemPreference: 'light', // determined by system
  accentColor: '#3B82F6', // blue-500 default
  fontSize: 'medium', // 'small', 'medium', 'large'
  animations: true,
  reducedMotion: false,
  borderRadius: 'medium', // 'none', 'small', 'medium', 'large'
  density: 'comfortable', // 'compact', 'comfortable', 'spacious'
  customColors: {
    primary: '#3B82F6',
    secondary: '#10B981',
    success: '#22C55E',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#0EA5E9'
  },
  customTheme: null
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setThemeMode: (state, action) => {
      state.mode = action.payload;
    },
    
    setSystemPreference: (state, action) => {
      state.systemPreference = action.payload;
    },
    
    setAccentColor: (state, action) => {
      state.accentColor = action.payload;
    },
    
    setFontSize: (state, action) => {
      state.fontSize = action.payload;
    },
    
    toggleAnimations: (state) => {
      state.animations = !state.animations;
    },
    
    setReducedMotion: (state, action) => {
      state.reducedMotion = action.payload;
    },
    
    setBorderRadius: (state, action) => {
      state.borderRadius = action.payload;
    },
    
    setDensity: (state, action) => {
      state.density = action.payload;
    },
    
    updateCustomColor: (state, action) => {
      const { key, value } = action.payload;
      if (state.customColors.hasOwnProperty(key)) {
        state.customColors[key] = value;
      }
    },
    
    setCustomTheme: (state, action) => {
      state.customTheme = action.payload;
    },
    
    resetTheme: (state) => {
      return initialState;
    }
  }
});

// Selectors
export const selectThemeMode = (state) => {
  return state.theme.mode === 'system' 
    ? state.theme.systemPreference 
    : state.theme.mode;
};

export const selectAccentColor = (state) => state.theme.accentColor;
export const selectFontSize = (state) => state.theme.fontSize;
export const selectAnimations = (state) => state.theme.animations;
export const selectReducedMotion = (state) => state.theme.reducedMotion;
export const selectBorderRadius = (state) => state.theme.borderRadius;
export const selectDensity = (state) => state.theme.density;
export const selectCustomColors = (state) => state.theme.customColors;
export const selectCustomTheme = (state) => state.theme.customTheme;
export const selectRawThemeMode = (state) => state.theme.mode;
export const selectSystemPreference = (state) => state.theme.systemPreference;

export const {
  setThemeMode,
  setSystemPreference,
  setAccentColor,
  setFontSize,
  toggleAnimations,
  setReducedMotion,
  setBorderRadius,
  setDensity,
  updateCustomColor,
  setCustomTheme,
  resetTheme
} = themeSlice.actions;

export default themeSlice.reducer;