<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
interface Product { id: string; name: string; price: number; description: string }
interface Order { id: number; name: string; price: number; paid: number; refunded: number; status: string; receipt?: string }
interface Store { balance: number; products: Product[]; orders: Order[]; coupon: { code: string; product: string; percent: number }; notice?: string }
const { data, loading, error } = usePage<Store>();
const coupons = ref<Record<string, string>>({});
const busy = ref(false);
const feedback = ref('');
const failed = ref(false);
const money = (value: number) => `${value.toLocaleString('ko-KR')}원`;
async function action(path: string, body: Record<string, unknown>) {
  if (busy.value) return;
  busy.value = true; failed.value = false; feedback.value = '';
  try {
    const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const result = await response.json();
    if (!response.ok) { failed.value = true; feedback.value = result.error; }
    else { data.value = result as Store; feedback.value = result.notice; }
  } catch { failed.value = true; feedback.value = '처리 결과를 확인하지 못했습니다. 현재 상태를 다시 확인한 뒤 시도하세요.'; }
  finally { busy.value = false; }
}
async function refresh() {
  if (busy.value) return;
  busy.value = true;
  try {
    const response = await fetch('/api/shop', { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('connection');
    data.value = await response.json(); feedback.value = '현재 잔액과 주문 기록을 확인했습니다.'; failed.value = false;
  } catch { feedback.value = '상점 연결을 확인하고 다시 시도하세요.'; failed.value = true; }
  finally { busy.value = false; }
}
</script>
<template>
  <TargetPage bare title="작은 작업실 상점" :loading="loading" :error="error">
    <div v-if="data" class="shop">
      <header class="top">
        <h1 class="brand"><a href="/" aria-label="작은 작업실 상점 처음으로">
          <svg viewBox="0 0 40 40" aria-hidden="true"><rect x="2" y="2" width="36" height="36" rx="10" fill="#b8652f"/><rect x="9" y="8" width="22" height="20" rx="5" fill="#f6d9bd"/><rect x="12" y="11" width="16" height="12" rx="3" fill="#fff4e6"/><rect x="9" y="30" width="22" height="3" rx="1.5" fill="#f6d9bd"/></svg>
          <span><strong>작은 작업실 상점</strong><small>전시 장비와 키보드 소품</small></span>
        </a></h1>
        <nav aria-label="상점 메뉴"><a href="#deal">이번 주 행사</a><a href="#products">상품</a><a href="#orders">주문 기록</a></nav>
        <div class="account">
          <p>내 구매 계정<strong class="balance">사용 가능한 잔액 {{ money(data.balance) }}</strong></p>
          <div class="account-actions"><button class="ghost" :disabled="busy" @click="refresh">현재 상태 확인</button><button class="ghost" :disabled="busy" @click="action('/api/reset', {})">처음부터 다시</button></div>
        </div>
      </header>
      <p class="notice" :class="{ error: failed, active: feedback }" role="status" aria-live="polite">{{ feedback }}</p>
      <main class="content">
        <section id="deal" class="deal">
          <div class="deal-text">
            <p class="eyebrow">이번 주 행사</p>
            <h2>작업용 USB 케이블 <em>{{ data.coupon.percent }}% 할인</em></h2>
            <p><code class="coupon">{{ data.coupon.code }}</code> 쿠폰으로 작업용 USB 케이블을 {{ data.coupon.percent }}% 할인합니다. 행사 기간에는 여러 주문에 사용할 수 있습니다. 한정판 상품은 할인 대상이 아닙니다.</p>
            <p>발송 전 주문은 취소할 수 있습니다. 취소하면 결제한 금액을 구매 계정으로 돌려드립니다.</p>
            <p class="hint">한정판 키캡 세트를 구매하면 주문 영수증에 구매 확인 코드가 표시됩니다.</p>
          </div>
          <svg class="deal-art" viewBox="0 0 220 140" aria-hidden="true"><rect width="220" height="140" rx="18" fill="#f6d9bd"/><path d="M28 98 C 70 30, 100 120, 150 62 S 190 46, 196 40" fill="none" stroke="#7a4426" stroke-width="7" stroke-linecap="round"/><rect x="14" y="88" width="30" height="22" rx="5" fill="#2a2118"/><rect x="184" y="28" width="26" height="22" rx="5" fill="#2a2118"/><circle cx="170" cy="112" r="20" fill="#b8652f"/><text x="170" y="118" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">50%</text></svg>
        </section>
        <section id="products" class="block">
          <h2>상품</h2>
          <div class="products">
            <form v-for="product in data.products" :key="product.id" class="product" @submit.prevent="action('/api/orders', { product: product.id, coupon: coupons[product.id] ?? '' })">
              <div class="art" :class="product.id" aria-hidden="true">
                <svg v-if="product.id === 'cable'" viewBox="0 0 160 100"><path d="M26 72 C 60 20, 84 96, 120 40" fill="none" stroke="#7a4426" stroke-width="6" stroke-linecap="round"/><rect x="12" y="64" width="24" height="18" rx="4" fill="#2a2118"/><rect x="112" y="28" width="22" height="18" rx="4" fill="#2a2118"/></svg>
                <svg v-else viewBox="0 0 160 100"><g fill="#fff4e6" stroke="#2a2118" stroke-width="3"><rect x="18" y="22" width="40" height="40" rx="9"/><rect x="66" y="22" width="40" height="40" rx="9"/><rect x="114" y="22" width="30" height="40" rx="9"/><rect x="18" y="68" width="88" height="20" rx="8"/></g><g fill="#b8652f"><rect x="26" y="30" width="24" height="18" rx="5"/><rect x="74" y="30" width="24" height="18" rx="5"/></g></svg>
                <span class="tag" :class="{ limited: product.id !== 'cable' }">{{ product.id === 'cable' ? '행사 상품' : '한정판' }}</span>
              </div>
              <div class="info"><h3>{{ product.name }}</h3><p class="price">{{ money(product.price) }}</p><p class="desc">{{ product.description }}</p></div>
              <label :for="`coupon-${product.id}`">쿠폰 (선택)<input :id="`coupon-${product.id}`" v-model="coupons[product.id]" maxlength="32" autocomplete="off" placeholder="쿠폰 코드" :disabled="busy"></label>
              <button class="primary" :disabled="busy">{{ product.name }} 구매</button>
            </form>
          </div>
        </section>
        <section id="orders" class="block">
          <h2>주문 기록</h2>
          <p v-if="!data.orders.length" class="empty">아직 주문이 없습니다.</p>
          <ol v-else class="orders">
            <li v-for="order in data.orders" :key="order.id" class="order">
              <div class="order-heading"><h3>주문 #{{ order.id }} · {{ order.name }}</h3><span class="status" :class="order.status">{{ order.status === 'paid' ? '결제 완료' : '취소 완료' }}</span></div>
              <dl><div><dt>상품 가격</dt><dd>{{ money(order.price) }}</dd></div><div><dt>실제 결제액</dt><dd>{{ money(order.paid) }}</dd></div><div v-if="order.status === 'cancelled'"><dt>환불액</dt><dd>{{ money(order.refunded) }}</dd></div></dl>
              <div v-if="order.receipt" class="receipt"><h4>한정판 상품 구매 영수증</h4><p>구매 확인 코드</p><code>{{ order.receipt }}</code></div>
              <button v-if="order.status === 'paid'" class="outline" :disabled="busy" @click="action('/api/cancel', { order_id: order.id })">주문 #{{ order.id }} 취소</button>
            </li>
          </ol>
        </section>
      </main>
      <footer class="foot">작은 작업실 상점은 실습용 사이트입니다. 실제 결제나 배송은 이루어지지 않습니다.</footer>
    </div>
  </TargetPage>
</template>
<style>
html:root { color-scheme: light; color: #2a2118; background: #fbf7f0; }
body { background: #fbf7f0; }
</style>
<style scoped>
.shop { --ink: #2a2118; --muted: #6f6254; --line: #e6dccd; --paper: #fff; --brand: #b8652f; --brand-dark: #8f4a1f; --soft: #f6ede0; max-width: 64rem; margin: 0 auto; padding: 0 var(--inset) 2rem; color: var(--ink); }
.top { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem 1.5rem; padding: 1rem 0; border-bottom: 1px solid var(--line); background: transparent; }
.brand { margin: 0; font-size: 1rem; line-height: 1.3; }
.brand a { display: flex; align-items: center; gap: 0.75rem; color: inherit; text-decoration: none; }
.brand svg { width: 2.5rem; height: 2.5rem; flex: none; }
.brand strong { display: block; font-size: 1.15rem; line-height: 1.3; }
.brand small { color: var(--muted); font-size: 0.8rem; }
nav { display: flex; flex-wrap: wrap; gap: 0.25rem 1rem; margin-inline: auto; }
nav a { color: var(--muted); text-decoration: none; font-weight: 600; padding: 0.25rem 0.1rem; border-bottom: 2px solid transparent; }
nav a:hover { color: var(--brand-dark); border-bottom-color: var(--brand); }
.account { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 0.75rem; }
.account p { margin: 0; font-size: 0.8rem; color: var(--muted); line-height: 1.4; }
.balance { display: block; color: var(--brand-dark); font-size: 1rem; font-variant-numeric: tabular-nums; }
.account-actions { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.notice { margin: 0; padding: 0.4rem 0; min-height: 1.65rem; font-size: 0.9rem; color: #2f6f55; }
.notice.error { color: #b3261e; }
.content { display: grid; gap: 1.75rem; max-width: none; margin: 0; padding: 0; }
.deal { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 14rem); gap: 1.5rem; align-items: center; padding: 1.5rem; margin-top: 0.5rem; background: var(--soft); border: 1px solid var(--line); border-radius: 1rem; }
.deal h2 { margin: 0 0 0.75rem; font-size: 1.6rem; line-height: 1.3; }
.deal h2 em { font-style: normal; color: var(--brand-dark); }
.deal p { margin-bottom: 0.5rem; }
.eyebrow { margin: 0 0 0.25rem; color: var(--brand-dark); font-weight: 700; font-size: 0.85rem; letter-spacing: 0.02em; }
.coupon { background: var(--paper); border: 1px dashed var(--brand); border-radius: 0.35rem; padding: 0.05rem 0.4rem; font-weight: 700; color: var(--brand-dark); }
.hint { color: var(--muted); font-size: 0.9rem; }
.deal-art { width: 100%; height: auto; }
.block { padding: 0; border: 0; }
.block h2 { margin: 0 0 0.9rem; font-size: 1.25rem; }
.products { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); gap: 1.25rem; }
.product { display: grid; grid-template-columns: 1fr; align-items: start; align-content: start; gap: 0.75rem; padding: 0; background: var(--paper); border: 1px solid var(--line); border-radius: 1rem; overflow: hidden; box-shadow: 0 1px 2px rgba(42, 33, 24, 0.06); }
.art { position: relative; display: grid; place-items: center; height: 9rem; background: var(--soft); }
.art.limited, .art.keycaps { background: #efe3f6; }
.art svg { width: 9.5rem; height: auto; }
.tag { position: absolute; top: 0.6rem; left: 0.6rem; padding: 0.1rem 0.55rem; border-radius: 999px; background: var(--brand); color: #fff; font-size: 0.75rem; font-weight: 700; }
.tag.limited { background: #2a2118; color: #f6d9bd; }
.info, .product label, .product button { margin-inline: 1rem; }
.product button { margin-bottom: 1rem; }
.info h3 { margin: 0; font-size: 1.05rem; }
.price { margin: 0.1rem 0 0.35rem; font-size: 1.3rem; font-weight: 750; font-variant-numeric: tabular-nums; }
.desc { margin: 0; color: var(--muted); font-size: 0.9rem; }
.product label { color: var(--muted); font-size: 0.85rem; }
.shop input { background: var(--paper); color: var(--ink); border-color: #cdbfae; caret-color: var(--brand); }
.shop input::placeholder { color: #a39485; }
.shop input:focus-visible, .shop button:focus-visible, .shop a:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
.shop button { border-radius: 0.6rem; font-weight: 650; }
.primary { background: var(--brand); border-color: var(--brand-dark); color: #fff; }
.primary:hover { background: var(--brand-dark); }
.primary:active { background: #6f3817; }
.ghost { background: var(--paper); border-color: #cdbfae; color: var(--ink); height: 2.25rem; padding: 0 0.75rem; font-size: 0.85rem; }
.ghost:hover { background: var(--soft); }
.outline { background: var(--paper); border-color: #b3261e; color: #b3261e; }
.outline:hover { background: #fdecea; }
.shop button:disabled { opacity: 0.55; cursor: wait; }
.empty { padding: 1.25rem; margin: 0; color: var(--muted); background: var(--paper); border: 1px dashed var(--line); border-radius: 1rem; text-align: center; }
.orders { display: grid; gap: 1rem; list-style: none; padding: 0; margin: 0; }
.order { display: grid; gap: 0.75rem; padding: 1rem 1.1rem; background: var(--paper); border: 1px solid var(--line); border-radius: 1rem; }
.orders li + li { margin-top: 0; }
.order-heading { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.5rem; }
.order h3 { margin: 0; font-size: 1rem; }
.status { padding: 0.1rem 0.6rem; border-radius: 999px; font-size: 0.8rem; font-weight: 700; background: #e3f2ea; color: #1f5a40; }
.status.cancelled { background: #eee7dc; color: #5b4f41; }
dl { display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 0; }
dl div { min-width: 8rem; padding: 0.55rem 0.8rem; background: var(--soft); border-radius: 0.6rem; }
dt { color: var(--muted); font-size: 0.8rem; }
dd { margin: 0; font-weight: 700; font-variant-numeric: tabular-nums; }
.receipt { padding: 0.9rem 1rem; border: 2px dashed var(--brand); border-radius: 0.8rem; background: #fffaf3; }
.receipt h4 { margin: 0 0 0.25rem; font-size: 0.95rem; }
.receipt p { margin: 0 0 0.25rem; color: var(--muted); font-size: 0.85rem; }
.receipt code { overflow-wrap: anywhere; font-weight: 700; color: var(--brand-dark); }
.order button { justify-self: start; }
.foot { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.85rem; text-align: center; }
@media (max-width: 40rem) {
  nav { margin-inline: 0; order: 3; width: 100%; }
  .deal { grid-template-columns: 1fr; }
  .deal-art { max-width: 12rem; }
}
</style>
