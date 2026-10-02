<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const name = ref(new URLSearchParams(location.search).get('name') ?? '');
const { data, loading, error } = usePage<{ query?: string; error?: string; matches: { name: string; note: string }[] }>();
</script>
<template>
  <TargetPage title="회원 검색 데스크" :loading="loading" :error="error">
    <section><p>공개 회원 mira와 sol의 소개를 검색할 수 있습니다.</p><form action="/" method="get"><label>회원 이름<input v-model="name" name="name" maxlength="256"></label><button>검색</button></form></section>
    <section><h2>이번 검색에 사용한 조건</h2><p v-if="data?.error" class="error" role="status">{{ data.error }}</p><pre v-else><code>{{ data?.query }}</code></pre></section>
    <section><h2>검색 결과</h2><table><thead><tr><th scope="col">닉네임</th><th scope="col">소개</th></tr></thead><tbody><tr v-for="(row, index) in data?.matches" :key="index"><td>{{ row.name }}</td><td>{{ row.note }}</td></tr></tbody></table><p>public = 1은 공개 회원, public = 0은 비공개 회원을 뜻합니다.</p></section>
  </TargetPage>
</template>
