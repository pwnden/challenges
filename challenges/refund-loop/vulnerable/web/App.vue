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
  <TargetPage title="작은 작업실 상점" :loading="loading" :error="error">
    <template v-if="data">
      <section class="account">
        <div><h2>내 구매 계정</h2><p>사용 가능한 잔액 <strong class="balance">{{ money(data.balance) }}</strong></p><p>한정판 키캡 세트를 구매하면 주문 영수증에 구매 확인 코드가 표시됩니다.</p></div>
        <div class="account-actions"><button :disabled="busy" @click="refresh">현재 상태 확인</button><button :disabled="busy" @click="action('/api/reset', {})">처음부터 다시</button></div>
      </section>
      <p class="feedback" :class="{ error: failed }" role="status" aria-live="polite">{{ feedback }}</p>
      <section>
        <h2>이번 주 행사</h2><p>작업용 USB 케이블은 <code>{{ data.coupon.code }}</code> 쿠폰으로 {{ data.coupon.percent }}% 할인합니다. 행사 기간에는 여러 주문에 사용할 수 있습니다. 한정판 상품은 할인 대상이 아닙니다.</p>
        <p>발송 전 주문은 취소할 수 있습니다. 취소하면 결제한 금액을 구매 계정으로 돌려드립니다.</p>
      </section>
      <section>
        <h2>상품</h2>
        <div class="products">
          <form v-for="product in data.products" :key="product.id" class="product" @submit.prevent="action('/api/orders', { product: product.id, coupon: coupons[product.id] ?? '' })">
            <div><h3>{{ product.name }}</h3><p class="price">{{ money(product.price) }}</p><p>{{ product.description }}</p></div>
            <label :for="`coupon-${product.id}`">쿠폰 (선택)<input :id="`coupon-${product.id}`" v-model="coupons[product.id]" maxlength="32" autocomplete="off" :disabled="busy"></label>
            <button :disabled="busy">{{ product.name }} 구매</button>
          </form>
        </div>
      </section>
      <section>
        <h2>주문 기록</h2><p v-if="!data.orders.length">아직 주문이 없습니다.</p>
        <ol v-else class="orders">
          <li v-for="order in data.orders" :key="order.id" class="order">
            <div class="order-heading"><h3>주문 #{{ order.id }} · {{ order.name }}</h3><span>{{ order.status === 'paid' ? '결제 완료' : '취소 완료' }}</span></div>
            <dl><div><dt>상품 가격</dt><dd>{{ money(order.price) }}</dd></div><div><dt>실제 결제액</dt><dd>{{ money(order.paid) }}</dd></div><div v-if="order.status === 'cancelled'"><dt>환불액</dt><dd>{{ money(order.refunded) }}</dd></div></dl>
            <div v-if="order.receipt" class="receipt"><h3>한정판 상품 구매 영수증</h3><p>구매 확인 코드</p><code>{{ order.receipt }}</code></div>
            <button v-if="order.status === 'paid'" :disabled="busy" @click="action('/api/cancel', { order_id: order.id })">주문 #{{ order.id }} 취소</button>
          </li>
        </ol>
      </section>
    </template>
  </TargetPage>
</template>
<style scoped>
.account, .order-heading { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: var(--inset); }
.account-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.balance, .price { font-weight: 650; font-variant-numeric: tabular-nums; color: #94c5ff; }
.products { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); gap: var(--inset); }
.product { grid-template-columns: 1fr; align-content: start; padding: var(--inset); background: #182334; border-radius: var(--radius); }
h3 { margin: 0; font-size: 1rem; }
.orders { display: grid; gap: var(--inset); list-style: none; padding: 0; margin: 0; }
.order { padding: var(--inset); border: 1px solid #34455c; border-radius: var(--radius); }
.orders li + li { margin-top: 0; }
dl { display: flex; flex-wrap: wrap; gap: var(--inset); }
dt { color: #a9bed6; font-size: 0.875rem; }
dd { margin: 0; font-variant-numeric: tabular-nums; }
.receipt { padding: var(--inset); margin-bottom: var(--inset); background: #182334; border-radius: var(--radius); }
.receipt code { overflow-wrap: anywhere; }
.feedback { padding: var(--inset); min-height: 5.3rem; margin: 0; }
</style>
