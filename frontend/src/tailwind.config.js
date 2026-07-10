/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Playfair Display"', 'serif'],
        serif: ['"Cormorant Garamond"', 'serif'],
      },
      colors: {
        vellum: {
          DEFAULT: '#ece1c8',
          card: '#f5ecd6',
        },
        gold: {
          DEFAULT: '#cfa640',
          bright: '#f0cf87',
          dark: '#a97f2e',
        },
        porphyry: {
          DEFAULT: '#6e1f2b',
          deep: '#4c141d',
        },
        ink: {
          DEFAULT: '#2a1d14',
          soft: '#5c4632',
        },
        candle: {
          DEFAULT: '#f0cf87',
        },
      },
    },
  },
  plugins: [],
}