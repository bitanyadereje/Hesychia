/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Cormorant SC"', 'serif'],
        serif: ['"EB Garamond"', 'serif'],
        rubric: ['"UnifrakturCook"', 'serif'],
      },
      colors: {
        vellum: {
          DEFAULT: '#ece1c8',
          card: '#f5ecd6',
        },
        ink: {
          DEFAULT: '#2a1d14',
          soft: '#5c4632',
        },
        porphyry: {
          DEFAULT: '#6e1f2b',
          deep: '#4c141d',
        },
        gold: {
          DEFAULT: '#a97f2e',
          bright: '#cfa640',
        },
        candle: '#f0cf87',
      },
      keyframes: {
        flicker: {
          '0%, 100%': { opacity: '1', transform: 'scaleY(1)' },
          '35%': { opacity: '0.55', transform: 'scaleY(0.85)' },
          '60%': { opacity: '0.85', transform: 'scaleY(1.05)' },
        },
      },
      animation: {
        flicker: 'flicker 1.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
