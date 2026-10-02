import { afterEach, expect, it, vi } from 'vitest';
import { createSSRApp, ref } from 'vue';
import { renderToString } from '@vue/server-renderer';
import NoteVault from '../../challenges/note-vault/vulnerable/web/App.vue';
import BorrowedBadge from '../../challenges/borrowed-badge/vulnerable/web/App.vue';
import QueryDesk from '../../challenges/query-desk/vulnerable/web/App.vue';
import PaperSession from '../../challenges/paper-session/vulnerable/web/App.vue';
import PathParcel from '../../challenges/path-parcel/vulnerable/web/App.vue';
import ForgottenShelf from '../../challenges/forgotten-shelf/vulnerable/web/App.vue';

const page = vi.hoisted(() => ({ data: {} as unknown }));
vi.mock('../src/page', async () => {
  const { ref } = await import('vue');
  return { usePage: () => ({ data: ref(page.data), loading: ref(false), error: ref('') }), link: (path: string, parameters: Record<string, string>) => `${path}?${new URLSearchParams(parameters)}` };
});
afterEach(() => vi.unstubAllGlobals());
function globals(path = '/') {
  vi.stubGlobal('location', { pathname: path, search: '' });
  vi.stubGlobal('document', { cookie: 'paper_role=guest' });
}
it('shows only backend-authorized notes and escapes note bodies', async () => {
  globals('/notes/1'); page.data = { title: 'Welcome', body: '<script>alert(1)</script>' };
  const html = await renderToString(createSSRApp(NoteVault));
  expect(html).toContain('&lt;script&gt;'); expect(html).not.toContain('<script>');
  globals(); page.data = { user: 'guest', notes: [{ id: 1, title: 'Welcome' }] };
  const home = await renderToString(createSSRApp(NoteVault));
  expect(home).toContain('href="/notes/1"'); expect(home).not.toContain('/notes/2');
});
it('renders SQL results as text and submits the real search parameter', async () => {
  globals(); page.data = { query: 'SELECT', matches: [{ name: 'mira', note: '<img src=x onerror=alert(1)>' }] };
  const html = await renderToString(createSSRApp(QueryDesk));
  expect(html).toContain('name="name"'); expect(html).toContain('&lt;img'); expect(html).not.toContain('<img');
});
it('preserves document history links without placing secret contents in the list', async () => {
  globals('/history'); page.data = { resource: 'locker/team-admin', versions: [{ version: 'r1', title: '첫 작성' }] };
  const html = await renderToString(createSSRApp(BorrowedBadge));
  expect(html).toContain('/version?resource=locker%2Fteam-admin&amp;version=r1');
  expect(html).not.toContain('pwnden{');
});
it('renders the cookie experiment, file lookup and archive clues', async () => {
  globals(); page.data = { role: 'guest' };
  expect(await renderToString(createSSRApp(PaperSession))).toContain('paper_role');
  page.data = { files: ['welcome.txt', 'guide.txt'] };
  expect(await renderToString(createSSRApp(PathParcel))).toContain('/view?file=guide.txt');
  globals('/about'); page.data = { export: 'site-backup.txt', crawler: '/robots.txt' };
  expect(await renderToString(createSSRApp(ForgottenShelf))).toContain('href="/robots.txt"');
});
