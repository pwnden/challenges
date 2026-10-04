import { afterEach, expect, it, vi } from 'vitest';
import { createRenderer, defineComponent, h, nextTick, ref } from 'vue';
import { navigatePages, navigationError, pagePending, usePage } from '../src/page';
import TargetPage from '../src/TargetPage.vue';

type Node = { text: string; children: Node[]; parent?: Node; props: Record<string, unknown> };
function node(text = ''): Node { return { text, children: [], props: {} }; }
function text(item: Node): string { return item.text + item.children.map(text).join(''); }
const renderer = createRenderer<Node, Node>({
  createElement: () => node(), createText: node, createComment: () => node(),
  setText: (item, value) => { item.text = value; },
  setElementText: (item, value) => { item.text = value; item.children = []; },
  patchProp: (item, key, _old, value) => { item.props[key] = value; },
  insert: (item, parent, anchor) => {
    if (item.parent) item.parent.children.splice(item.parent.children.indexOf(item), 1);
    item.parent = parent;
    const index = anchor ? parent.children.indexOf(anchor) : -1;
    parent.children.splice(index < 0 ? parent.children.length : index, 0, item);
  },
  remove: item => { item.parent?.children.splice(item.parent.children.indexOf(item), 1); },
  parentNode: item => item.parent ?? null,
  nextSibling: item => item.parent?.children[item.parent.children.indexOf(item) + 1] ?? null,
});
const unmounts: (() => void)[] = [];
afterEach(() => { unmounts.splice(0).forEach(stop => stop()); vi.unstubAllGlobals(); });
function response(body: string, status = 200) {
  return new Response(JSON.stringify(status === 200 ? { body } : { error: body }), { status, headers: { 'Content-Type': 'application/json' } });
}
function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
async function mount(precommit = true, bootstrap?: { status: number; data: { body?: string; error?: string } }) {
  const listeners: Record<string, (event: NavigateEvent) => void> = {};
  const navigation = { addEventListener: (name: string, listener: (event: NavigateEvent) => void) => { listeners[name] = listener; } };
  vi.stubGlobal('window', { navigation, ...(precommit ? { NavigationPrecommitController: {} } : {}) });
  vi.stubGlobal('location', new URL('http://target.test/'));
  const fetch = vi.fn();
  if (!bootstrap) fetch.mockResolvedValueOnce(response('previous'));
  vi.stubGlobal('fetch', fetch);
  const seed = bootstrap ? { textContent: JSON.stringify(bootstrap), remove: vi.fn() } : undefined;
  vi.stubGlobal('document', { getElementById: () => seed?.remove.mock.calls.length ? null : seed });
  navigationError.value = ''; pagePending.value = false;
  const root = node();
  const revision = ref(0);
  const Scenario = defineComponent({ setup() {
    const { data, loading, error } = usePage<{ body: string }>(['/', '/notes/', '/view']);
    const query = location.search;
    return () => h(TargetPage, { title: 'Target', loading: loading.value, error: error.value }, () => h('p', data.value?.body + query));
  } });
  const app = renderer.createApp({ render: () => h(Scenario, { key: revision.value }) });
  app.mount(root); unmounts.push(() => app.unmount());
  const initialText = text(root);
  await vi.waitFor(() => expect(text(root)).toContain(bootstrap?.status === 401 ? '먼저 로그인' : bootstrap?.data.body ?? 'previous'));
  navigatePages(async () => { revision.value++; await nextTick(); });
  function navigate(path: string, patch: Partial<NavigateEvent> = {}) {
    const abort = new AbortController();
    let options: NavigationInterceptOptions | undefined;
    const event = { destination: { url: new URL(path, location.href).href }, canIntercept: true, cancelable: true,
      hashChange: false, downloadRequest: null, formData: null, signal: abort.signal,
      intercept: vi.fn((value: NavigationInterceptOptions) => { options = value; }), ...patch } as unknown as NavigateEvent;
    listeners.navigate!(event);
    const finish = async () => {
      if (!options) return;
      try {
        if (options.precommitHandler) await options.precommitHandler({} as NavigationPrecommitController);
        vi.stubGlobal('location', new URL(event.destination.url));
        await options.handler?.();
        listeners.navigatesuccess!(event);
      } catch (failure) {
        listeners.navigateerror!(event);
        throw failure;
      }
    };
    return { event, abort, finish };
  }
  return { root, fetch, navigate, initialText, seed };
}

it('mounts full-document history restores with ready server data and no second request', async () => {
  const body = 'Ready document </script><script>alert(1)</script>& 한글';
  const view = await mount(true, { status: 200, data: { body } });
  expect(view.initialText).toContain(body); expect(view.initialText).not.toContain('불러오는 중');
  expect(view.fetch).not.toHaveBeenCalled(); expect(view.seed?.remove).toHaveBeenCalledOnce();
  view.fetch.mockResolvedValueOnce(response('next'));
  await view.navigate('/notes/1').finish();
  expect(text(view.root)).toContain('next'); expect(text(view.root)).not.toContain(body);
  expect(view.fetch).toHaveBeenCalledTimes(1);
});

it('mounts server-provided HTTP errors without loading or refetching', async () => {
  const view = await mount(true, { status: 401, data: { error: 'sign_in_required' } });
  expect(view.initialText).toContain('먼저 로그인'); expect(view.initialText).not.toContain('불러오는 중');
  expect(view.fetch).not.toHaveBeenCalled();
});

it('keeps the old content and address until ready, then renders once without a second fetch', async () => {
  const view = await mount(); const next = deferred<Response>();
  view.fetch.mockReturnValueOnce(next.promise);
  const visit = view.navigate('/view?file=guide.txt'); const finished = visit.finish();
  await nextTick();
  expect(location.pathname).toBe('/'); expect(text(view.root)).toContain('previous');
  expect(text(view.root)).not.toContain('불러오는 중'); expect(pagePending.value).toBe(true);
  next.resolve(response('next')); await finished;
  expect(text(view.root)).toContain('next?file=guide.txt'); expect(text(view.root)).not.toContain('previous');
  expect(text(view.root)).toContain('처음으로'); expect(location.pathname).toBe('/view');
  expect(view.fetch).toHaveBeenCalledTimes(2); expect(pagePending.value).toBe(false);
});

it('retains content during history traversal and older Navigation API transitions', async () => {
  for (const precommit of [true, false]) {
    const view = await mount(precommit); const next = deferred<Response>();
    view.fetch.mockReturnValueOnce(next.promise);
    const visit = view.navigate('/notes/1', { cancelable: false, navigationType: 'traverse' }); const finished = visit.finish();
    await nextTick(); expect(text(view.root)).toContain('previous'); expect(text(view.root)).not.toContain('불러오는 중');
    next.resolve(response('note')); await finished;
    expect(text(view.root)).toContain('note');
  }
});

it('does not let an aborted earlier response replace the last destination', async () => {
  const view = await mount(); const slow = deferred<Response>();
  view.fetch.mockReturnValueOnce(slow.promise).mockResolvedValueOnce(response('latest'));
  const first = view.navigate('/notes/1'); const failure = first.finish().catch(error => error);
  first.abort.abort();
  const second = view.navigate('/notes/2'); await second.finish();
  slow.resolve(response('stale')); expect((await failure).name).toBe('AbortError');
  expect(text(view.root)).toContain('latest'); expect(text(view.root)).not.toContain('stale');
  expect(location.pathname).toBe('/notes/2'); expect(navigationError.value).toBe('');
});

it('retains the prior page after connection failure and permits retry', async () => {
  const view = await mount(); view.fetch.mockRejectedValueOnce(new TypeError('offline'));
  await expect(view.navigate('/notes/1').finish()).rejects.toThrow('offline'); await nextTick();
  expect(text(view.root)).toContain('previous'); expect(text(view.root)).toContain('사이트 연결');
  expect(location.pathname).toBe('/'); expect(pagePending.value).toBe(false);
  view.fetch.mockResolvedValueOnce(response('retried')); await view.navigate('/notes/1').finish();
  expect(text(view.root)).toContain('retried'); expect(navigationError.value).toBe('');
});

it('renders destination HTTP errors after the response arrives', async () => {
  const view = await mount(); view.fetch.mockResolvedValueOnce(response('sign_in_required', 401));
  await view.navigate('/notes/1').finish();
  expect(location.pathname).toBe('/notes/1'); expect(text(view.root)).toContain('먼저 로그인');
  expect(text(view.root)).not.toContain('previous'); expect(text(view.root)).not.toContain('불러오는 중');
});

it('leaves raw resources, downloads, POST, fragment and cross-origin navigation to the browser', async () => {
  const view = await mount();
  for (const [path, patch] of [
    ['/robots.txt', {}], ['/api/notes/2', {}], ['/notes/1', { downloadRequest: 'note.txt' }],
    ['/notes/1', { formData: new FormData() }], ['/#part', { hashChange: true }],
    ['http://other.test/notes/1', {}], ['/notes/1', { canIntercept: false }],
  ] as [string, Partial<NavigateEvent>][]) {
    expect(view.navigate(path, patch).event.intercept).not.toHaveBeenCalled();
  }
  expect(view.fetch).toHaveBeenCalledTimes(1);
});
