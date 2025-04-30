module.exports = {
  plugins: {
    'postcss-import': {},
    'tailwindcss/nesting': 'postcss-nesting',
    tailwindcss: {},
    autoprefixer: {
      flexbox: 'no-2009',
      grid: 'autoplace', 
      overrideBrowserslist: ['>0.3%', 'not dead', 'not op_mini all']
    },
    ...(process.env.NODE_ENV === 'production' && {
      cssnano: {
        preset: [
          'default',
          {
            discardComments: { removeAll: true },
            normalizeWhitespace: true,
            minifyFontValues: { removeQuotes: false },
            colormin: true,
            calc: false,
            mergeLonghand: true,
            convertValues: true,
            reduceTransforms: true,
            zindex: false
          }
        ],
        plugins: [
          require('postcss-discard-duplicates'),
          require('postcss-merge-rules'),
          require('postcss-merge-longhand'),
          require('postcss-unique-selectors')
        ]
      }
    })
  }
};






































