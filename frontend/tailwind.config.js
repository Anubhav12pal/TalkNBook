/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-red': '#dc2626',
        'brand-yellow': '#fbbf24', 
        'brand-green': '#10b981',
        'brand-blue': '#3b82f6',
        'dark-bg': '#1a1a1a',
        'dark-card': '#2a2a2a',
        'dark-border': '#3a3a3a',
        'dark-input': '#1a1a1a',
      },
      animation: {
        'pulse-brand': 'pulse 2s infinite',
      },
      aspectRatio: {
        '2/3': '2 / 3',
      },
    },
  },
  plugins: [],
}

