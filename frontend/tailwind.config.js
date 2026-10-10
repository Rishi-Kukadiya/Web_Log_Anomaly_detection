/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        sidebar: {
          bg: '#0a101f',
          active: '#1e293b',
          hover: '#15203b',
          text: '#94a3b8',
          textActive: '#ffffff',
          accent: '#2563eb',
        },
        dashboard: {
          bg: '#f8fafc',
          card: '#ffffff',
          border: '#e2e8f0',
          heading: '#0f172a',
          subtext: '#64748b',
          anomaly: '#ef4444',
          traffic: '#3b82f6',
          url: '#10b981',
          error: '#f43f5e',
        }
      }
    },
  },
  plugins: [],
}
