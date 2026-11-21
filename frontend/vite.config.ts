import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Proxy all /api/* requests to the FastAPI backend (LangGraph pipeline)
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // SSE stream for real-time LangGraph state streaming
      '/stream': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../backend/static', // FastAPI will serve this via StaticFiles
    emptyOutDir: true,
  },
})
