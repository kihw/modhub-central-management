// Primary colors
const primary = {
  50: "#f0f9ff",
  100: "#e0f2fe",
  200: "#bae6fd",
  300: "#7dd3fc",
  400: "#38bdf8",
  500: "#0ea5e9",
  600: "#0284c7",
  700: "#0369a1",
  800: "#075985",
  900: "#0c4a6e",
  950: "#082f49",
};

// Neutral colors
const neutral = {
  50: "#f8fafc",
  100: "#f1f5f9",
  200: "#e2e8f0",
  300: "#cbd5e1",
  400: "#94a3b8",
  500: "#64748b",
  600: "#475569",
  700: "#334155",
  800: "#1e293b",
  900: "#0f172a",
  950: "#020617",
};

// Semantic colors
const semantic = {
  success: {
    light: "#86efac",
    default: "#22c55e",
    dark: "#15803d",
  },
  warning: {
    light: "#fde68a",
    default: "#f59e0b",
    dark: "#b45309",
  },
  error: {
    light: "#fca5a5",
    default: "#ef4444",
    dark: "#b91c1c",
  },
  info: {
    light: "#a5b4fc",
    default: "#6366f1",
    dark: "#4338ca",
  },
};

// Border colors
const border = {
  light: neutral[200],
  default: neutral[300],
  dark: neutral[400],
};

// Background colors
const background = {
  primary: "#ffffff",
  secondary: neutral[50],
  tertiary: neutral[100],
};

// Text colors
const text = {
  primary: neutral[900],
  secondary: neutral[600],
  tertiary: neutral[500],
  disabled: neutral[400],
  inverse: "#ffffff",
};

const colors = {
  primary,
  neutral,
  semantic,
  border,
  background,
  text,
};

export default colors;
