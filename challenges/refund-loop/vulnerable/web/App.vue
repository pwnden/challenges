<script setup lang="ts">
import { ref } from 'vue';
import { usePage } from '@target/page';
import { FormRoot } from '@target/sectile';
import Field from '@target/Field.vue';
import SiteHeader from '@target/SiteHeader.vue';
import SubmitButton from '@target/SubmitButton.vue';
import TargetPage from '@target/TargetPage.vue';
import Toaster from '@target/Toaster.vue';
import { postJson, useAction } from '@target/useAction';
interface Product { id: string; name: string; price: number; description: string }
interface Order { id: number; name: string; price: number; paid: number; refunded: number; status: string; receipt?: string }
interface Store { balance: number; products: Product[]; orders: Order[]; coupon: { code: string; product: string; percent: number }; notice?: string }
const onOrders = location.pathname === '/orders';
const { data, loading, error } = usePage<Store>(['/', '/orders']);
const { busy, toasts, notify, run } = useAction();
const ordered = ref(false);
const money = (value: number) => `${value.toLocaleString('ko-KR')}원`;
const action = (path: string, body: Record<string, unknown>) => run(async () => {
  const { ok, result } = await postJson<Store>(path, body);
  if (!ok) return notify('error', result.error ?? '요청을 처리하지 못했습니다.');
  data.value = result; ordered.value = path === '/api/orders'; notify('success', result.notice ?? '');
});
const refresh = () => run(async () => {
  const response = await fetch('/api/shop', { headers: { Accept: 'application/json' } });
  if (!response.ok) return notify('error', '상점 연결을 확인하고 다시 시도하세요.');
  data.value = await response.json(); notify('success', '현재 잔액과 주문 기록을 확인했습니다.');
}, '상점 연결을 확인하고 다시 시도하세요.');
</script>
<template>
  <TargetPage bare title="작은 작업실 상점" :loading="loading" :error="error">
    <div v-if="data" class="shop">
      <SiteHeader title="작은 작업실 상점">
        <template #nav><a href="/" :aria-current="onOrders ? undefined : 'page'">상품</a><a href="/orders" :aria-current="onOrders ? 'page' : undefined">주문 기록</a></template>
        <template #actions>
          <p class="balance-box"><span>구매 계정 잔액</span><strong class="balance">{{ money(data.balance) }}</strong></p>
          <button class="small" :disabled="busy" @click="refresh">현재 상태 확인</button>
          <button class="small" :disabled="busy" @click="action('/api/reset', {})">처음부터 다시</button>
        </template>
      </SiteHeader>
      <Toaster v-model:toasts="toasts"><template #extra="{ item }"><a v-if="item.kind === 'success' && ordered && !onOrders" href="/orders">주문 기록 보기</a></template></Toaster>
      <main class="content">
        <template v-if="!onOrders">
          <section aria-labelledby="rules-title">
            <h2 id="rules-title">구매 안내</h2>
            <dl>
              <div><dt>이번 주 행사</dt><dd>작업용 USB 케이블은 <code>{{ data.coupon.code }}</code> 쿠폰으로 {{ data.coupon.percent }}% 할인합니다. 행사 기간에는 여러 주문에 사용할 수 있습니다. 한정판 상품은 할인 대상이 아닙니다.</dd></div>
              <div><dt>주문 취소</dt><dd>발송 전 주문은 취소할 수 있습니다. 취소하면 결제한 금액을 구매 계정으로 돌려드립니다.</dd></div>
              <div><dt>영수증</dt><dd>한정판 키캡 세트를 구매하면 주문 영수증에 구매 확인 코드가 표시됩니다.</dd></div>
            </dl>
          </section>
          <section id="products" class="plain" aria-labelledby="products-title">
            <h2 id="products-title">상품</h2>
            <div class="products">
              <FormRoot v-for="product in data.products" :key="product.id" class="card product" :on-submit="event => action('/api/orders', { product: product.id, coupon: String(event.values.coupon ?? '') })">
                <div class="head"><h3>{{ product.name }}</h3><span v-if="product.id === data.coupon.product" class="label">쿠폰 대상</span></div>
                <p class="price">{{ money(product.price) }}</p>
                <p class="desc">{{ product.description }}</p>
                <Field :id="`coupon-${product.id}`" name="coupon" label="쿠폰 (선택)" maxlength="32" autocomplete="off" :disabled="busy" />
                <SubmitButton variant="primary" :disabled="busy">{{ product.name }} 구매</SubmitButton>
              </FormRoot>
            </div>
          </section>
        </template>
        <section v-else id="orders" class="plain" aria-labelledby="orders-title">
          <h2 id="orders-title">주문 기록</h2>
          <p v-if="!data.orders.length" class="empty">아직 주문이 없습니다. <a href="/">상품 보기</a></p>
          <template v-else>
            <div class="scroll" role="region" aria-label="주문 기록 표" tabindex="0">
              <table>
                <thead><tr><th scope="col">주문</th><th scope="col">상태</th><th scope="col" class="num">상품 가격</th><th scope="col" class="num">실제 결제액</th><th scope="col" class="num">환불액</th><th scope="col"><span class="visually-hidden">처리</span></th></tr></thead>
                <tbody>
                  <tr v-for="order in data.orders" :key="order.id">
                    <th scope="row">#{{ order.id }} · {{ order.name }}</th>
                    <td class="status">{{ order.status === 'paid' ? '결제 완료' : '취소 완료' }}</td>
                    <td class="num">{{ money(order.price) }}</td>
                    <td class="num">{{ money(order.paid) }}</td>
                    <td class="num">{{ order.status === 'cancelled' ? money(order.refunded) : '–' }}</td>
                    <td><button v-if="order.status === 'paid'" class="small" :disabled="busy" @click="action('/api/cancel', { order_id: order.id })">주문 #{{ order.id }} 취소</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-for="order in data.orders.filter(item => item.receipt)" :key="`receipt-${order.id}`" class="card receipt">
              <h3>한정판 상품 구매 영수증 · 주문 #{{ order.id }}</h3>
              <p class="muted">구매 확인 코드</p>
              <code>{{ order.receipt }}</code>
            </div>
          </template>
        </section>
      </main>
    </div>
  </TargetPage>
</template>
<style scoped>
.shop { max-width: 62rem; margin: 0 auto; padding: 0 var(--inset) 2rem; }
.balance-box { display: grid; margin: 0 0.5rem 0 0; text-align: right; line-height: 1.35; }
.balance-box span { font-size: 0.8rem; color: var(--muted); }
.balance { font-size: 1.15rem; font-variant-numeric: tabular-nums; }
.content { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; max-width: none; margin: 0; padding: 0; }
.content section { margin: 0; }
dl { display: grid; gap: 0.5rem; margin: 0; }
dl > div { display: grid; grid-template-columns: 7.5rem minmax(0, 1fr); gap: 0.25rem 1rem; }
dt { font-weight: 700; }
dd { margin: 0; }
.products { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); gap: 1rem; }
.product { grid-template-columns: 1fr; align-items: start; align-content: start; gap: 0.35rem; margin: 0; }
.head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.5rem; }
.label { padding: 0 0.5rem; border: 1px solid var(--line); border-radius: 999px; background: var(--tint); font-size: 0.8rem; color: var(--muted); }
.price { margin: 0; font-size: 1.35rem; font-weight: 750; font-variant-numeric: tabular-nums; }
.desc { margin: 0 0 0.35rem; color: var(--muted); font-size: 0.95rem; }
.product button { margin-top: 0.4rem; }
.empty { padding: 1rem; color: var(--muted); background: var(--paper); border: 1px dashed var(--line); border-radius: var(--radius); }
table { min-width: 38rem; }
.status { white-space: nowrap; }
.receipt { margin: 1rem 0 0; border-color: var(--ink); }
.receipt code { font-weight: 700; }
@media (max-width: 40rem) { dl > div { grid-template-columns: 1fr; } }
</style>
