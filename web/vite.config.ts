import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const scenario = process.env.SCENARIO_DIR ?? '../challenges/note-vault/vulnerable/web';
export default defineConfig({
  plugins: [vue(), {
    name: 'target-font-licenses',
    generateBundle() {
      for (const name of ['Pretendard-OFL.txt', 'D2Coding-OFL.txt']) {
        this.emitFile({ type: 'asset', fileName: `assets/licenses/${name}`, source: readFileSync(resolve('src/fonts', name), 'utf8') });
      }
    },
  }],
  resolve: { dedupe: ['vue'], alias: { '@scenario': resolve(scenario, 'App.vue'), '@target': resolve('src') } },
  build: { outDir: 'dist', emptyOutDir: true },
});
