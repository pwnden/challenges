<script setup lang="ts">
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ collections?: string[]; export?: string; crawler?: string }>(['/', '/about']);
const onAbout = location.pathname === '/about';
</script>
<template>
  <TargetPage title="작은 웹 보관소" :loading="loading" :error="error">
    <template #nav><a href="/" :aria-current="onAbout ? undefined : 'page'">보관 목록</a><a href="/about" :aria-current="onAbout ? 'page' : undefined">운영 안내</a></template>
    <template v-if="data">
        <section v-if="data?.collections" aria-labelledby="collections-title">
          <h2 id="collections-title">보관 중인 자료</h2>
          <p>문을 닫은 팬사이트와 개인 홈페이지의 흔적을 보관합니다.</p>
          <ul class="collections"><li v-for="name in data.collections" :key="name" class="card">{{ name }}</li></ul>
          <p><a href="/about">운영 안내</a></p>
        </section>
        <section v-else aria-labelledby="about-title">
          <h2 id="about-title">운영 안내</h2>
          <p>최근 자료를 이전하면서 내보낸 백업이 있습니다.</p>
          <p>이전 작업의 내보내기 파일명은 <code>{{ data?.export }}</code>입니다.</p>
          <p>검색 서비스가 페이지를 수집할 때 참고하는 안내는 <a :href="data?.crawler">{{ data?.crawler }}</a>에 있습니다.</p>
        </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.collections { display: grid; grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr)); gap: 0.75rem; margin: 0 0 1rem; padding: 0; list-style: none; }
.collections .card { margin: 0; font-weight: 650; }
</style>
