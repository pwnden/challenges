<script setup lang="ts">
import { ref } from 'vue';
import { usePage, link } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ policy?: unknown; user?: string; resource?: string; versions?: { version: string; title: string }[]; body?: string }>();
const resource = ref(new URLSearchParams(location.search).get('resource') ?? 'locker/team-notes');
</script>
<template>
  <TargetPage title="팀 문서 사이트" :loading="loading" :error="error">
    <section v-if="data?.policy"><p>현재 계정: {{ data.user }}. 공유 작업 노트를 읽고 변경 기록을 확인할 수 있습니다.</p>
      <h2>문서 목록</h2><ul><li>locker/team-notes — 팀 공유 작업 노트 <a :href="link('/read', { resource: 'locker/team-notes' })">현재 문서</a> · <a :href="link('/history', { resource: 'locker/team-notes' })">변경 기록</a></li><li>locker/team-admin — 운영자의 복구 문서 <a :href="link('/read', { resource: 'locker/team-admin' })">현재 문서</a></li><li>locker/personal-draft — 다른 사용자의 개인 초안</li></ul>
    </section>
    <section v-if="data?.policy"><h2>이 계정의 접근 규칙</h2><p>Allow는 허용, Deny는 거절입니다. Action은 기능, Resource는 문서 이름입니다. *는 해당 위치의 글자를 대신합니다. 요청 기능과 문서 이름에 맞는 Deny 규칙이 있으면 거절합니다.</p><pre><code>{{ JSON.stringify(data.policy, null, 2) }}</code></pre><h2>기능 안내</h2><ul><li>현재 문서: read</li><li>변경 기록 목록: read-history</li><li>기록에 저장된 문서: read-version</li></ul><form action="/read"><label>문서 이름<input v-model="resource" name="resource" maxlength="128" required></label><button>읽기</button></form></section>
    <section v-if="data?.versions"><h2>{{ data.resource }} 변경 기록</h2><ul><li v-for="item in data.versions" :key="item.version"><a :href="link('/version', { resource: data.resource!, version: item.version })">{{ item.version }} — {{ item.title }}</a></li></ul></section>
    <section v-if="data?.body !== undefined"><h2>{{ resource }}</h2><pre>{{ data.body }}</pre></section>
  </TargetPage>
</template>
