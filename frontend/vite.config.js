import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// During `npm run dev` the Django backend is assumed to run on :8000.
// We proxy the backend routes so the browser talks to a single origin
// (http://localhost:5173) and there are no CORS / cookie headaches.
const DJANGO_ORIGIN = process.env.VITE_BACKEND_ORIGIN || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/gmail': { target: DJANGO_ORIGIN, changeOrigin: true },
      '/stripe': { target: DJANGO_ORIGIN, changeOrigin: true },
      '/api': { target: DJANGO_ORIGIN, changeOrigin: true },
      '/health': { target: DJANGO_ORIGIN, changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
