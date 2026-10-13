<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import { FormRoot } from '@target/sectile';
import Button from '@target/Button.vue';
import Field from '@target/Field.vue';
import SubmitButton from '@target/SubmitButton.vue';
import TargetPage from '@target/TargetPage.vue';
import Toaster from '@target/Toaster.vue';
import { useAction } from '@target/useAction';
interface Ticket { id: number; title: string; owner: string; body: string; invitation_code?: string }
interface Desk { user: string; role: string; tickets: { id: number; title: string }[]; notice?: string }
interface Staff { user: string; role: string; confirmation: string }
const { data, loading, error } = usePage<Desk>();
const { busy, toasts, notify, run } = useAction();
const ticketId = ref('');
const invitation = ref('');
const ticket = ref<Ticket | null>(null);
const staff = ref<Staff | null>(null);
const request = (path: string, body?: Record<string, unknown>) => run(async () => {
  if (path.startsWith('/api/ticket')) ticket.value = null;
  if (path === '/api/staff' || path === '/api/reset') staff.value = null;
  const response = await fetch(path, { method: body ? 'POST' : 'GET', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
  const result = await response.json();
  if (!response.ok) return notify('error', result.error);
  if (result.ticket) ticket.value = result.ticket;
  else if (result.staff) staff.value = result.staff;
  else {
    data.value = result as Desk;
    if (result.notice) notify('success', result.notice);
    if (path === '/api/reset') { ticket.value = null; invitation.value = ''; ticketId.value = ''; }
  }
}, '처리 결과를 확인하지 못했습니다. 현재 계정을 다시 확인하세요.');
const lookup = (id: string) => { ticketId.value = id; return request(`/api/ticket?id=${encodeURIComponent(id)}`); };
</script>
<template>
  <TargetPage title="전시 모임 고객지원" :loading="loading" :error="error">
    <template v-if="data" #actions>
      <span class="chip">계정 <code>{{ data.user }}</code> · 권한 <strong>{{ data.role === 'staff' ? '운영 담당자' : '일반 회원' }}</strong></span>
      <Button small :disabled="busy" @click="request('/api/desk')">현재 계정 확인</Button>
      <Button small :disabled="busy" @click="request('/api/reset', {})">처음부터 다시</Button>
    </template>
    <Toaster v-model:toasts="toasts" />
    <template v-if="data">
      <div class="split inbox">
        <section aria-labelledby="inbox-title">
          <h2 id="inbox-title">내 문의</h2>
          <p>문의 본문은 작성자만 읽을 수 있어야 합니다. 알림에 적힌 번호로도 문의를 조회할 수 있습니다.</p>
          <ul class="rows tickets"><li v-for="item in data.tickets" :key="item.id"><Button :disabled="busy" @click="lookup(String(item.id))">#{{ item.id }} · {{ item.title }}</Button></li></ul>
          <FormRoot :on-submit="() => lookup(ticketId)">
            <Field id="ticket-id" v-model="ticketId" label="문의 번호" inputmode="numeric" maxlength="8" required />
            <SubmitButton variant="primary" :disabled="busy">문의 조회</SubmitButton>
          </FormRoot>
        </section>
        <section aria-labelledby="ticket-title" aria-live="polite">
          <template v-if="ticket">
            <h2 id="ticket-title">#{{ ticket.id }} · {{ ticket.title }}</h2>
            <p class="meta">작성자 <code>{{ ticket.owner }}</code></p>
            <p class="body">{{ ticket.body }}</p>
            <p v-if="ticket.invitation_code" class="body">초대 코드 <code>{{ ticket.invitation_code }}</code></p>
          </template>
          <template v-else><h2 id="ticket-title">문의 내용</h2><p class="muted">왼쪽 목록이나 문의 번호로 문의를 열면 본문이 여기에 표시됩니다.</p></template>
        </section>
      </div>
      <div class="pair">
        <section aria-labelledby="invite-title">
          <h2 id="invite-title">운영 초대</h2>
          <p>초대를 받은 계정은 코드를 등록해 합류합니다. 다른 사람에게 발급된 코드는 사용할 수 없어야 합니다.</p>
          <FormRoot :on-submit="() => request('/api/invitation', { code: invitation })">
            <Field id="invitation-code" v-model="invitation" label="초대 코드" maxlength="128" required autocomplete="off" />
            <SubmitButton variant="primary" :disabled="busy">초대 등록</SubmitButton>
          </FormRoot>
        </section>
        <section aria-labelledby="staff-title" aria-live="polite">
          <h2 id="staff-title">운영 화면</h2>
          <p>운영 담당자가 접속 확인 코드를 조회하는 화면입니다.</p>
          <Button :disabled="busy" @click="request('/api/staff')">운영 화면 열기</Button>
          <div v-if="staff" class="card result"><h3>운영 담당자 접속 확인</h3><p>접속 계정 <code>{{ staff.user }}</code></p><p>접속 확인 코드 <code>{{ staff.confirmation }}</code></p></div>
        </section>
      </div>
    </template>
  </TargetPage>
</template>
<style scoped>
.inbox { grid-template-columns: minmax(16rem, 22rem) minmax(0, 1fr); }
.inbox section, .pair section { margin: 0; }
.pair { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr)); gap: 1rem; margin-top: 1rem; }
.tickets { margin-bottom: 1rem; }
.tickets button { display: block; width: 100%; height: auto; padding: 0.7rem 0.9rem; text-align: left; font-weight: 600; background: transparent; border: 0; border-radius: 0; }
.tickets button:hover { background: var(--tint); }
.meta { color: var(--muted); }
.body { padding: 0.8rem 1rem; background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius); }
.result { margin-top: 1rem; background: var(--bg); }
.result code { overflow-wrap: anywhere; }
@media (max-width: 40rem) { .inbox { grid-template-columns: 1fr; } }
</style>
