/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        navy: '#0A1024',
      },
      fontFamily: {
        sans: ['"Work Sans"', 'sans-serif'],
        display: ['Fraunces', 'serif'],
        'admin-sans': ['Inter', 'sans-serif'],
        'admin-display': ['"Space Grotesk"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}