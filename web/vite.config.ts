import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'node:path';

const scenario = process.env.SCENARIO_DIR ?? '../challenges/note-vault/vulnerable/web';
export default defineConfig({
  plugins: [vue()],
  resolve: { dedupe: ['vue'], alias: { '@scenario': resolve(scenario, 'App.vue'), '@target': resolve('src') } },
  build: { outDir: 'dist', emptyOutDir: true },
});
