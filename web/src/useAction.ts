import { ref } from 'vue';
import { addToast, type ToastMessage } from './toasts';

// One shared way to run a request: ignore a second click while one is pending, report a
// failure as a toast and keep the page usable. `postJson` is the request half.
export function useAction() {
  const busy = ref(false);
  const toasts = ref<ToastMessage[]>([]);
  const notify = (kind: ToastMessage['kind'], text: string) => { toasts.value = addToast(toasts.value, kind, text); };
  async function run(job: () => Promise<void>, failure = '처리 결과를 확인하지 못했습니다. 현재 상태를 다시 확인한 뒤 시도하세요.') {
    if (busy.value) return;
    busy.value = true;
    try { await job(); } catch { notify('error', failure); }
    finally { busy.value = false; }
  }
  return { busy, toasts, notify, run };
}

export async function postJson<T = Record<string, unknown>>(path: string, body: Record<string, unknown> = {}) {
  const response = await fetch(path, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return { ok: response.ok, result: await response.json() as T & { error?: string; notice?: string } };
}
