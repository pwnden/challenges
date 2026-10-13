import { afterEach, expect, it, vi } from 'vitest';
import { createSSRApp, ref } from 'vue';
import { renderToString } from '@vue/server-renderer';
import NoteVault from '../../challenges/note-vault/vulnerable/web/App.vue';
import BorrowedBadge from '../../challenges/borrowed-badge/vulnerable/web/App.vue';
import QueryDesk from '../../challenges/query-desk/vulnerable/web/App.vue';
import PaperSession from '../../challenges/paper-session/vulnerable/web/App.vue';
import PathParcel from '../../challenges/path-parcel/vulnerable/web/App.vue';
import ForgottenShelf from '../../challenges/forgotten-shelf/vulnerable/web/App.vue';
import RefundLoop from '../../challenges/refund-loop/vulnerable/web/App.vue';
import TicketBridge from '../../challenges/ticket-bridge/vulnerable/web/App.vue';
import LapRecord from '../../challenges/lap-record/vulnerable/web/App.vue';

const page = vi.hoisted(() => ({ data: {} as unknown }));
vi.mock('../src/page', async () => {
  const { ref } = await import('vue');
  return { navigationError: ref(''), pagePending: ref(false), usePage: () => ({ data: ref(page.data), loading: ref(false), error: ref('') }), link: (path: string, parameters: Record<string, string>) => `${path}?${new URLSearchParams(parameters)}` };
});
afterEach(() => vi.unstubAllGlobals());
function globals(path = '/') {
  vi.stubGlobal('location', { pathname: path, search: '' });
  vi.stubGlobal('document', { cookie: 'paper_role=guest' });
}
it('shows the product page and renders receipts only on the order page from completed backend orders', async () => {
  globals();
  const shop = { balance: 1000, products: [{ id: 'cable', name: '케이블', price: 1000, description: '행사 상품' }], coupon: { code: 'CABLE50', product: 'cable', percent: 50 }, orders: [] as unknown[] };
  page.data = shop;
  const products = await renderToString(createSSRApp(RefundLoop));
  expect(products).toContain('1,000원');
  expect(products).toContain('CABLE50');
  expect(products).toContain('coupon-cable');
  expect(products).toContain('href="/orders"');
  expect(products).not.toContain('pwnden{');
  expect(products).not.toContain('id="orders"');
  globals('/orders');
  const empty = await renderToString(createSSRApp(RefundLoop));
  expect(empty).toContain('아직 주문이 없습니다.');
  expect(empty).not.toContain('coupon-cable');
  page.data = { ...shop, balance: 0, orders: [{ id: 5, name: '한정판 키캡', price: 3000, paid: 3000, refunded: 0, status: 'paid', receipt: 'pwnden{receipt}' }] };
  const purchased = await renderToString(createSSRApp(RefundLoop));
  expect(purchased).toContain('pwnden{receipt}');
  expect(purchased).toContain('주문 #5 취소');
  page.data = { ...shop, orders: [{ id: 1, name: '케이블', price: 1000, paid: 500, refunded: 1000, status: 'cancelled' }] };
  const cancelled = await renderToString(createSSRApp(RefundLoop));
  expect(cancelled).toContain('환불액');
  expect(cancelled).toContain('500원');
  expect(cancelled).not.toContain('주문 #1 취소');
});
it('shows support controls and renders the staff confirmation only from the backend response', async () => {
  globals();
  page.data = { user: 'member', role: 'member', tickets: [{ id: 310, title: '전시 안내 수정' }] };
  const html = await renderToString(createSSRApp(TicketBridge));
  expect(html).toContain('일반 회원');
  expect(html).toContain('#310 · 전시 안내 수정');
  expect(html).toContain('운영 초대');
  expect(html).toContain('운영 화면 열기');
  expect(html).not.toContain('pwnden{');
  expect(html).not.toContain('초대 코드 <code');
  page.data = { user: 'member', role: 'staff', tickets: [] };
  const promoted = await renderToString(createSSRApp(TicketBridge));
  expect(promoted).toContain('운영 담당자');
  expect(promoted).not.toContain('pwnden{');
});
it('shows the star run rules and the board, and renders the trophy only from backend state', async () => {
  globals();
  const track = { rules: { stars: 6, segment_m: 20, max_speed: 10 }, leaderboard: [{ name: '바람개비', time_ms: 12640, mine: false }], best_ms: null as number | null };
  page.data = track;
  const initial = await renderToString(createSSRApp(LapRecord));
  expect(initial).toContain('별이 6개');
  expect(initial).toContain('12.64초');
  expect(initial).toContain('달리기 시작');
  expect(initial).not.toContain('pwnden{');
  expect(initial).not.toContain('class="card trophy"');
  page.data = { ...track, best_ms: 6000, leaderboard: [{ name: '나', time_ms: 6000, mine: true }, ...track.leaderboard], trophy: 'pwnden{trophy}' };
  const earned = await renderToString(createSSRApp(LapRecord));
  expect(earned).toContain('6.00초');
  expect(earned).toContain('class="card trophy"');
  expect(earned).toContain('pwnden{trophy}');
});
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
