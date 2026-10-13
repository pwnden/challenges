<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import Field from '@target/Field.vue';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ role?: string; body?: string }>(['/', '/key']);
const stored = document.cookie.split('; ').find(item => item.startsWith('paper_role='))?.slice('paper_role='.length);
const claim = ref(stored ? decodeURIComponent(stored) : 'guest');
const onKey = location.pathname === '/key';
function save() { document.cookie = `paper_role=${encodeURIComponent(claim.value)}; Path=/; SameSite=Lax`; location.reload(); }
</script>
<template>
  <TargetPage title="제작실 문서 사이트" :loading="loading" :error="error">
    <template #nav><a href="/" :aria-current="onKey ? undefined : 'page'">작업 노트</a><a href="/key" :aria-current="onKey ? 'page' : undefined">장비 복구 키</a></template>
    <template v-if="data?.role" #actions><span class="chip">서버가 판단한 사용자 구분 <strong>{{ data.role }}</strong></span></template>
    <template v-if="data">
        <section v-if="data?.body !== undefined" aria-labelledby="key-title"><h2 id="key-title">장비 복구 키</h2><pre>{{ data.body }}</pre></section>
        <template v-else>
          <section aria-labelledby="notes-title">
            <h2 id="notes-title">작업 노트</h2>
            <p>게스트는 공개 작업 노트를, 운영자는 장비 복구 키를 읽을 수 있습니다.</p>
            <p>서버가 판단한 사용자 구분: <strong>{{ data?.role }}</strong></p>
            <p>guest는 게스트, staff는 운영자를 뜻합니다. <a href="/key">장비 복구 키</a>는 운영자용 자료입니다.</p>
          </section>
          <section aria-labelledby="cookie-title">
            <h2 id="cookie-title">브라우저에 저장된 사용자 구분</h2>
            <p>paper_role은 브라우저가 사이트에 보내는 쿠키 값입니다. 아래 입력칸에서 바꿀 수 있습니다. 저장 후 서버의 판단과 복구 키 접근 결과를 확인하세요.</p>
            <form @submit.prevent="save"><Field v-model="claim" label="사용자 구분 (paper_role)" maxlength="32" pattern="[a-z]+" required /><button class="primary">저장</button></form>
          </section>
        </template>
    </template>
  </TargetPage>
</template>
<style scoped>
</style>
