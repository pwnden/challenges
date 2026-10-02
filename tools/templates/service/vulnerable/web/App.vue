<script setup lang="ts">
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const { loading, error } = usePage();
</script>
<template>
  <TargetPage title="문제 사이트" :loading="loading" :error="error">
    <section><h2>사이트 안내</h2><p>이곳에 문제의 화면과 정상 기능을 작성하세요.</p></section>
  </TargetPage>
</template>
