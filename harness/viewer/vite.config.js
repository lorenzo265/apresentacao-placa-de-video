import { defineConfig } from 'vite';

// base relativa: o build funciona servido de qualquer pasta, sem internet.
export default defineConfig({
  base: './',
  build: { chunkSizeWarningLimit: 1500 },
});
