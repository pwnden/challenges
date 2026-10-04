<script setup lang="ts">
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ collections?: string[]; export?: string; crawler?: string }>(['/', '/about']);
</script>
<template>
  <TargetPage title="작은 웹 보관소" :loading="loading" :error="error">
    <section v-if="data?.collections"><p>문을 닫은 팬사이트와 개인 홈페이지의 흔적을 보관합니다.</p><ul><li v-for="name in data.collections" :key="name">{{ name }}</li></ul><a href="/about">운영 안내</a></section>
    <section v-else><h2>운영 안내</h2><p>최근 자료를 이전하면서 내보낸 백업이 있습니다.</p><p>이전 작업의 내보내기 파일명은 <code>{{ data?.export }}</code>입니다.</p><p>검색 서비스가 페이지를 수집할 때 참고하는 안내는 <a :href="data?.crawler">{{ data?.crawler }}</a>에 있습니다.</p></section>
  </TargetPage>
</template>
