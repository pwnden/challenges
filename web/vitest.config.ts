import { defineConfig } from 'vitest/config';

export default defineConfig({ test: { projects: [
  { extends: './vite.config.ts', test: {
    name: 'scenarios', include: ['tests/scenarios.test.ts'], environment: 'node',
  } },
  { extends: './vite.config.ts', test: {
    name: 'navigation', include: ['tests/navigation.test.ts'], environment: './tests/environment.mjs',
    server: { deps: { inline: ['vue', /^@vue\//] } },
  } },
] } });
