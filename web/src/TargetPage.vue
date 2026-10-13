<script setup lang="ts">
import { navigationError, pagePending } from './page';
import SiteHeader from './SiteHeader.vue';
// The frame every site shares: the header always shows, so a page that fails to load keeps
// its navigation. A site adds page links and account actions through the `nav` and `actions` slots.
defineProps<{ title: string; loading?: boolean; error?: string }>();
const home = location.pathname === '/';
</script>
<template>
  <main :aria-busy="loading || pagePending">
    <SiteHeader :title="title">
      <template v-if="$slots.nav || !home" #nav><slot name="nav"><a href="/">처음으로</a></slot></template>
      <template v-if="$slots.actions" #actions><slot name="actions" /></template>
    </SiteHeader>
    <p v-if="navigationError" class="alert" role="alert">{{ navigationError }}</p>
    <p v-if="loading" role="status">불러오는 중…</p>
    <p v-else-if="error" class="alert" role="alert">{{ error }}</p>
    <slot v-else />
  </main>
</template>
