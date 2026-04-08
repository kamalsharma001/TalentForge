/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Deep forest green — primary brand colour from screenshots
        forest: {
          50:  '#f0f7f4',
          100: '#d9ede5',
          200: '#b5dbcc',
          300: '#84c2ab',
          400: '#52a285',
          500: '#318669',
          600: '#236b54',
          700: '#1d5645',
          800: '#1a4538',
          900: '#163a2f',  // ← main brand
          950: '#0c2219',
        },
        // Warm amber/golden yellow accent from screenshots
        amber: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        // Warm cream background from screenshots
        cream: {
          50:  '#fdfcf8',
          100: '#f8f5ec',
          200: '#f0ead6',
          300: '#e6dcbf',
          400: '#d4c99a',
        },
        // Card background (light yellow from screenshots)
        card: {
          yellow: '#fef9e7',
          beige:  '#f5f0e8',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        sans:    ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'card':  '0 2px 16px 0 rgba(26,61,46,0.08)',
        'card-hover': '0 8px 32px 0 rgba(26,61,46,0.14)',
        'btn':   '0 2px 8px 0 rgba(26,61,46,0.25)',
      },
      animation: {
        'fade-in':    'fadeIn 0.4s ease-out',
        'slide-up':   'slideUp 0.4s ease-out',
        'slide-in-r': 'slideInRight 0.35s ease-out',
        'pulse-dot':  'pulseDot 2s infinite',
      },
      keyframes: {
        fadeIn:       { '0%': { opacity: 0 }, '100%': { opacity: 1 } },
        slideUp:      { '0%': { opacity: 0, transform: 'translateY(16px)' }, '100%': { opacity: 1, transform: 'translateY(0)' } },
        slideInRight: { '0%': { opacity: 0, transform: 'translateX(20px)' }, '100%': { opacity: 1, transform: 'translateX(0)' } },
        pulseDot:     { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.4 } },
      },
    },
  },
  plugins: [],
}
