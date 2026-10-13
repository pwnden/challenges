<script setup lang="ts">
// The top bar every site shares: a name that links home, optional page links, and actions on the right.
defineProps<{ title: string }>();
</script>
<template>
  <header class="site-header">
    <h1 class="brand"><a href="/">{{ title }}</a></h1>
    <nav v-if="$slots.nav" aria-label="사이트 메뉴"><slot name="nav" /></nav>
    <div v-if="$slots.actions" class="actions"><slot name="actions" /></div>
  </header>
</template>
