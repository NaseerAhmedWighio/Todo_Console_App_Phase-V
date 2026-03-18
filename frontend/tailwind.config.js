/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-dark': 'linear-gradient(135deg, rgb(9, 15, 32) 0%, rgb(30, 58, 95) 100%)',
      },
      colors: {
        'background-dark': '#0f172a',
        'primary-400': 'rgb(var(--accent-primary) / 0.4)',
        'primary-500': 'rgb(var(--accent-primary))',
        'accent-purple': 'rgb(var(--accent-secondary))',
        'accent-cyan': 'rgb(var(--accent-cyan))',
        'card': 'rgb(var(--card-bg))',
        'card-secondary': 'rgb(var(--card-secondary))',
      },
      borderRadius: {
        'card': '16px',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(var(--glow-color), var(--glow-opacity))',
        'glow-lg': '0 0 30px rgba(var(--glow-color), var(--glow-opacity))',
      },
    },
  },
  plugins: [],
}
