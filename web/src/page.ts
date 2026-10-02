import { onMounted, ref } from 'vue';

export function link(path: string, parameters: Record<string, string>): string {
  return `${path}?${new URLSearchParams(parameters)}`;
}

export function usePage<T>(path = location.pathname + location.search) {
  const data = ref<T>();
  const loading = ref(true);
  const error = ref('');
  async function load() {
    loading.value = true; error.value = '';
    try {
      const response = await fetch(path, { headers: { Accept: 'application/json' }, cache: 'no-store' });
      const json = response.headers.get('Content-Type')?.includes('application/json');
      const payload = json ? await response.json() : { body: await response.text() };
      if (response.ok) data.value = payload;
      else {
        const reasons: Record<string, string> = { sign_in_required: '메모를 읽으려면 먼저 로그인하세요.', not_found: '자료를 찾을 수 없습니다.', invalid_note_id: '메모 번호를 확인하세요.' };
        error.value = payload.body ?? reasons[payload.error] ?? payload.error ?? '자료를 읽을 수 없습니다.';
      }
    } catch { error.value = '사이트 연결을 확인하고 다시 시도하세요.'; }
    finally { loading.value = false; }
  }
  onMounted(load);
  return { data, loading, error, load };
}
