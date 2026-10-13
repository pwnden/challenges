<script setup lang="ts">
import { ref } from 'vue';
import { usePage, link } from '@target/page';
import Field from '@target/Field.vue';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ policy?: unknown; user?: string; resource?: string; versions?: { version: string; title: string }[]; body?: string }>(['/', '/read', '/history', '/version']);
const resource = ref(new URLSearchParams(location.search).get('resource') ?? 'locker/team-notes');
const documents = [
  { name: 'locker/team-notes', note: '팀 공유 작업 노트', history: true },
  { name: 'locker/team-admin', note: '운영자의 복구 문서', history: false },
  { name: 'locker/personal-draft', note: '다른 사용자의 개인 초안', history: false, readable: false },
];
const actions = [['현재 문서', 'read'], ['변경 기록 목록', 'read-history'], ['기록에 저장된 문서', 'read-version']];
</script>
<template>
  <TargetPage title="팀 문서 사이트" :loading="loading" :error="error">
    <template v-if="data?.user" #actions><span class="chip">현재 계정 <strong>{{ data.user }}</strong></span></template>
    <template v-if="data">
        <template v-if="data?.policy">
          <section aria-labelledby="docs-title">
            <h2 id="docs-title">문서 목록</h2>
            <p>현재 계정: {{ data.user }}. 공유 작업 노트를 읽고 변경 기록을 확인할 수 있습니다.</p>
            <div class="scroll" role="region" aria-label="문서 목록 표" tabindex="0">
              <table>
                <thead><tr><th scope="col">문서</th><th scope="col">설명</th><th scope="col">열기</th></tr></thead>
                <tbody>
                  <tr v-for="item in documents" :key="item.name">
                    <th scope="row"><code>{{ item.name }}</code></th>
                    <td>{{ item.note }}</td>
                    <td class="open"><template v-if="item.readable !== false"><a :href="link('/read', { resource: item.name })">현재 문서</a><template v-if="item.history"> · <a :href="link('/history', { resource: item.name })">변경 기록</a></template></template></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <form action="/read" class="open-form"><Field v-model="resource" label="문서 이름" name="resource" maxlength="128" required /><button class="primary">읽기</button></form>
          </section>
          <section aria-labelledby="rules-title">
            <h2 id="rules-title">이 계정의 접근 규칙</h2>
            <p>Allow는 허용, Deny는 거절입니다. Action은 기능, Resource는 문서 이름입니다. *는 해당 위치의 글자를 대신합니다. 요청 기능과 문서 이름에 맞는 Deny 규칙이 있으면 거절합니다.</p>
            <pre class="policy"><code>{{ JSON.stringify(data.policy, null, 2) }}</code></pre>
            <h3>기능 안내</h3>
            <dl class="actions"><div v-for="[label, action] in actions" :key="action"><dt>{{ label }}</dt><dd><code>{{ action }}</code></dd></div></dl>
          </section>
        </template>
        <section v-if="data?.versions" aria-labelledby="history-title">
          <h2 id="history-title">{{ data.resource }} 변경 기록</h2>
          <ul class="rows"><li v-for="item in data.versions" :key="item.version"><a :href="link('/version', { resource: data.resource!, version: item.version })">{{ item.version }} — {{ item.title }}</a></li></ul>
        </section>
        <section v-if="data?.body !== undefined" class="document" aria-labelledby="doc-title"><h2 id="doc-title">{{ resource }}</h2><pre>{{ data.body }}</pre></section>
    </template>
  </TargetPage>
</template>
<style scoped>
table { min-width: 34rem; }
.open { white-space: nowrap; }
.open-form { margin-top: 1rem; }
.policy { margin: 0 0 1rem; background: var(--bg); }
.actions { display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; margin: 0.5rem 0 0; }
.actions > div { display: flex; gap: 0.5rem; }
.actions dt { color: var(--muted); }
.actions dd { margin: 0; }
</style>
