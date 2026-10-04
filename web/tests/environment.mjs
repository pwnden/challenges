import { builtinEnvironments } from 'vitest/runtime';

// Client-compiled Vue components on a custom renderer, without a DOM library.
export default { ...builtinEnvironments.node, name: 'target', viteEnvironment: 'client' };
