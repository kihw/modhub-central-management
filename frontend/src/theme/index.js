import colors from "./colors";
import fonts from "./fonts";

// Spacing system
const spacing = {
  0: "0",
  px: "1px",
  0.5: "0.125rem",
  1: "0.25rem",
  1.5: "0.375rem",
  2: "0.5rem",
  2.5: "0.625rem",
  3: "0.75rem",
  3.5: "0.875rem",
  4: "1rem",
  5: "1.25rem",
  6: "1.5rem",
  7: "1.75rem",
  8: "2rem",
  9: "2.25rem",
  10: "2.5rem",
  11: "2.75rem",
  12: "3rem",
  14: "3.5rem",
  16: "4rem",
  20: "5rem",
  24: "6rem",
  28: "7rem",
  32: "8rem",
  36: "9rem",
  40: "10rem",
  44: "11rem",
  48: "12rem",
  52: "13rem",
  56: "14rem",
  60: "15rem",
  64: "16rem",
  72: "18rem",
  80: "20rem",
  96: "24rem",
};

// Breakpoints
const breakpoints = {
  xs: "320px",
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
};

// Shadows
const shadows = {
  xs: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
  sm: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
  md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
  lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
  xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
  "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
  inner: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",
  none: "none",
};

// Borders
const borders = {
  radius: {
    none: "0",
    sm: "0.125rem",
    md: "0.25rem",
    lg: "0.375rem",
    xl: "0.5rem",
    "2xl": "0.75rem",
    "3xl": "1rem",
    full: "9999px",
  },
  width: {
    0: "0px",
    1: "1px",
    2: "2px",
    4: "4px",
    8: "8px",
  },
};

// Z-index values
const zIndices = {
  0: "0",
  10: "10",
  20: "20",
  30: "30",
  40: "40",
  50: "50",
  auto: "auto",
  dropdown: "1000",
  sticky: "1020",
  fixed: "1030",
  modalBackdrop: "1040",
  modal: "1050",
  popover: "1060",
  tooltip: "1070",
};

// Transitions
const transitions = {
  duration: {
    75: "75ms",
    100: "100ms",
    150: "150ms",
    200: "200ms",
    300: "300ms",
    500: "500ms",
    700: "700ms",
    1000: "1000ms",
  },
  easing: {
    linear: "linear",
    in: "cubic-bezier(0.4, 0, 1, 1)",
    out: "cubic-bezier(0, 0, 0.2, 1)",
    inOut: "cubic-bezier(0.4, 0, 0.2, 1)",
  },
};

// Component-specific theme values
const components = {
  button: {
    sizes: {
      xs: {
        height: "1.5rem",
        fontSize: fonts.sizes.xs,
        padding: `0 ${spacing[2.5]}`,
        borderRadius: borders.radius.md,
      },
      sm: {
        height: "2rem",
        fontSize: fonts.sizes.sm,
        padding: `0 ${spacing[3]}`,
        borderRadius: borders.radius.md,
      },
      md: {
        height: "2.5rem",
        fontSize: fonts.sizes.base,
        padding: `0 ${spacing[4]}`,
        borderRadius: borders.radius.md,
      },
      lg: {
        height: "3rem",
        fontSize: fonts.sizes.lg,
        padding: `0 ${spacing[6]}`,
        borderRadius: borders.radius.lg,
      },
      xl: {
        height: "3.5rem",
        fontSize: fonts.sizes.xl,
        padding: `0 ${spacing[8]}`,
        borderRadius: borders.radius.xl,
      },
    },
  },
  input: {
    sizes: {
      sm: {
        height: "2rem",
        fontSize: fonts.sizes.sm,
        padding: `0 ${spacing[3]}`,
        borderRadius: borders.radius.md,
      },
      md: {
        height: "2.5rem",
        fontSize: fonts.sizes.base,
        padding: `0 ${spacing[4]}`,
        borderRadius: borders.radius.md,
      },
      lg: {
        height: "3rem",
        fontSize: fonts.sizes.lg,
        padding: `0 ${spacing[5]}`,
        borderRadius: borders.radius.md,
      },
    },
  },
};

// Main theme object
const theme = {
  colors,
  fonts,
  spacing,
  breakpoints,
  shadows,
  borders,
  zIndices,
  transitions,
  components,
};

// Helper functions
export const getColor = (path) => {
  if (!path) return undefined;

  const parts = path.split(".");
  let result = theme.colors;

  for (const part of parts) {
    if (!result[part]) return undefined;
    result = result[part];
  }

  return result;
};

export const getSpacing = (value) => {
  return theme.spacing[value] || value;
};

export const getFontSize = (size) => {
  return theme.fonts.sizes[size] || size;
};

export const getTypographyStyle = (variant) => {
  return theme.fonts.variants[variant] || {};
};

export default theme;
