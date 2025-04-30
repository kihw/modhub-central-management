import { css } from 'styled-components';

const FONT_PATHS = {
  Inter: {
    Light: ['Inter-Light', 300],
    Regular: ['Inter-Regular', 400], 
    Medium: ['Inter-Medium', 500],
    SemiBold: ['Inter-SemiBold', 600],
    Bold: ['Inter-Bold', 700]
  },
  JetBrainsMono: {
    Regular: ['JetBrainsMono-Regular', 400]
  }
} as const;

export const fontFaces = css`
  ${Object.entries(FONT_PATHS).flatMap(([family, weights]) =>
    Object.entries(weights).map(([weight, [file, value]]) => `
      @font-face {
        font-family: '${family}';
        font-style: normal;
        font-weight: ${value};
        font-display: swap;
        src: local('${family} ${weight}'),
             url('../assets/fonts/${file}.woff2') format('woff2'),
             url('../assets/fonts/${file}.woff') format('woff');
      }
    `).join('')
  )}
`;

export const fonts = {
  primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  mono: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
} as const;

export const fontSizes = {
  xs: '0.75rem',
  sm: '0.875rem',
  base: '1rem', 
  md: '1.125rem',
  lg: '1.25rem',
  xl: '1.5rem',
  '2xl': '1.875rem',
  '3xl': '2.25rem',
  '4xl': '3rem'
} as const;

export const fontWeights = {
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700
} as const;

export const lineHeights = {
  tight: 1.2,
  normal: 1.5,
  relaxed: 1.75
} as const;

export const letterSpacings = {
  tighter: '-0.05em',
  tight: '-0.025em',
  normal: '0',
  wide: '0.025em',
  wider: '0.05em'
} as const;

export const fluidFontSize = (minFontSize: string, maxFontSize: string, minScreenWidth: string, maxScreenWidth: string): string => {
  const minFont = parseFloat(minFontSize);
  const maxFont = parseFloat(maxFontSize);
  const minScreen = parseFloat(minScreenWidth);
  const maxScreen = parseFloat(maxScreenWidth);

  if (isNaN(minFont) || isNaN(maxFont) || isNaN(minScreen) || isNaN(maxScreen)) {
    throw new Error('Invalid font size parameters');
  }

  return `
    font-size: ${minFontSize};
    font-size: clamp(
      ${minFontSize},
      calc(${minFont}rem + (${maxFont} - ${minFont}) * ((100vw - ${minScreen}rem) / (${maxScreen} - ${minScreen}))),
      ${maxFontSize}
    );
  `.trim();
};

export default {
  fontFaces,
  fonts,
  fontSizes,
  fontWeights,
  lineHeights,
  letterSpacings,
  fluidFontSize
} as const;