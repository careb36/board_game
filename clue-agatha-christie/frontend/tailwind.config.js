/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'victorian-gold': '#d4af37',
        'victorian-dark': '#1a1a2e',
        'victorian-red': '#8b0000',
        'victorian-cream': '#f5f5dc',
      },
      fontFamily: {
        'serif': ['Georgia', 'serif'],
        'display': ['Playfair Display', 'serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          'from': { boxShadow: '0 0 20px #d4af37' },
          'to': { boxShadow: '0 0 40px #d4af37' },
        },
      },
    },
  },
  plugins: [],
}
