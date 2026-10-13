<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
interface Ticket { id: number; title: string; owner: string; body: string; invitation_code?: string }
interface Desk { user: string; role: string; tickets: { id: number; title: string }[] }
interface Staff { user: string; role: string; confirmation: string }
const { data, loading, error } = usePage<Desk>();
const ticketId = ref('');
const invitation = ref('');
const ticket = ref<Ticket | null>(null);
const staff = ref<Staff | null>(null);
const busy = ref(false);
const feedback = ref('');
const failed = ref(false);
async function request(path: string, body?: Record<string, unknown>) {
  if (busy.value) return;
  busy.value = true; failed.value = false; feedback.value = '';
  if (path.startsWith('/api/ticket')) ticket.value = null;
  if (path === '/api/staff' || path === '/api/reset') staff.value = null;
  try {
    const response = await fetch(path, { method: body ? 'POST' : 'GET', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
    const result = await response.json();
    if (!response.ok) { failed.value = true; feedback.value = result.error; }
    else if (result.ticket) { ticket.value = result.ticket; feedback.value = '문의 내용을 확인했습니다.'; }
    else if (result.staff) { staff.value = result.staff; feedback.value = '운영 화면을 열었습니다.'; }
    else {
      data.value = result as Desk; feedback.value = result.notice ?? '현재 계정을 확인했습니다.';
      if (path === '/api/reset') { ticket.value = null; invitation.value = ''; ticketId.value = ''; }
    }
  } catch { failed.value = true; feedback.value = '처리 결과를 확인하지 못했습니다. 현재 계정을 다시 확인하세요.'; }
  finally { busy.value = false; }
}
function lookup(id: string) { ticketId.value = id; return request(`/api/ticket?id=${encodeURIComponent(id)}`); }
</script>
<template>
  <TargetPage title="전시 모임 고객지원" :loading="loading" :error="error">
    <template v-if="data">
      <section>
        <h2>내 시험 계정</h2><p>계정 <code>{{ data.user }}</code> · 권한 <strong>{{ data.role === 'staff' ? '운영 담당자' : '일반 회원' }}</strong></p>
        <div class="actions"><button :disabled="busy" @click="request('/api/desk')">현재 계정 확인</button><button :disabled="busy" @click="request('/api/reset', {})">처음부터 다시</button></div>
      </section>
      <p class="feedback" :class="{ error: failed }" role="status" aria-live="polite">{{ feedback }}</p>
      <section>
        <h2>내 문의</h2><p>문의 본문은 작성자만 읽을 수 있어야 합니다. 알림에 적힌 번호로도 문의를 조회할 수 있습니다.</p>
        <ul><li v-for="item in data.tickets" :key="item.id"><button :disabled="busy" @click="lookup(String(item.id))">#{{ item.id }} · {{ item.title }}</button></li></ul>
        <form @submit.prevent="lookup(ticketId)"><label for="ticket-id">문의 번호<input id="ticket-id" v-model="ticketId" inputmode="numeric" maxlength="8" required :disabled="busy"></label><button :disabled="busy">문의 조회</button></form>
        <article v-if="ticket" class="detail"><h3>#{{ ticket.id }} · {{ ticket.title }}</h3><p>작성자 <code>{{ ticket.owner }}</code></p><p>{{ ticket.body }}</p><p v-if="ticket.invitation_code">초대 코드 <code>{{ ticket.invitation_code }}</code></p></article>
      </section>
      <section>
        <h2>운영 초대</h2><p>초대를 받은 계정은 코드를 등록해 합류합니다. 다른 사람에게 발급된 코드는 사용할 수 없어야 합니다.</p>
        <form @submit.prevent="request('/api/invitation', { code: invitation })"><label for="invitation-code">초대 코드<input id="invitation-code" v-model="invitation" maxlength="128" required autocomplete="off" :disabled="busy"></label><button :disabled="busy">초대 등록</button></form>
      </section>
      <section>
        <h2>운영 화면</h2><p>운영 담당자가 접속 확인 코드를 조회하는 화면입니다.</p><button :disabled="busy" @click="request('/api/staff')">운영 화면 열기</button>
        <article v-if="staff" class="detail"><h3>운영 담당자 접속 확인</h3><p>접속 계정 <code>{{ staff.user }}</code></p><p>접속 확인 코드 <code>{{ staff.confirmation }}</code></p></article>
      </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.detail { margin-top: var(--inset); padding: var(--inset); background: #182334; border-radius: var(--radius); }
.detail code { overflow-wrap: anywhere; }
.feedback { padding: var(--inset); min-height: 5.3rem; margin: 0; }
h3 { font-size: 1rem; }
</style>
