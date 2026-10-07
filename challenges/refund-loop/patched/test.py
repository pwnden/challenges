"""Preserve purchases and cancellation while denying inflated refunds."""
import runpy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

Client = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'solve/solve.py'))['Client']


def check():
    client = Client()
    assert client.request('/api/shop')[1]['balance'] == 1000
    for coupon, paid in (('', 1000), ('CABLE50', 500), ('CABLE50', 500)):
        status, state = client.request('/api/orders', {'product': 'cable', 'coupon': coupon})
        assert status == 200 and state['balance'] == 1000 - paid
        order_id = state['orders'][0]['id']
        status, state = client.request('/api/cancel', {'order_id': order_id})
        assert status == 200 and state['balance'] == 1000
        assert state['orders'][0]['refunded'] == paid
        assert client.request('/api/cancel', {'order_id': order_id})[0] == 400
    for body in ({'product': 'limited'}, {'product': 'limited', 'coupon': 'CABLE50'},
                 {'product': 'cable', 'coupon': 'invalid'}, {'product': 'missing'},
                 {'product': 'cable', 'coupon': []}):
        assert client.request('/api/orders', body)[0] == 400
    assert client.request('/api/cancel', {'order_id': -1})[0] == 400
    assert client.request('/api/cancel', {'order_id': True})[0] == 400
    assert client.request('/api/shop')[1]['balance'] == 1000
    status, state = client.request('/api/orders', {'product': 'cable', 'coupon': 'CABLE50'})
    assert status == 200
    order_id = state['orders'][0]['id']
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(lambda _: client.request('/api/cancel', {'order_id': order_id})[0], range(2)))
    assert sorted(statuses) == [200, 400]
    assert client.request('/api/shop')[1]['balance'] == 1000
    assert client.request('/api/reset', {})[1]['orders'] == []
    assert client.request('/api/shop')[1]['balance'] == 1000
    print('purchases, discounts, cancellation and reset work; refunds equal actual payments')


if __name__ == '__main__':
    check()
