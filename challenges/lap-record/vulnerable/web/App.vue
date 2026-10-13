<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
interface Row { name: string; time_ms: number; mine: boolean }
interface Track { rules: { stars: number; segment_m: number; max_speed: number }; leaderboard: Row[]; best_ms: number | null; trophy?: string }
const { data, loading, error } = usePage<Track>();
const runId = ref<number | null>(null);
const marks = ref<number[]>([]);
const replay = ref('');
const clock = ref(0);
const lastAt = ref(0);
const busy = ref(false);
const feedback = ref('');
const failed = ref(false);
const GAP_MS = 2000;
let timer: number | undefined;
onMounted(() => { timer = window.setInterval(() => { clock.value = Date.now(); }, 100); });
onBeforeUnmount(() => window.clearInterval(timer));
const waitMs = computed(() => Math.max(0, GAP_MS - (clock.value - lastAt.value)));
const stars = computed(() => data.value?.rules.stars ?? 6);
const finished = computed(() => marks.value.length === stars.value);
const seconds = (ms: number) => (ms / 1000).toFixed(2) + '초';
function writeReplay() {
  replay.value = JSON.stringify({ run_id: runId.value, checkpoints: marks.value.map((t_ms, index) => ({ id: index + 1, t_ms })) }, null, 2);
}
async function send(path: string, body: Record<string, unknown>) {
  const response = await fetch(path, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return { ok: response.ok, result: await response.json() };
}
async function act(job: () => Promise<void>) {
  if (busy.value) return;
  busy.value = true; failed.value = false; feedback.value = '';
  try { await job(); } catch { failed.value = true; feedback.value = '처리 결과를 확인하지 못했습니다. 순위표를 다시 확인하세요.'; }
  finally { busy.value = false; }
}
const start = () => act(async () => {
  const { ok, result } = await send('/api/run/start', {});
  if (!ok) { failed.value = true; feedback.value = result.error; return; }
  runId.value = result.run_id; marks.value = []; lastAt.value = Date.now(); clock.value = Date.now(); writeReplay();
  feedback.value = '달리기를 시작했습니다.';
});
const pick = () => act(async () => {
  const { ok, result } = await send('/api/run/checkpoint', { run_id: runId.value, id: marks.value.length + 1 });
  if (!ok) { failed.value = true; feedback.value = result.error; return; }
  marks.value = [...marks.value, result.t_ms]; lastAt.value = Date.now(); writeReplay();
  feedback.value = `별 ${result.id}개를 주웠습니다.`;
});
const submit = () => act(async () => {
  let parsed: { run_id?: number; checkpoints?: unknown };
  try { parsed = JSON.parse(replay.value); } catch { failed.value = true; feedback.value = '기록 코드의 형식을 확인하세요.'; return; }
  const { ok, result } = await send('/api/run/finish', { run_id: parsed.run_id, checkpoints: parsed.checkpoints });
  if (!ok) { failed.value = true; feedback.value = result.error; return; }
  data.value = result as Track; feedback.value = result.notice;
  runId.value = null; marks.value = []; replay.value = '';
});
const reset = () => act(async () => {
  const { ok, result } = await send('/api/reset', {});
  if (!ok) { failed.value = true; feedback.value = result.error; return; }
  data.value = result as Track; feedback.value = result.notice;
  runId.value = null; marks.value = []; replay.value = '';
});
</script>
<template>
  <TargetPage title="별 달리기" :loading="loading" :error="error">
    <template v-if="data">
      <section>
        <h2>트랙 규칙</h2>
        <p>트랙에는 별이 {{ data.rules.stars }}개 있고 별 사이는 {{ data.rules.segment_m }}m입니다. 달리는 사람의 최고 속도는 초속 {{ data.rules.max_speed }}m입니다.
          별은 앞의 별을 주운 뒤 2초가 지나야 주울 수 있습니다. 모든 별을 주우면 기록 코드가 만들어지고, 기록 등록으로 순위표에 올립니다.
          한계 기록보다 빠른 기록을 올리면 전설 트로피 코드가 지급됩니다.</p>
        <div class="actions"><button :disabled="busy" @click="start">달리기 시작</button><button :disabled="busy" @click="reset">처음부터 다시</button></div>
      </section>
      <p class="feedback" :class="{ error: failed }" role="status" aria-live="polite">{{ feedback }}</p>
      <section v-if="runId !== null">
        <h2>달리기 {{ runId }}번</h2>
        <p>주운 별 {{ marks.length }} / {{ stars }}개<template v-if="!finished"> · 다음 별까지 {{ waitMs > 0 ? (waitMs / 1000).toFixed(1) + '초' : '도착' }}</template></p>
        <progress :max="stars" :value="marks.length" aria-label="주운 별"></progress>
        <div class="actions"><button :disabled="busy || finished || waitMs > 0" @click="pick">별 줍기</button></div>
        <label for="replay">기록 코드<textarea id="replay" v-model="replay" rows="12" spellcheck="false" :disabled="busy"></textarea></label>
        <div class="actions"><button :disabled="busy || !finished" @click="submit">기록 등록</button></div>
      </section>
      <section>
        <h2>순위표</h2>
        <table>
          <thead><tr><th scope="col">순위</th><th scope="col">이름</th><th scope="col">기록</th></tr></thead>
          <tbody><tr v-for="(row, index) in data.leaderboard" :key="row.name" :class="{ mine: row.mine }"><td>{{ index + 1 }}</td><td>{{ row.name }}</td><td>{{ seconds(row.time_ms) }}</td></tr></tbody>
        </table>
        <article v-if="data.trophy" class="detail"><h3>전설 트로피</h3><p>트로피 코드 <code>{{ data.trophy }}</code></p></article>
      </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
.feedback { padding: 0.5rem var(--inset); margin: 0; }
.detail { margin-top: var(--inset); padding: var(--inset); background: #182334; border-radius: var(--radius); }
.detail code { overflow-wrap: anywhere; }
textarea { width: 100%; box-sizing: border-box; font-family: var(--mono, monospace); }
progress { width: 100%; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.35rem 0.5rem; text-align: left; }
tr.mine { font-weight: 700; }
h3 { font-size: 1rem; }
</style>
