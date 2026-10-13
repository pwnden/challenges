<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import TargetPage from '@target/TargetPage.vue';
interface Product { id: string; name: string; price: number; description: string }
interface Order { id: number; name: string; price: number; paid: number; refunded: number; status: string; receipt?: string }
interface Store { balance: number; products: Product[]; orders: Order[]; coupon: { code: string; product: string; percent: number }; notice?: string }
const onOrders = location.pathname === '/orders';
const { data, loading, error } = usePage<Store>(['/', '/orders']);
const ordered = ref(false);
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
    else { data.value = result as Store; feedback.value = result.notice; ordered.value = path === '/api/orders'; }
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
        <h1 class="brand"><a href="/">작은 작업실 상점</a></h1>
        <nav aria-label="상점 메뉴"><a href="/" :aria-current="onOrders ? undefined : 'page'">상품</a><a href="/orders" :aria-current="onOrders ? 'page' : undefined">주문 기록</a></nav>
        <div class="account">
          <p><span>구매 계정 잔액</span><strong class="balance">{{ money(data.balance) }}</strong></p>
          <button class="quiet" :disabled="busy" @click="refresh">현재 상태 확인</button>
          <button class="quiet" :disabled="busy" @click="action('/api/reset', {})">처음부터 다시</button>
        </div>
      </header>
      <p class="notice" :class="{ error: failed }" role="status" aria-live="polite">{{ feedback }}<template v-if="ordered && !failed && !onOrders"> <a href="/orders">주문 기록 보기</a></template></p>
      <main class="content">
        <template v-if="!onOrders">
        <section class="rules" aria-labelledby="rules-title">
          <h2 id="rules-title">구매 안내</h2>
          <dl>
            <div><dt>이번 주 행사</dt><dd>작업용 USB 케이블은 <code>{{ data.coupon.code }}</code> 쿠폰으로 {{ data.coupon.percent }}% 할인합니다. 행사 기간에는 여러 주문에 사용할 수 있습니다. 한정판 상품은 할인 대상이 아닙니다.</dd></div>
            <div><dt>주문 취소</dt><dd>발송 전 주문은 취소할 수 있습니다. 취소하면 결제한 금액을 구매 계정으로 돌려드립니다.</dd></div>
            <div><dt>영수증</dt><dd>한정판 키캡 세트를 구매하면 주문 영수증에 구매 확인 코드가 표시됩니다.</dd></div>
          </dl>
        </section>
        <section id="products" aria-labelledby="products-title">
          <h2 id="products-title">상품</h2>
          <div class="products">
            <form v-for="product in data.products" :key="product.id" class="product" @submit.prevent="action('/api/orders', { product: product.id, coupon: coupons[product.id] ?? '' })">
              <div class="head"><h3>{{ product.name }}</h3><span v-if="product.id === data.coupon.product" class="label">쿠폰 대상</span></div>
              <p class="price">{{ money(product.price) }}</p>
              <p class="desc">{{ product.description }}</p>
              <label :for="`coupon-${product.id}`">쿠폰 (선택)<input :id="`coupon-${product.id}`" v-model="coupons[product.id]" maxlength="32" autocomplete="off" :disabled="busy"></label>
              <button class="primary" :disabled="busy">{{ product.name }} 구매</button>
            </form>
          </div>
        </section>
        </template>
        <section v-else id="orders" aria-labelledby="orders-title">
          <h2 id="orders-title">주문 기록</h2>
          <p v-if="!data.orders.length" class="empty">아직 주문이 없습니다. <a href="/">상품 보기</a></p>
          <template v-else>
            <div class="scroll" role="region" aria-label="주문 기록 표" tabindex="0">
              <table>
                <thead><tr><th scope="col">주문</th><th scope="col">상태</th><th scope="col" class="num">상품 가격</th><th scope="col" class="num">실제 결제액</th><th scope="col" class="num">환불액</th><th scope="col"><span class="visually-hidden">처리</span></th></tr></thead>
                <tbody>
                  <tr v-for="order in data.orders" :key="order.id">
                    <th scope="row">#{{ order.id }} · {{ order.name }}</th>
                    <td>{{ order.status === 'paid' ? '결제 완료' : '취소 완료' }}</td>
                    <td class="num">{{ money(order.price) }}</td>
                    <td class="num">{{ money(order.paid) }}</td>
                    <td class="num">{{ order.status === 'cancelled' ? money(order.refunded) : '–' }}</td>
                    <td><button v-if="order.status === 'paid'" class="quiet" :disabled="busy" @click="action('/api/cancel', { order_id: order.id })">주문 #{{ order.id }} 취소</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-for="order in data.orders.filter(item => item.receipt)" :key="`receipt-${order.id}`" class="receipt">
              <h3>한정판 상품 구매 영수증 · 주문 #{{ order.id }}</h3>
              <p>구매 확인 코드</p>
              <code>{{ order.receipt }}</code>
            </div>
          </template>
        </section>
      </main>
      <footer class="foot">이 상점은 실습용입니다. 실제 결제와 배송은 하지 않습니다.</footer>
    </div>
  </TargetPage>
</template>
<style>
html:root { color-scheme: light; color: #1f1f1c; background: #f6f6f3; }
body { background: #f6f6f3; }
</style>
<style scoped>
.shop { --ink: #1f1f1c; --muted: #55554f; --line: #d4d4cc; --paper: #fff; --tint: #eceae4; --accent: #1c5db3; --accent-dark: #154a91; --danger: #a3201a; max-width: 62rem; margin: 0 auto; padding: 0 var(--inset) 2rem; color: var(--ink); word-break: keep-all; overflow-wrap: break-word; }
.top { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 1.5rem; padding: 0.9rem 0; border-bottom: 1px solid var(--line); background: transparent; }
.brand { margin: 0; font-size: 1.15rem; line-height: 1.4; }
.brand a { color: inherit; text-decoration: none; font-weight: 750; }
nav { display: flex; gap: 1.25rem; }
nav a { color: var(--muted); font-weight: 600; text-underline-offset: 0.3em; }
nav a[aria-current='page'] { color: var(--ink); font-weight: 750; text-decoration-thickness: 2px; text-decoration-color: var(--accent); }
nav a:hover { color: var(--accent-dark); }
.account { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin-left: auto; }
.account p { display: grid; margin: 0 0.5rem 0 0; text-align: right; line-height: 1.35; }
.account span { font-size: 0.8rem; color: var(--muted); }
.balance { font-size: 1.15rem; font-variant-numeric: tabular-nums; }
.notice { min-height: 1.65rem; margin: 0; padding: 0.4rem 0; font-size: 0.95rem; color: #1d6b47; }
.notice.error { color: var(--danger); }
.content { display: grid; grid-template-columns: minmax(0, 1fr); gap: 2rem; max-width: none; margin: 0; padding: 0; }
.content h2 { margin: 0 0 0.75rem; font-size: 1.15rem; }
.content section { padding: 0; border: 0; }
.rules { padding: 1rem 1.1rem !important; background: var(--paper); border: 1px solid var(--line) !important; border-radius: 0.4rem; }
.rules dl { display: grid; gap: 0.5rem; margin: 0; }
.rules dl > div { display: grid; grid-template-columns: 7.5rem minmax(0, 1fr); gap: 0.25rem 1rem; }
.rules dt { font-weight: 700; }
.rules dd { margin: 0; }
code { background: var(--tint); padding: 0.05rem 0.35rem; border-radius: 0.25rem; }
.products { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); gap: 1rem; }
.product { display: grid; grid-template-columns: 1fr; align-items: start; align-content: start; gap: 0.35rem; padding: 1rem 1.1rem; background: var(--paper); border: 1px solid var(--line); border-radius: 0.4rem; }
.head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.5rem; }
.product h3 { margin: 0; font-size: 1.05rem; }
.label { padding: 0 0.5rem; border: 1px solid var(--line); border-radius: 999px; background: var(--tint); font-size: 0.8rem; color: var(--muted); }
.price { margin: 0; font-size: 1.35rem; font-weight: 750; font-variant-numeric: tabular-nums; }
.desc { margin: 0 0 0.35rem; color: var(--muted); font-size: 0.95rem; }
.product label { color: var(--muted); font-size: 0.9rem; }
.shop input { background: var(--paper); color: var(--ink); border-color: #8c8c84; caret-color: var(--accent); }
.shop input::placeholder { color: #6b6b64; }
.shop button { border-radius: 0.4rem; font-weight: 650; }
.shop a { color: var(--accent); }
.shop a:hover { color: var(--accent-dark); }
.shop :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.primary { margin-top: 0.4rem; background: var(--accent); border-color: var(--accent-dark); color: #fff; }
.primary:hover { background: var(--accent-dark); }
.primary:active { background: #0f3a73; }
.quiet { height: 2.25rem; padding: 0 0.75rem; background: var(--paper); border-color: #8c8c84; color: var(--ink); font-size: 0.9rem; }
.quiet:hover { background: var(--tint); }
.shop button:disabled { opacity: 0.6; cursor: wait; }
.empty { margin: 0; padding: 1rem; color: var(--muted); background: var(--paper); border: 1px dashed var(--line); border-radius: 0.4rem; }
.scroll { position: relative; overflow-x: auto; background: var(--paper); border: 1px solid var(--line); border-radius: 0.4rem; }
.scroll:focus-visible { outline-offset: 0; }
.shop table { min-width: 38rem; }
.shop th, .shop td { padding: 0.65rem 0.8rem; border-bottom: 1px solid var(--line); text-align: left; overflow-wrap: normal; word-break: keep-all; }
.shop td:nth-child(2) { white-space: nowrap; }
.shop thead th { color: var(--muted); font-size: 0.85rem; font-weight: 600; white-space: nowrap; background: var(--tint); }
.shop tbody th { font-weight: 650; }
.shop tbody tr:last-child th, .shop tbody tr:last-child td { border-bottom: 0; }
.shop .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.receipt { margin-top: 1rem; padding: 0.9rem 1.1rem; background: var(--paper); border: 1px solid var(--ink); border-radius: 0.4rem; }
.receipt h3 { margin: 0 0 0.25rem; font-size: 1rem; }
.receipt p { margin: 0 0 0.25rem; color: var(--muted); font-size: 0.9rem; }
.receipt code { overflow-wrap: anywhere; font-weight: 700; }
.foot { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.9rem; }
@media (max-width: 40rem) {
  .account { margin-left: 0; width: 100%; }
  .account p { text-align: left; margin-right: auto; }
  .rules dl > div { grid-template-columns: 1fr; }
}
</style>
