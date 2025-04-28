const fontWeights = {
  thin: "100",
  extralight: "200",
  light: "300",
  normal: "400",
  medium: "500",
  semibold: "600",
  bold: "700",
  extrabold: "800",
  black: "900",
};

const fontSizes = {
  xs: "0.75rem", // 12px
  sm: "0.875rem", // 14px
  base: "1rem", // 16px
  lg: "1.125rem", // 18px
  xl: "1.25rem", // 20px
  "2xl": "1.5rem", // 24px
  "3xl": "1.875rem", // 30px
  "4xl": "2.25rem", // 36px
  "5xl": "3rem", // 48px
  "6xl": "3.75rem", // 60px
  "7xl": "4.5rem", // 72px
  "8xl": "6rem", // 96px
  "9xl": "8rem", // 128px
};

const lineHeights = {
  none: "1",
  tight: "1.25",
  snug: "1.375",
  normal: "1.5",
  relaxed: "1.625",
  loose: "2",
};

const letterSpacings = {
  tighter: "-0.05em",
  tight: "-0.025em",
  normal: "0",
  wide: "0.025em",
  wider: "0.05em",
  widest: "0.1em",
};

const fontFamilies = {
  sans: [
    "Inter",
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "BlinkMacSystemFont",
    '"Segoe UI"',
    "Roboto",
    '"Helvetica Neue"',
    "Arial",
    '"Noto Sans"',
    "sans-serif",
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"',
    '"Noto Color Emoji"',
  ].join(","),
  serif: [
    "ui-serif",
    "Georgia",
    "Cambria",
    '"Times New Roman"',
    "Times",
    "serif",
  ].join(","),
  mono: [
    "ui-monospace",
    "SFMono-Regular",
    "Menlo",
    "Monaco",
    "Consolas",
    '"Liberation Mono"',
    '"Courier New"',
    "monospace",
  ].join(","),
};

const typographyVariants = {
  h1: {
    fontFamily: "sans",
    fontSize: "4xl",
    fontWeight: "bold",
    lineHeight: "tight",
    letterSpacing: "tight",
  },
  h2: {
    fontFamily: "sans",
    fontSize: "3xl",
    fontWeight: "bold",
    lineHeight: "tight",
    letterSpacing: "tight",
  },
  h3: {
    fontFamily: "sans",
    fontSize: "2xl",
    fontWeight: "semibold",
    lineHeight: "tight",
    letterSpacing: "normal",
  },
  h4: {
    fontFamily: "sans",
    fontSize: "xl",
    fontWeight: "semibold",
    lineHeight: "tight",
    letterSpacing: "normal",
  },
  h5: {
    fontFamily: "sans",
    fontSize: "lg",
    fontWeight: "semibold",
    lineHeight: "tight",
    letterSpacing: "normal",
  },
  h6: {
    fontFamily: "sans",
    fontSize: "base",
    fontWeight: "semibold",
    lineHeight: "tight",
    letterSpacing: "normal",
  },
  body1: {
    fontFamily: "sans",
    fontSize: "base",
    fontWeight: "normal",
    lineHeight: "normal",
    letterSpacing: "normal",
  },
  body2: {
    fontFamily: "sans",
    fontSize: "sm",
    fontWeight: "normal",
    lineHeight: "normal",
    letterSpacing: "normal",
  },
  caption: {
    fontFamily: "sans",
    fontSize: "xs",
    fontWeight: "normal",
    lineHeight: "normal",
    letterSpacing: "normal",
  },
  button: {
    fontFamily: "sans",
    fontSize: "sm",
    fontWeight: "medium",
    lineHeight: "none",
    letterSpacing: "wide",
  },
};

const fonts = {
  weights: fontWeights,
  sizes: fontSizes,
  lineHeights,
  letterSpacings,
  families: fontFamilies,
  variants: typographyVariants,
};

export default fonts;
