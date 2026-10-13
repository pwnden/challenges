<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { usePage } from '@target/page';
import { FormRoot, ProgressRoot } from '@target/sectile';
import Button from '@target/Button.vue';
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
const pick = () => finished.value || waitMs.value > 0 ? undefined : run(async () => {
  const { ok, result } = await postJson<{ t_ms: number }>('/api/run/checkpoint', { run_id: runId.value, id: marks.value.length + 1 });
  if (!ok) return notify('error', result.error ?? '별을 줍지 못했습니다.');
  marks.value = [...marks.value, result.t_ms]; lastAt.value = Date.now(); writeReplay();
}, '처리 결과를 확인하지 못했습니다. 순위표를 다시 확인하세요.');
const submit = () => !finished.value ? undefined : run(async () => {
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
    <template v-if="data" #actions>
      <Button variant="primary" small :disabled="busy" @click="start">달리기 시작</Button>
      <Button small :disabled="busy" @click="reset">처음부터 다시</Button>
    </template>
    <Toaster v-model:toasts="toasts" />
    <template v-if="data">
      <section aria-labelledby="rules-title">
        <h2 id="rules-title">트랙 규칙</h2>
        <p>트랙에는 별이 {{ data.rules.stars }}개 있고 별 사이는 {{ data.rules.segment_m }}m입니다. 달리는 사람의 최고 속도는 초속 {{ data.rules.max_speed }}m입니다.
          별은 앞의 별을 주운 뒤 2초가 지나야 주울 수 있습니다. 모든 별을 주우면 기록 코드가 만들어지고, 기록 등록으로 순위표에 올립니다.
          한계 기록보다 빠른 기록을 올리면 전설 트로피 코드가 지급됩니다.</p>
      </section>
      <section v-if="runId !== null" aria-labelledby="run-title">
        <h2 id="run-title">달리기 {{ runId }}번</h2>
        <ProgressRoot class="progress" :value="marks.length" :max="stars" label="주운 별" :format-value="count => `${count}/${stars}개`">
          <ol class="stars" aria-hidden="true">
            <li v-for="n in stars" :key="n" :class="{ got: n <= marks.length }">
              <svg viewBox="0 0 24 24" width="36" height="36"><path d="M12 2.5l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8-6.1-3.4-6.1 3.4 1.4-6.8-5.1-4.7 6.9-.8z" /></svg>
            </li>
          </ol>
        </ProgressRoot>
        <p class="status">주운 별 {{ marks.length }} / {{ stars }}개<template v-if="!finished"> · 다음 별까지 {{ waitMs > 0 ? (waitMs / 1000).toFixed(1) + '초' : '도착' }}</template></p>
        <Button variant="primary" :disabled="busy || finished || waitMs > 0" @click="pick">별 줍기</Button>
        <FormRoot class="stack replay-form" :on-submit="submit">
          <Field id="replay" v-model="replay" label="기록 코드" multiline rows="12" :spellcheck="false" />
          <SubmitButton :disabled="busy || !finished">기록 등록</SubmitButton>
        </FormRoot>
      </section>
      <section aria-labelledby="board-title">
        <h2 id="board-title">순위표</h2>
        <div class="scroll" role="region" aria-label="순위표" tabindex="0">
          <table>
            <thead><tr><th scope="col">순위</th><th scope="col">이름</th><th scope="col" class="num">기록</th></tr></thead>
            <tbody><tr v-for="(row, index) in data.leaderboard" :key="row.name" :class="{ mine: row.mine }"><td>{{ index + 1 }}</td><th scope="row">{{ row.name }}</th><td class="num">{{ seconds(row.time_ms) }}</td></tr></tbody>
          </table>
        </div>
        <article v-if="data.trophy" class="card trophy"><h3>전설 트로피</h3><p>트로피 코드 <code>{{ data.trophy }}</code></p></article>
      </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.progress { margin: 0.25rem 0 0.5rem; }
.stars { display: flex; gap: 0.5rem; margin: 0; padding: 0; list-style: none; }
.stars li { margin: 0; line-height: 0; }
.stars svg { fill: var(--tint); stroke: var(--line-strong); stroke-width: 1.2; stroke-linejoin: round; }
.stars .got svg { fill: #e8a317; stroke: #8a5a00; }
.status { margin: 0 0 0.75rem; }
.replay-form { max-width: none; margin-top: 1rem; }
.replay-form button { justify-self: start; }
tbody th { font-weight: 600; text-align: left; }
tr.mine th, tr.mine td { font-weight: 700; background: var(--tint); }
.trophy { margin-top: 1rem; border-color: var(--ink); }
.trophy code { overflow-wrap: anywhere; }
</style>
