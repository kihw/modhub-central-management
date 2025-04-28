/**
 * ModHub Central - Font Configuration
 * 
 * This file contains all font definitions for the application.
 * We use Inter as our primary font family with various weights.
 */

import { css } from 'styled-components';

// Font face definitions
export const fontFaces = css`
  @font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300;
    src: url('../assets/fonts/Inter-Light.woff2') format('woff2'),
         url('../assets/fonts/Inter-Light.woff') format('woff');
    font-display: swap;
  }

  @font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    src: url('../assets/fonts/Inter-Regular.woff2') format('woff2'),
         url('../assets/fonts/Inter-Regular.woff') format('woff');
    font-display: swap;
  }

  @font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 500;
    src: url('../assets/fonts/Inter-Medium.woff2') format('woff2'),
         url('../assets/fonts/Inter-Medium.woff') format('woff');
    font-display: swap;
  }

  @font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 600;
    src: url('../assets/fonts/Inter-SemiBold.woff2') format('woff2'),
         url('../assets/fonts/Inter-SemiBold.woff') format('woff');
    font-display: swap;
  }

  @font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 700;
    src: url('../assets/fonts/Inter-Bold.woff2') format('woff2'),
         url('../assets/fonts/Inter-Bold.woff') format('woff');
    font-display: swap;
  }

  // Monospace font for code blocks and technical content
  @font-face {
    font-family: 'JetBrains Mono';
    font-style: normal;
    font-weight: 400;
    src: url('../assets/fonts/JetBrainsMono-Regular.woff2') format('woff2'),
         url('../assets/fonts/JetBrainsMono-Regular.woff') format('woff');
    font-display: swap;
  }
`;

// Font-related constants
export const fonts = {
  primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  mono: "'JetBrains Mono', monospace",
};

// Font size system
export const fontSizes = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  md: '1.125rem',   // 18px
  lg: '1.25rem',    // 20px
  xl: '1.5rem',     // 24px
  '2xl': '1.875rem', // 30px
  '3xl': '2.25rem',  // 36px
  '4xl': '3rem',     // 48px
};

// Font weights
export const fontWeights = {
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
};

// Line heights
export const lineHeights = {
  tight: 1.2,
  normal: 1.5,
  relaxed: 1.75,
};

// Letter spacings
export const letterSpacings = {
  tighter: '-0.05em',
  tight: '-0.025em', 
  normal: '0',
  wide: '0.025em',
  wider: '0.05em',
};

// Helper function to calculate fluid font sizes between viewport widths
export const fluidFontSize = (minFontSize, maxFontSize, minScreenWidth, maxScreenWidth) => {
  const minFont = parseFloat(minFontSize);
  const maxFont = parseFloat(maxFontSize);
  const minScreen = parseFloat(minScreenWidth);
  const maxScreen = parseFloat(maxScreenWidth);
  
  return `
    font-size: ${minFontSize};
    
    @media screen and (min-width: ${minScreenWidth}) {
      font-size: calc(${minFont}rem + (${maxFont} - ${minFont}) * ((100vw - ${minScreen}rem) / (${maxScreen} - ${minScreen})));
    }
    
    @media screen and (min-width: ${maxScreenWidth}) {
      font-size: ${maxFontSize};
    }
  `;
};

export default {
  fontFaces,
  fonts,
  fontSizes,
  fontWeights,
  lineHeights,
  letterSpacings,
  fluidFontSize
};