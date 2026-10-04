import { onMounted, ref } from 'vue';

type Page = { data?: unknown; error: string };
let prepared: Page | undefined;
let routes: readonly string[] = ['/'];
export const pagePending = ref(false);
export const navigationError = ref('');
const connectionError = '사이트 연결을 확인하고 다시 시도하세요.';

function pageResult(status: number, payload: unknown): Page {
  if (status >= 200 && status < 300) return { data: payload, error: '' };
  const failure = payload as { body?: string; error?: string };
  const reasons: Record<string, string> = { sign_in_required: '메모를 읽으려면 먼저 로그인하세요.', not_found: '자료를 찾을 수 없습니다.', invalid_note_id: '메모 번호를 확인하세요.' };
  return { error: failure.body ?? reasons[failure.error ?? ''] ?? failure.error ?? '자료를 읽을 수 없습니다.' };
}

function documentPage(): Page | undefined {
  if (typeof document === 'undefined') return;
  const element = document.getElementById('pwnden-page-data');
  if (!element?.textContent) return;
  const initial = JSON.parse(element.textContent) as { status: number; data: unknown };
  element.remove();
  return pageResult(initial.status, initial.data);
}

async function readPage(path: string, signal?: AbortSignal): Promise<Page> {
  const response = await fetch(path, { headers: { Accept: 'application/json' }, cache: 'no-store', signal });
  const json = response.headers.get('Content-Type')?.includes('application/json');
  const payload = json ? await response.json() : { body: await response.text() };
  return pageResult(response.status, payload);
}

export function navigatePages(render: () => Promise<void>) {
  const navigation = window.navigation;
  if (!navigation) return;
  let active: AbortSignal | undefined;
  navigation.addEventListener('navigate', event => {
    const url = new URL(event.destination.url);
    if (!event.canIntercept || event.hashChange || event.downloadRequest != null || event.formData
        || url.origin !== location.origin || url.username || url.password
        || !routes.some(path => path.endsWith('/') && path !== '/' ? url.pathname.startsWith(path) : url.pathname === path)) return;
    active = event.signal;
    pagePending.value = true;
    navigationError.value = '';
    let page: Page | undefined;
    const prepare = async () => {
      try {
        page = await readPage(url.pathname + url.search, event.signal);
        event.signal.throwIfAborted();
      } catch (failure) {
        if (active === event.signal && !event.signal.aborted) navigationError.value = connectionError;
        throw failure;
      }
    };
    const commit = async () => {
      event.signal.throwIfAborted();
      prepared = page;
      try { await render(); }
      finally { prepared = undefined; }
    };
    // Precommit keeps the address and document together until data is ready.
    // Older Navigation API implementations still retain the document content.
    if (event.cancelable && 'NavigationPrecommitController' in window) {
      event.intercept({ precommitHandler: prepare, handler: commit });
    } else {
      event.intercept({ handler: async () => { await prepare(); await commit(); } });
    }
    event.signal.addEventListener('abort', () => {
      if (active === event.signal) pagePending.value = false;
    }, { once: true });
  });
  navigation.addEventListener('navigatesuccess', () => { pagePending.value = false; });
  navigation.addEventListener('navigateerror', () => { pagePending.value = false; });
}

export function link(path: string, parameters: Record<string, string>): string {
  return `${path}?${new URLSearchParams(parameters)}`;
}

export function usePage<T>(paths: readonly string[] = ['/']) {
  routes = paths;
  const path = location.pathname + location.search;
  const initial = prepared ?? documentPage();
  const data = ref(initial?.data as T | undefined);
  const loading = ref(!initial);
  const error = ref(initial?.error ?? '');
  async function load() {
    loading.value = true; error.value = '';
    try {
      const page = await readPage(path);
      data.value = page.data as T;
      error.value = page.error;
    } catch { error.value = connectionError; }
    finally { loading.value = false; }
  }
  onMounted(() => { if (!initial) void load(); });
  return { data, loading, error, load };
}
