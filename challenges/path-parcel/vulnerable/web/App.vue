<script setup lang="ts">
import { ref } from 'vue';
import { usePage, link } from '@target/page';
import Field from '@target/Field.vue';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ files?: string[]; body?: string }>(['/', '/view']);
const file = ref(new URLSearchParams(location.search).get('file') ?? 'welcome.txt');
const current = new URLSearchParams(location.search).get('file');
</script>
<template>
  <TargetPage title="주소 없는 택배함" :loading="loading" :error="error">
    <template v-if="data">
        <section aria-labelledby="find-title">
          <h2 id="find-title">파일 찾기</h2>
          <p>접수 안내 문서를 파일명으로 찾아 읽는 사이트입니다.</p>
          <form action="/view"><Field v-model="file" label="파일명" name="file" maxlength="256" required /><button class="primary">읽기</button></form>
        </section>
        <div :class="data?.files ? 'split' : 'single'">
          <nav v-if="data?.files" aria-label="파일 목록"><ul class="rows"><li v-for="name in data.files" :key="name"><a :href="link('/view', { file: name })" :aria-current="name === current ? 'page' : undefined">{{ name }}</a></li></ul></nav>
          <section v-if="data?.body !== undefined" class="document" aria-labelledby="file-title"><h2 id="file-title">{{ file }}</h2><pre>{{ data.body }}</pre></section>
          <p v-else class="empty muted">목록에서 파일을 고르면 내용이 여기에 표시됩니다.</p>
        </div>
    </template>
  </TargetPage>
</template>
<style scoped>
.split, .single { margin-top: 1rem; }
.split section, .single section { margin: 0; }
.empty { margin: 0; padding: 1rem; background: var(--paper); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>
