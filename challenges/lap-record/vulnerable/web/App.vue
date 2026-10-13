<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { usePage } from '@target/page';
import { FormRoot, ProgressIndicator, ProgressRoot, ProgressTrack } from '@target/sectile';
import Field from '@target/Field.vue';
import SubmitButton from '@target/SubmitButton.vue';
import TargetPage from '@target/TargetPage.vue';
import Toaster from '@target/Toaster.vue';
import { postJson, useAction } from '@target/useAction';
interface Row { name: string; time_ms: number; mine: boolean }
interface Track { rules: { stars: number; segment_m: number; max_speed: number }; leaderboard: Row[]; best_ms: number | null; trophy?: string; notice?: string }
const { data, loading, error } = usePage<Track>();
const { busy, toasts, notify, run } = useAction();
const runId = ref<number | null>(null);
const marks = ref<number[]>([]);
const replay = ref('');
const clock = ref(0);
const lastAt = ref(0);
const GAP_MS = 2000;
let timer: number | undefined;
onMounted(() => { timer = window.setInterval(() => { clock.value = Date.now(); }, 100); });
onBeforeUnmount(() => window.clearInterval(timer));
const waitMs = computed(() => Math.max(0, GAP_MS - (clock.value - lastAt.value)));
const stars = computed(() => data.value?.rules.stars ?? 6);
const finished = computed(() => marks.value.length === stars.value);
const seconds = (ms: number) => (ms / 1000).toFixed(2) + '초';
const clear = () => { runId.value = null; marks.value = []; replay.value = ''; };
function writeReplay() {
  replay.value = JSON.stringify({ run_id: runId.value, checkpoints: marks.value.map((t_ms, index) => ({ id: index + 1, t_ms })) }, null, 2);
}
const start = () => run(async () => {
  const { ok, result } = await postJson<{ run_id: number }>('/api/run/start');
  if (!ok) return notify('error', result.error ?? '달리기를 시작하지 못했습니다.');
  runId.value = result.run_id; marks.value = []; lastAt.value = Date.now(); clock.value = Date.now(); writeReplay();
}, '처리 결과를 확인하지 못했습니다. 순위표를 다시 확인하세요.');
const pick = () => run(async () => {
  const { ok, result } = await postJson<{ t_ms: number }>('/api/run/checkpoint', { run_id: runId.value, id: marks.value.length + 1 });
  if (!ok) return notify('error', result.error ?? '별을 줍지 못했습니다.');
  marks.value = [...marks.value, result.t_ms]; lastAt.value = Date.now(); writeReplay();
}, '처리 결과를 확인하지 못했습니다. 순위표를 다시 확인하세요.');
const submit = () => run(async () => {
  let parsed: { run_id?: number; checkpoints?: unknown };
  try { parsed = JSON.parse(replay.value); } catch { return notify('error', '기록 코드의 형식을 확인하세요.'); }
  const { ok, result } = await postJson<Track>('/api/run/finish', { run_id: parsed.run_id, checkpoints: parsed.checkpoints });
  if (!ok) return notify('error', result.error ?? '기록을 등록하지 못했습니다.');
  data.value = result; notify('success', result.notice ?? ''); clear();
}, '처리 결과를 확인하지 못했습니다. 순위표를 다시 확인하세요.');
const reset = () => run(async () => {
  const { ok, result } = await postJson<Track>('/api/reset');
  if (!ok) return notify('error', result.error ?? '초기화하지 못했습니다.');
  data.value = result; notify('success', result.notice ?? ''); clear();
}, '처리 결과를 확인하지 못했습니다. 순위표를 다시 확인하세요.');
</script>
<template>
  <TargetPage title="별 달리기" :loading="loading" :error="error">
    <template v-if="data">
      <Toaster v-model:toasts="toasts" />
      <section>
        <h2>트랙 규칙</h2>
        <p>트랙에는 별이 {{ data.rules.stars }}개 있고 별 사이는 {{ data.rules.segment_m }}m입니다. 달리는 사람의 최고 속도는 초속 {{ data.rules.max_speed }}m입니다.
          별은 앞의 별을 주운 뒤 2초가 지나야 주울 수 있습니다. 모든 별을 주우면 기록 코드가 만들어지고, 기록 등록으로 순위표에 올립니다.
          한계 기록보다 빠른 기록을 올리면 전설 트로피 코드가 지급됩니다.</p>
        <div class="row"><button class="primary" :disabled="busy" @click="start">달리기 시작</button><button :disabled="busy" @click="reset">처음부터 다시</button></div>
      </section>
      <section v-if="runId !== null">
        <h2>달리기 {{ runId }}번</h2>
        <p>주운 별 {{ marks.length }} / {{ stars }}개<template v-if="!finished"> · 다음 별까지 {{ waitMs > 0 ? (waitMs / 1000).toFixed(1) + '초' : '도착' }}</template></p>
        <ProgressRoot class="progress" :value="marks.length" :max="stars" label="주운 별" :format-value="count => `${count}/${stars}개`"><ProgressTrack class="track"><ProgressIndicator class="bar" /></ProgressTrack></ProgressRoot>
        <div class="row"><button class="primary" :disabled="busy || finished || waitMs > 0" @click="pick">별 줍기</button></div>
        <FormRoot class="stack replay-form" :on-submit="submit">
          <Field id="replay" v-model="replay" label="기록 코드" multiline rows="12" :spellcheck="false" :disabled="busy" />
          <SubmitButton :disabled="busy || !finished">기록 등록</SubmitButton>
        </FormRoot>
      </section>
      <section>
        <h2>순위표</h2>
        <div class="scroll" role="region" aria-label="순위표" tabindex="0">
          <table>
            <thead><tr><th scope="col">순위</th><th scope="col">이름</th><th scope="col" class="num">기록</th></tr></thead>
            <tbody><tr v-for="(row, index) in data.leaderboard" :key="row.name" :class="{ mine: row.mine }"><td>{{ index + 1 }}</td><td>{{ row.name }}</td><td class="num">{{ seconds(row.time_ms) }}</td></tr></tbody>
          </table>
        </div>
        <article v-if="data.trophy" class="card trophy"><h3>전설 트로피</h3><p>트로피 코드 <code>{{ data.trophy }}</code></p></article>
      </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
.progress { margin: 0.5rem 0; }
.track { height: 0.6rem; overflow: hidden; background: var(--tint); border: 1px solid var(--line); border-radius: 999px; }
.bar { width: var(--sectile-progress-percentage); height: 100%; background: var(--accent); }
.replay-form { max-width: none; margin-top: 1rem; }
.replay-form button { justify-self: start; }
tr.mine th, tr.mine td { font-weight: 700; background: var(--tint); }
.trophy { margin-top: 1rem; border-color: var(--ink); }
.trophy code { overflow-wrap: anywhere; }
</style>
