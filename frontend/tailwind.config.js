/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#E8835A',
          hover: '#D6744D',
          active: '#C4653F',
          light: '#FFF0E8',
          dark: '#EE9B78',
        },
        secondary: {
          DEFAULT: '#7BB6A4',
          dark: '#8DC7B5',
        },
        accent: {
          DEFAULT: '#F2B84B',
          dark: '#F5C96A',
        },
        background: {
          DEFAULT: '#FFF9F5',
          dark: '#1E1A17',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          dark: '#2A2420',
        },
        'text-primary': {
          DEFAULT: '#3D3028',
          dark: '#F0E6DD',
        },
        'text-secondary': {
          DEFAULT: '#9B8E82',
          dark: '#8C7E72',
        },
        border: {
          DEFAULT: '#F0E6DD',
          dark: '#3D3428',
        },
        success: '#7BB6A4',
        warning: '#F2B84B',
        error: {
          DEFAULT: '#E06B5E',
          dark: '#E88078',
        },
        soft: '#F5EDE6',
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', '"PingFang SC"', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      borderRadius: {
        'btn': '12px',
        'input': '12px',
        'card': '16px',
        'bubble': '18px',
        'icon': '14px',
      },
      boxShadow: {
        'low': '0 2px 8px rgba(61, 48, 40, 0.06)',
        'mid': '0 4px 16px rgba(61, 48, 40, 0.10)',
        'high': '0 8px 32px rgba(61, 48, 40, 0.14)',
      },
      fontSize: {
        'h1': ['28px', { lineHeight: '1.3', fontWeight: '700' }],
        'h2': ['22px', { lineHeight: '1.3', fontWeight: '600' }],
        'h3': ['18px', { lineHeight: '1.4', fontWeight: '600' }],
        'body': ['15px', { lineHeight: '1.6', fontWeight: '400' }],
        'caption': ['13px', { lineHeight: '1.5', fontWeight: '400' }],
        'code': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
      },
      spacing: {
        '18': '4.5rem',
        '72': '18rem',
        '84': '21rem',
      },
      animation: {
        'bounce-dot': 'bounce-dot 1.4s infinite ease-in-out',
        'fade-in': 'fade-in 0.3s ease-in-out',
        'slide-up': 'slide-up 0.2s ease-out',
        'scale-in': 'scale-in 0.25s ease-out',
        'ripple': 'ripple 0.6s ease-out',
        'cursor-blink': 'cursor-blink 1s infinite',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
      },
      keyframes: {
        'bounce-dot': {
          '0%, 80%, 100%': { transform: 'scale(0)' },
          '40%': { transform: 'scale(1)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'ripple': {
          '0%': { transform: 'scale(0)', opacity: '0.5' },
          '100%': { transform: 'scale(4)', opacity: '0' },
        },
        'cursor-blink': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
}
