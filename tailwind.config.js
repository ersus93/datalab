/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Primary: Sky Blue (científico, preciso)
        primary: {
          50: 'rgba(56, 189, 248, 0.08)',
          100: 'rgba(56, 189, 248, 0.15)',
          200: 'rgba(56, 189, 248, 0.25)',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        
        // Secondary: Violet (autoridad gubernamental)
        secondary: {
          50: 'rgba(167, 139, 250, 0.08)',
          100: 'rgba(167, 139, 250, 0.15)',
          200: 'rgba(167, 139, 250, 0.22)',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },

        // Glass Tokens
        glass: {
          1: 'rgba(255, 255, 255, 0.040)',
          2: 'rgba(255, 255, 255, 0.070)',
          3: 'rgba(255, 255, 255, 0.110)',
          hover: 'rgba(255, 255, 255, 0.130)',
          active: 'rgba(255, 255, 255, 0.170)',
          border: 'rgba(255, 255, 255, 0.110)',
          'border-subtle': 'rgba(255, 255, 255, 0.060)',
          'border-strong': 'rgba(255, 255, 255, 0.190)',
        },

        // Estado (semántico)
        success: {
          50: 'rgba(52, 211, 153, 0.10)',
          100: 'rgba(52, 211, 153, 0.18)',
          500: '#34d399',
          600: '#10b981',
          700: '#059669',
        },
        warning: {
          50: 'rgba(251, 191, 36, 0.10)',
          100: 'rgba(251, 191, 36, 0.18)',
          500: '#fbbf24',
          600: '#f59e0b',
          700: '#d97706',
        },
        error: {
          50: 'rgba(248, 113, 113, 0.10)',
          100: 'rgba(248, 113, 113, 0.18)',
          500: '#f87171',
          600: '#ef4444',
          700: '#dc2626',
        },
        info: {
          50: 'rgba(34, 211, 238, 0.10)',
          100: 'rgba(34, 211, 238, 0.18)',
          500: '#22d3ee',
          600: '#06b6d4',
          700: '#0891b2',
        },

        // Texto
        text: {
          primary: 'rgba(248, 250, 252, 0.92)',
          secondary: 'rgba(148, 163, 184, 0.85)',
          tertiary: 'rgba(100, 116, 139, 0.90)',
          muted: 'rgba(148, 163, 184, 0.50)',
          inverse: '#070c18',
        },

        // Background
        bg: {
          page: '#070c18',
        },
      },

      backdropBlur: {
        sm: 'blur(8px) saturate(140%)',
        md: 'blur(18px) saturate(180%)',
        lg: 'blur(28px) saturate(200%)',
        xl: 'blur(40px) saturate(220%)',
      },

      borderRadius: {
        none: '0',
        sm: '0.25rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.25rem',
        '3xl': '1.75rem',
        full: '9999px',
      },

      boxShadow: {
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.07)',
        'glass-md': '0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.09)',
        'glass-lg': '0 16px 50px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255,255,255,0.12)',
        'glass-xl': '0 25px 60px rgba(0, 0, 0, 0.58), inset 0 1px 0 rgba(255,255,255,0.15)',
        'glass-glow': '0 0 30px rgba(56, 189, 248, 0.18), 0 8px 32px rgba(0, 0, 0, 0.45)',
        'glass-glow-success': '0 0 30px rgba(52, 211, 153, 0.18)',
        'glass-glow-warning': '0 0 30px rgba(251, 191, 36, 0.18)',
        'glass-glow-error': '0 0 30px rgba(248, 113, 113, 0.18)',
      },

      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'orb-blue': 'radial-gradient(circle, rgba(56, 189, 248, 0.22) 0%, transparent 65%)',
        'orb-violet': 'radial-gradient(circle, rgba(139, 92, 246, 0.20) 0%, transparent 65%)',
        'orb-success': 'radial-gradient(circle, rgba(52, 211, 153, 0.15) 0%, transparent 65%)',
      },

      fontFamily: {
        base: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        heading: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },

      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },

      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
      },

      lineHeight: {
        tight: '1.25',
        snug: '1.375',
        normal: '1.5',
        relaxed: '1.625',
        loose: '2',
      },

      spacing: {
        0: '0',
        1: '0.25rem',
        2: '0.5rem',
        3: '0.75rem',
        4: '1rem',
        5: '1.25rem',
        6: '1.5rem',
        8: '2rem',
        10: '2.5rem',
        12: '3rem',
        16: '4rem',
        20: '5rem',
      },

      animation: {
        'orb-float': 'orb-float 12s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'spin': 'spin 700ms linear infinite',
      },

      keyframes: {
        'orb-float': {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 30px) scale(0.9)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(56, 189, 248, 0.18)' },
          '50%': { boxShadow: '0 0 40px rgba(56, 189, 248, 0.28)' },
        },
      },

      transitionDuration: {
        75: '75ms',
        100: '100ms',
        150: '150ms',
        200: '200ms',
        300: '300ms',
        500: '500ms',
      },

      transitionTimingFunction: {
        linear: 'linear',
        in: 'cubic-bezier(0.4, 0, 1, 1)',
        out: 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [
    // Forms plugin (estilos para inputs, selects, checkboxes)
    function({ addBase, theme }) {
      addBase({
        'input[type="text"]': { borderRadius: theme('borderRadius.lg') },
        'input[type="email"]': { borderRadius: theme('borderRadius.lg') },
        'input[type="password"]': { borderRadius: theme('borderRadius.lg') },
        'select': { borderRadius: theme('borderRadius.lg') },
        'textarea': { borderRadius: theme('borderRadius.lg') },
      })
    },
    // Typography plugin (contenido rico: artículos, documentación)
    function({ addBase, theme }) {
      addBase({
        '.prose': { maxWidth: theme('maxWidth.4xl') },
      })
    },
  ],
};
