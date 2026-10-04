<script setup lang="ts">
import { ref } from 'vue';
import { usePage, link } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ files?: string[]; body?: string }>(['/', '/view']);
const file = ref(new URLSearchParams(location.search).get('file') ?? 'welcome.txt');
</script>
<template>
  <TargetPage title="주소 없는 택배함" :loading="loading" :error="error">
    <section><p>접수 안내 문서를 파일명으로 찾아 읽는 사이트입니다.</p><ul v-if="data?.files"><li v-for="name in data.files" :key="name"><a :href="link('/view', { file: name })">{{ name }}</a></li></ul><form action="/view"><label>파일명<input v-model="file" name="file" maxlength="256" required></label><button>읽기</button></form></section>
    <section v-if="data?.body !== undefined"><h2>{{ file }}</h2><pre>{{ data.body }}</pre></section>
  </TargetPage>
</template>
