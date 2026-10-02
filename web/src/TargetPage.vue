<script setup lang="ts">
defineProps<{ title: string; loading?: boolean; error?: string }>();
const home = location.pathname === '/';
</script>
<template>
  <main :aria-busy="loading">
    <header><h1>{{ title }}</h1><a v-if="!home" href="/">처음으로</a></header>
    <p v-if="loading" role="status">불러오는 중…</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>
    <slot v-else />
  </main>
</template>
