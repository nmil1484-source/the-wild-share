import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    'process.env': {},
    'process.version': JSON.stringify(''),
    'process.versions': JSON.stringify({}),
    'process': JSON.stringify({
      env: {},
      version: '',
      versions: {}
    })
  },
  build: {
    outDir: '../src/static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
})

