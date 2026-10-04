<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
const { data, loading, error } = usePage<{ user?: string | null; notes?: { id: number; title: string }[]; title?: string; body?: string }>(['/', '/notes/']);
const username = ref('guest');
const password = ref('');
const pending = ref(false);
const loginError = ref('');
async function login() {
  if (pending.value) return;
  pending.value = true; loginError.value = '';
  try {
    const response = await fetch('/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: username.value, password: password.value }) });
    if (response.ok) location.assign('/');
    else loginError.value = '아이디와 비밀번호를 확인하세요.';
  } catch { loginError.value = '연결을 확인하고 다시 로그인하세요.'; }
  finally { pending.value = false; }
}
</script>
<template>
  <TargetPage title="개인 메모 사이트" :loading="loading" :error="error">
    <section v-if="data?.body !== undefined"><h2>{{ data.title }}</h2><pre>{{ data.body }}</pre><a href="/">내 메모 목록</a></section>
    <section v-else-if="data?.user"><h2>{{ data.user }}의 메모</h2><ul><li v-for="note in data.notes" :key="note.id"><a :href="`/notes/${note.id}`">{{ note.title }}</a> · #{{ note.id }}</li></ul></section>
    <section v-else><h2>로그인</h2><p>로그인하면 내 메모를 읽을 수 있습니다.</p>
      <form class="login" @submit.prevent="login"><label>아이디<input v-model="username" name="username" autocomplete="username" required></label><label>비밀번호<input v-model="password" name="password" type="password" autocomplete="current-password" required></label><button :disabled="pending">로그인</button><p class="feedback error" role="status">{{ loginError }}</p></form>
    </section>
  </TargetPage>
</template>
