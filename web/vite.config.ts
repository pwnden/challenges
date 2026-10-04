import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const scenario = process.env.SCENARIO_DIR ?? '../challenges/note-vault/vulnerable/web';
export default defineConfig({
  plugins: [vue(), {
    name: 'target-page-paint',
    'transformIndexHtml': {
      order: 'post',
      handler(html) {
        // Vite recreates the production module tag, so restore its paint gate.
        return html.replace(/<script\b[^>]*>/g, tag =>
          tag.includes('type="module"') && !tag.includes('blocking=')
            ? tag.replace('<script', '<script blocking="render"') : tag);
      },
    },
  }, {
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
