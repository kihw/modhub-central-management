import { createSlice } from '@reduxjs/toolkit';

const loadThemePreference = () => {
  const savedTheme = localStorage.getItem('themePreference');
  
  if (savedTheme) {
    return savedTheme;
  }
  
  // Check system preference if no saved preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  
  return 'light';
};

const applyTheme = (theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  localStorage.setItem('themePreference', theme);
};

const initialState = {
  currentTheme: loadThemePreference(),
  availableThemes: ['light', 'dark', 'system'],
  accentColor: '#3B82F6', // Default blue accent color
};

// Apply the initial theme when the slice is first loaded
applyTheme(initialState.currentTheme);

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.currentTheme = action.payload;
      applyTheme(action.payload);
    },
    toggleTheme: (state) => {
      const newTheme = state.currentTheme === 'dark' ? 'light' : 'dark';
      state.currentTheme = newTheme;
      applyTheme(newTheme);
    },
    setAccentColor: (state, action) => {
      state.accentColor = action.payload;
      document.documentElement.style.setProperty('--accent-color', action.payload);
    },
    resetThemePreferences: (state) => {
      state.currentTheme = 'light';
      state.accentColor = '#3B82F6';
      applyTheme('light');
      document.documentElement.style.setProperty('--accent-color', '#3B82F6');
    }
  }
});

export const { setTheme, toggleTheme, setAccentColor, resetThemePreferences } = themeSlice.actions;

export default themeSlice.reducer;