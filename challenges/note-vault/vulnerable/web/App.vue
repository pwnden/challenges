<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import { FormRoot } from '@target/sectile';
import Field from '@target/Field.vue';
import SubmitButton from '@target/SubmitButton.vue';
import TargetPage from '@target/TargetPage.vue';
import Toaster from '@target/Toaster.vue';
import { useAction } from '@target/useAction';
const { data, loading, error } = usePage<{ user?: string | null; notes?: { id: number; title: string }[]; title?: string; body?: string }>(['/', '/notes/']);
const { busy, toasts, notify, run } = useAction();
const username = ref('guest');
const password = ref('');
const login = () => run(async () => {
  const response = await fetch('/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: username.value, password: password.value }) });
  if (response.ok) location.assign('/');
  else notify('error', '아이디와 비밀번호를 확인하세요.');
}, '연결을 확인하고 다시 로그인하세요.');
</script>
<template>
  <TargetPage title="개인 메모 사이트" :loading="loading" :error="error">
    <template v-if="data?.user" #actions><span class="chip">로그인 계정 <strong>{{ data.user }}</strong></span></template>
    <Toaster v-model:toasts="toasts" />
    <template v-if="data">
        <section v-if="data?.body !== undefined" class="document" aria-labelledby="note-title">
          <h2 id="note-title">{{ data.title }}</h2>
          <pre class="body">{{ data.body }}</pre>
          <p><a href="/">내 메모 목록</a></p>
        </section>
        <section v-else-if="data?.user" class="plain" aria-labelledby="notes-title">
          <h2 id="notes-title">{{ data.user }}의 메모</h2>
          <ul class="rows"><li v-for="note in data.notes" :key="note.id"><a :href="`/notes/${note.id}`">{{ note.title }}<span class="meta">#{{ note.id }}</span></a></li></ul>
        </section>
        <section v-else class="center" aria-labelledby="login-title">
          <h2 id="login-title">로그인</h2>
          <p>로그인하면 내 메모를 읽을 수 있습니다.</p>
          <FormRoot class="login" :on-submit="login">
            <Field v-model="username" label="아이디" name="username" autocomplete="username" required :disabled="busy" />
            <Field v-model="password" label="비밀번호" name="password" type="password" autocomplete="current-password" required :disabled="busy" />
            <SubmitButton variant="primary" :disabled="busy">로그인</SubmitButton>
          </FormRoot>
        </section>
    </template>
  </TargetPage>
</template>
<style scoped>
section.center { margin: 2.5rem auto; }
.body { margin: 0 0 1rem; padding: 0.9rem 1rem; background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius); }
</style>
