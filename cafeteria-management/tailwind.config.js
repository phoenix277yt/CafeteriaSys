/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#007aff', // Apple's blue
        secondary: '#8e8e93', // Apple's gray
        backgroundLight: '#ffffff',
        backgroundDark: '#1c1c1e',
        textLight: '#000000',
        textDark: '#ffffff',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        subtle: '0 1px 3px rgba(0, 0, 0, 0.1)', // Subtle shadow for depth
      },
    },
  },
  plugins: [],
}