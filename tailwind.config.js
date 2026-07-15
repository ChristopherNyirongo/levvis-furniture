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
        sans: ['Manrope', 'sans-serif'],
        display: ['"Playfair Display"', 'serif'],
        'admin-sans': ['Manrope', 'sans-serif'],
        'admin-display': ['"Space Grotesk"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}