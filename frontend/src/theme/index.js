import { createTheme, responsiveFontSizes } from "@mui/material/styles";

const baseColors = {
  primary: { main: "#3f51b5", light: "#757de8", dark: "#002984", contrastText: "#fff" },
  secondary: { main: "#f50057", light: "#ff4081", dark: "#c51162", contrastText: "#fff" },
  success: { main: "#4caf50", light: "#80e27e", dark: "#087f23", contrastText: "#fff" },
  warning: { main: "#ff9800", light: "#ffc947", dark: "#c66900", contrastText: "rgba(0,0,0,0.87)" },
  error: { main: "#f44336", light: "#ff7961", dark: "#ba000d", contrastText: "#fff" },
  info: { main: "#2196f3", light: "#64b5f6", dark: "#0069c0", contrastText: "#fff" }
};

const lightColors = {
  ...baseColors,
  text: {
    primary: "rgba(0,0,0,0.87)",
    secondary: "rgba(0,0,0,0.6)",
    disabled: "rgba(0,0,0,0.38)"
  },
  background: {
    default: "#f5f5f5",
    paper: "#fff"
  },
  divider: "rgba(0,0,0,0.12)"
};

const darkColors = {
  ...baseColors,
  text: {
    primary: "#fff",
    secondary: "rgba(255,255,255,0.7)",
    disabled: "rgba(255,255,255,0.5)"
  },
  background: {
    default: "#121212",
    paper: "#1e1e1e"
  },
  divider: "rgba(255,255,255,0.12)"
};

const typography = {
  fontFamily: [
    "Inter",
    "-apple-system",
    "BlinkMacSystemFont",
    '"Segoe UI"',
    "Roboto",
    '"Helvetica Neue"',
    "Arial",
    "sans-serif",
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"'
  ].join(","),
  h1: { fontWeight: 700, fontSize: "2.5rem", lineHeight: 1.2 },
  h2: { fontWeight: 600, fontSize: "2rem", lineHeight: 1.3 },
  h3: { fontWeight: 600, fontSize: "1.75rem", lineHeight: 1.3 },
  h4: { fontWeight: 500, fontSize: "1.5rem", lineHeight: 1.4 },
  h5: { fontWeight: 500, fontSize: "1.25rem", lineHeight: 1.4 },
  h6: { fontWeight: 500, fontSize: "1rem", lineHeight: 1.5 },
  subtitle1: { fontSize: "1rem", lineHeight: 1.5 },
  subtitle2: { fontSize: "0.875rem", fontWeight: 500, lineHeight: 1.57 },
  body1: { fontSize: "1rem", lineHeight: 1.5 },
  body2: { fontSize: "0.875rem", lineHeight: 1.57 },
  button: { fontSize: "0.875rem", fontWeight: 500, textTransform: "none", lineHeight: 1.75 },
  caption: { fontSize: "0.75rem", lineHeight: 1.66 },
  overline: { fontSize: "0.75rem", textTransform: "uppercase", lineHeight: 2.66 }
};

const commonComponents = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: "8px 16px",
        transition: "all 0.2s"
      },
      containedPrimary: {
        boxShadow: "0 4px 6px rgba(63,81,181,0.25)",
        "&:hover": {
          boxShadow: "0 6px 10px rgba(63,81,181,0.35)"
        }
      },
      containedSecondary: {
        boxShadow: "0 4px 6px rgba(245,0,87,0.25)",
        "&:hover": {
          boxShadow: "0 6px 10px rgba(245,0,87,0.35)"
        }
      }
    }
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        transition: "box-shadow 0.3s"
      }
    }
  },
  MuiCardHeader: {
    styleOverrides: {
      root: { padding: 24 }
    }
  },
  MuiCardContent: {
    styleOverrides: {
      root: {
        padding: 24,
        "&:last-child": { paddingBottom: 24 }
      }
    }
  },
  MuiPaper: {
    styleOverrides: {
      rounded: { borderRadius: 12 }
    }
  },
  MuiTableCell: {
    styleOverrides: {
      head: { fontWeight: 600 }
    }
  }
};

const lightComponents = {
  ...commonComponents,
  MuiCard: {
    styleOverrides: {
      root: {
        ...commonComponents.MuiCard.styleOverrides.root,
        boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
      }
    }
  },
  MuiPaper: {
    styleOverrides: {
      ...commonComponents.MuiPaper.styleOverrides,
      elevation1: { boxShadow: "0 2px 12px rgba(0,0,0,0.08)" }
    }
  }
};

const darkComponents = {
  ...commonComponents,
  MuiCard: {
    styleOverrides: {
      root: {
        ...commonComponents.MuiCard.styleOverrides.root,
        boxShadow: "0 2px 12px rgba(0,0,0,0.2)",
        backgroundColor: "#1e1e1e"
      }
    }
  },
  MuiPaper: {
    styleOverrides: {
      ...commonComponents.MuiPaper.styleOverrides,
      elevation1: { boxShadow: "0 2px 12px rgba(0,0,0,0.2)" }
    }
  }
};

const shadows = [
  "none",
  ...Array(24).fill(null).map((_, i) => {
    const y = Math.floor((i + 1) / 3) + 1;
    const blur = (i + 1) * 2;
    const alpha = ((i + 1) / 24 * 0.2).toFixed(2);
    return `0 ${y}px ${blur}px rgba(0,0,0,${alpha})`;
  })
];

const baseThemeOptions = {
  typography,
  shape: { borderRadius: 8 }
};

const lightTheme = responsiveFontSizes(createTheme({
  ...baseThemeOptions,
  palette: { mode: "light", ...lightColors },
  components: lightComponents,
  shadows
}));

const darkTheme = responsiveFontSizes(createTheme({
  ...baseThemeOptions,
  palette: { mode: "dark", ...darkColors },
  components: darkComponents,
  shadows
}));

export { lightTheme, darkTheme };
export default { light: lightTheme, dark: darkTheme };