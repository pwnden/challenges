<script setup lang="ts">
import { navigationError, pagePending } from './page';
import SiteHeader from './SiteHeader.vue';
// A bare page keeps loading and error handling but lets the scenario draw its own site.
defineProps<{ title: string; loading?: boolean; error?: string; bare?: boolean }>();
const home = location.pathname === '/';
</script>
<template>
  <component :is="bare ? 'div' : 'main'" :aria-busy="loading || pagePending">
    <SiteHeader v-if="!bare" :title="title"><template v-if="!home" #nav><a href="/">처음으로</a></template></SiteHeader>
    <p v-if="navigationError" class="error" role="alert">{{ navigationError }}</p>
    <p v-if="loading" role="status">불러오는 중…</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>
    <slot v-else />
  </component>
</template>
