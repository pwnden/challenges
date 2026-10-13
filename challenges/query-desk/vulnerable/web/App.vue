<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import Field from '@target/Field.vue';
import TargetPage from '@target/TargetPage.vue';
const name = ref(new URLSearchParams(location.search).get('name') ?? '');
const { data, loading, error } = usePage<{ query?: string; error?: string; matches: { name: string; note: string }[] }>();
</script>
<template>
  <TargetPage title="회원 검색 데스크" :loading="loading" :error="error">
    <template v-if="data">
        <section aria-labelledby="search-title">
          <h2 id="search-title">회원 찾기</h2>
          <p>공개 회원 mira와 sol의 소개를 검색할 수 있습니다.</p>
          <form action="/" method="get"><Field v-model="name" label="회원 이름" name="name" maxlength="256" /><button class="primary">검색</button></form>
        </section>
        <section aria-labelledby="condition-title">
          <h2 id="condition-title">이번 검색에 사용한 조건</h2>
          <p v-if="data?.error" class="alert" role="status">{{ data.error }}</p>
          <pre v-else class="condition"><code>{{ data?.query }}</code></pre>
        </section>
        <section aria-labelledby="result-title">
          <h2 id="result-title">검색 결과</h2>
          <div class="scroll" role="region" aria-label="검색 결과 표" tabindex="0">
            <table>
              <thead><tr><th scope="col">닉네임</th><th scope="col">소개</th></tr></thead>
              <tbody>
                <tr v-for="(row, index) in data?.matches" :key="index"><th scope="row">{{ row.name }}</th><td>{{ row.note }}</td></tr>
                <tr v-if="!data?.matches?.length"><td colspan="2" class="muted">검색 결과가 없습니다.</td></tr>
              </tbody>
            </table>
          </div>
          <p class="legend muted">public = 1은 공개 회원, public = 0은 비공개 회원을 뜻합니다.</p>
        </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.condition { margin: 0; background: var(--bg); }
.legend { margin: 0.75rem 0 0; font-size: 0.9rem; }
table { min-width: 22rem; }
th[scope='row'] { font-weight: 650; }
</style>
