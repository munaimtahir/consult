import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Keystone Compatibility: Support for path-based routing
// Get APP_SLUG from environment variable (can be empty for root path deployment)
const appSlug = process.env.VITE_APP_SLUG || '';
const base = appSlug ? `/${appSlug}/` : '/';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: base,
  server: {
    // Ensure dev server works with subpath
    strictPort: false,
  },
})
