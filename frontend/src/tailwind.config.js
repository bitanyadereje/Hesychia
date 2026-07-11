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
        parchment: {
          DEFAULT: '#f4efe6',
          dark: '#e8ddd0',
          card: '#fcf9f2',
        },
        gold: {
          DEFAULT: '#b8966b',
          dark: '#a07d54',
          light: '#d6c6b2',
        },
        ink: {
          DEFAULT: '#3b2f2f',
          light: '#6b5a4a',
        },
      },
      screens: {
        xs: '480px',
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
      },
    },
  },
  plugins: [],
}