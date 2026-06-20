/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        coral: '#FF6B4A',
        charcoal: '#1A1A1A',
        cream: '#F5F2EA',
        mustard: '#E8B44A',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        'md': '12px',
        'lg': '16px',
      }
    },
  },
  plugins: [],
}
