import { createSlice } from '@reduxjs/toolkit';

const THEME_STORAGE_KEY = 'themePreference';
const ACCENT_COLOR_STORAGE_KEY = 'accentColor';
const DEFAULT_ACCENT_COLOR = '#3B82F6';
const SYSTEM_DARK_MEDIA_QUERY = '(prefers-color-scheme: dark)';
const VALID_THEMES = ['light', 'dark', 'system'];
const HEX_COLOR_REGEX = /^#[0-9A-F]{6}$/i;

const loadThemePreference = () => {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  if (savedTheme && VALID_THEMES.includes(savedTheme)) return savedTheme;
  return window.matchMedia?.(SYSTEM_DARK_MEDIA_QUERY).matches ? 'dark' : 'light';
};

const loadAccentColor = () => {
  const savedColor = localStorage.getItem(ACCENT_COLOR_STORAGE_KEY);
  return HEX_COLOR_REGEX.test(savedColor) ? savedColor : DEFAULT_ACCENT_COLOR;
};

const applyTheme = (theme) => {
  if (!VALID_THEMES.includes(theme)) return;
  const isDark = theme === 'system' 
    ? window.matchMedia(SYSTEM_DARK_MEDIA_QUERY).matches 
    : theme === 'dark';
  document.documentElement.classList.toggle('dark', isDark);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
};

const applyAccentColor = (color) => {
  if (!HEX_COLOR_REGEX.test(color)) return;
  document.documentElement.style.setProperty('--accent-color', color);
  localStorage.setItem(ACCENT_COLOR_STORAGE_KEY, color);
};

const initialState = {
  currentTheme: loadThemePreference(),
  availableThemes: VALID_THEMES,
  accentColor: loadAccentColor(),
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setTheme: (state, action) => {
      const newTheme = action.payload;
      if (!VALID_THEMES.includes(newTheme)) return;
      state.currentTheme = newTheme;
      applyTheme(newTheme);
    },
    toggleTheme: (state) => {
      const currentIndex = VALID_THEMES.indexOf(state.currentTheme);
      const newTheme = VALID_THEMES[(currentIndex + 1) % VALID_THEMES.length];
      state.currentTheme = newTheme;
      applyTheme(newTheme);
    },
    setAccentColor: (state, action) => {
      const newColor = action.payload;
      if (!HEX_COLOR_REGEX.test(newColor)) return;
      state.accentColor = newColor;
      applyAccentColor(newColor);
    },
    resetThemePreferences: (state) => {
      state.currentTheme = 'light';
      state.accentColor = DEFAULT_ACCENT_COLOR;
      applyTheme('light');
      applyAccentColor(DEFAULT_ACCENT_COLOR);
    }
  }
});

const systemThemeMediaQuery = window.matchMedia(SYSTEM_DARK_MEDIA_QUERY);
systemThemeMediaQuery.addEventListener('change', (e) => {
  if (initialState.currentTheme === 'system') {
    applyTheme('system');
  }
});

applyTheme(initialState.currentTheme);
applyAccentColor(initialState.accentColor);

export const { setTheme, toggleTheme, setAccentColor, resetThemePreferences } = themeSlice.actions;
export default themeSlice.reducer;