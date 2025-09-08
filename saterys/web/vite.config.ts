import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  root: '.',             // saterys/web
  publicDir: 'public',
  build: {
    outDir: '../static', // build directly into the Python package
    emptyOutDir: true
  },
  server: {
    port: 5173
  }
});
