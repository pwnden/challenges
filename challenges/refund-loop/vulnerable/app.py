"""A session-scoped shop with a replaceable refund accounting policy."""
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer
import json
import os
import secrets
from threading import RLock
from urllib.parse import urlsplit

from refund_policy import refund_amount
from web.server import TargetHandler

PRODUCTS = [
    {'id': 'cable', 'name': '작업용 USB 케이블', 'price': 1000,
     'description': '전시 장비에 쓰는 기본 케이블. 행사 할인 대상입니다.'},
    {'id': 'limited', 'name': '한정판 키캡 세트', 'price': 3000,
     'description': '이번 의뢰의 구매 대상. 할인 행사에서 제외됩니다.'},
]
SESSIONS = {}
LOCK = RLock()


class Shop:
    def __init__(self):
        self.balance = 1000
        self.orders = []

    def snapshot(self):
        orders = [dict(order) for order in reversed(self.orders)]
        for order in orders:
            if order['product'] == 'limited' and order['status'] == 'paid':
                order['receipt'] = os.environ['FLAG']
        return {'balance': self.balance, 'products': PRODUCTS, 'orders': orders,
                'coupon': {'code': 'CABLE50', 'product': 'cable', 'percent': 50}}

    def buy(self, product, coupon):
        item = next((item for item in PRODUCTS if item['id'] == product), None)
        if not item:
            raise ValueError('상품을 찾을 수 없습니다.')
        if not isinstance(coupon, str) or coupon not in ('', 'CABLE50'):
            raise ValueError('등록된 쿠폰을 입력하세요.')
        if coupon and product != 'cable':
            raise ValueError('이 상품은 할인 대상이 아닙니다.')
        if len(self.orders) >= 64:
            raise ValueError('주문 기록이 가득 찼습니다. 처음부터 다시 시작하세요.')
        paid = item['price'] // 2 if coupon else item['price']
        if paid > self.balance:
            raise ValueError('잔액이 부족합니다.')
        self.balance -= paid
        self.orders.append({'id': len(self.orders) + 1, 'product': product,
                            'name': item['name'], 'price': item['price'], 'paid': paid,
                            'refunded': 0, 'status': 'paid'})

    def cancel(self, order_id):
        order = next((order for order in self.orders if order['id'] == order_id), None)
        if not order:
            raise ValueError('주문을 찾을 수 없습니다.')
        if order['status'] != 'paid':
            raise ValueError('이미 취소한 주문입니다.')
        order['refunded'] = refund_amount(order)
        order['status'] = 'cancelled'
        self.balance += order['refunded']


class Handler(TargetHandler):
    def session(self):
        cookie = SimpleCookie()
        cookie.load(self.headers.get('Cookie', ''))
        sid = cookie.get('shop_sid')
        return sid.value if sid else ''

    def do_GET(self):
        if self.assets():
            return
        path = urlsplit(self.path).path
        if path == '/healthz':
            self.send(200, 'ok')
        elif path in ('/', '/api/shop'):
            with LOCK:
                sid = self.session()
                cookies = ()
                if sid not in SESSIONS:
                    sid = secrets.token_hex(24)
                    SESSIONS[sid] = Shop()
                    cookies = ('shop_sid=' + sid + '; HttpOnly; Path=/; SameSite=Lax',)
                self.page(200, SESSIONS[sid].snapshot(), cookies)
        else:
            self.send(404, '페이지를 찾을 수 없습니다.')

    def do_POST(self):
        with LOCK:
            shop = SESSIONS.get(self.session())
            if shop is None:
                self.page(401, {'error': '상점을 다시 열어 구매 계정을 준비하세요.'})
                return
            path = urlsplit(self.path).path
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 4096:
                    raise ValueError('요청 크기를 확인하세요.')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('요청 형식을 확인하세요.')
                if path == '/api/orders':
                    shop.buy(body.get('product'), body.get('coupon', ''))
                    notice = '구매했습니다. 주문 기록에서 결제 내용을 확인하세요.'
                elif path == '/api/cancel':
                    if type(body.get('order_id')) is not int:
                        raise ValueError('주문 번호를 확인하세요.')
                    shop.cancel(body['order_id'])
                    notice = '주문을 취소했습니다. 환불액을 확인하세요.'
                elif path == '/api/reset':
                    shop = SESSIONS[self.session()] = Shop()
                    notice = '잔액과 주문 기록을 처음 상태로 돌렸습니다.'
                else:
                    self.page(404, {'error': '기능을 찾을 수 없습니다.'})
                    return
            except (ValueError, TypeError) as error:
                self.page(400, {'error': str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else '요청 형식을 확인하세요.'})
                return
            self.page(200, {**shop.snapshot(), 'notice': notice})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
