"""Session-isolated star-run game with a record board; no external accounts."""
from http.cookies import CookieError, SimpleCookie
from http.server import ThreadingHTTPServer
import json
import os
import secrets
from threading import RLock
import time
from urllib.parse import urlsplit

from policy import recorded_time
from web.server import TargetHandler

STARS = 6
SEGMENT_METERS = 20
MAX_SPEED = 10
MIN_GAP_MS = SEGMENT_METERS * 1000 // MAX_SPEED
LIMIT_MS = STARS * MIN_GAP_MS
RIVALS = [('바람개비', 12640), ('도토리', 13410), ('구름', 15230), ('솜사탕', 18940)]
SESSIONS = {}
LOCK = RLock()


def is_int(value):
    return type(value) is int


class Track:
    def __init__(self):
        self.runs = {}
        self.next_run = 1
        self.best = None

    def start(self):
        number = self.next_run
        self.next_run += 1
        self.runs[number] = {'start': time.monotonic(), 'marks': [], 'done': False}
        return number

    @staticmethod
    def elapsed(run):
        return int((time.monotonic() - run['start']) * 1000)

    def snapshot(self):
        rows = [{'name': name, 'time_ms': value, 'mine': False} for name, value in RIVALS]
        if self.best is not None:
            rows.append({'name': '나', 'time_ms': self.best, 'mine': True})
        rows.sort(key=lambda row: row['time_ms'])
        data = {'rules': {'stars': STARS, 'segment_m': SEGMENT_METERS, 'max_speed': MAX_SPEED},
                'leaderboard': rows, 'best_ms': self.best}
        if self.best is not None and self.best < LIMIT_MS:
            data['trophy'] = os.environ['FLAG']
        return data


def valid_report(report):
    if not isinstance(report, list) or len(report) != STARS:
        return False
    previous = 0
    for number, entry in enumerate(report, 1):
        if not isinstance(entry, dict) or entry.get('id') != number or not is_int(entry.get('id')):
            return False
        value = entry.get('t_ms')
        if not is_int(value) or not previous < value <= 600000:
            return False
        previous = value
    return True


class Handler(TargetHandler):
    def log_message(self, *_):
        pass

    def session(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
        except CookieError:
            return ''
        sid = cookie.get('lap_sid')
        return sid.value if sid else ''

    def do_GET(self):
        if self.assets():
            return
        path = urlsplit(self.path).path
        if path == '/healthz':
            self.send(200, 'ok')
            return
        if path not in ('/', '/api/track'):
            self.page(404, {'error': '페이지를 찾을 수 없습니다.'})
            return
        with LOCK:
            track = SESSIONS.get(self.session())
            cookies = ()
            if track is None:
                sid = secrets.token_hex(24)
                track = SESSIONS[sid] = Track()
                cookies = ('lap_sid=' + sid + '; HttpOnly; Path=/; SameSite=Lax',)
            self.page(200, track.snapshot(), cookies)

    def body(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 4096:
                raise ValueError
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (ValueError, UnicodeError):
            self.page(400, {'error': '요청 형식을 확인하세요.'})
            return None

    def do_POST(self):
        with LOCK:
            sid = self.session()
            track = SESSIONS.get(sid)
            if track is None:
                self.page(401, {'error': '첫 화면에서 시험 게임을 준비하세요.'})
                return
            data = self.body()
            if data is None:
                return
            path = urlsplit(self.path).path
            if path == '/api/run/start':
                self.page(200, {'run_id': track.start()})
            elif path == '/api/run/checkpoint':
                self.checkpoint(track, data)
            elif path == '/api/run/finish':
                self.finish(track, data)
            elif path == '/api/reset':
                SESSIONS[sid] = Track()
                self.page(200, {**SESSIONS[sid].snapshot(), 'notice': '시험 게임을 처음 상태로 돌렸습니다.'})
            else:
                self.page(404, {'error': '기능을 찾을 수 없습니다.'})

    def find_run(self, track, data):
        run_id = data.get('run_id')
        run = track.runs.get(run_id) if is_int(run_id) else None
        if run is None:
            self.page(404, {'error': '달리기를 찾을 수 없습니다. 새로 시작하세요.'})
        elif run['done']:
            self.page(409, {'error': '이미 기록을 등록한 달리기입니다.'})
        else:
            return run
        return None

    def checkpoint(self, track, data):
        run = self.find_run(track, data)
        if run is None:
            return
        number = len(run['marks']) + 1
        if data.get('id') != number or not is_int(data.get('id')) or number > STARS:
            self.page(400, {'error': '다음 별 번호를 확인하세요.'})
            return
        elapsed = track.elapsed(run)
        previous = run['marks'][-1] if run['marks'] else 0
        if elapsed - previous < MIN_GAP_MS:
            self.page(429, {'error': '아직 다음 별까지 달리는 중입니다.', 'wait_ms': MIN_GAP_MS - (elapsed - previous)})
            return
        run['marks'].append(elapsed)
        self.page(200, {'id': number, 't_ms': elapsed})

    def finish(self, track, data):
        run = self.find_run(track, data)
        if run is None:
            return
        if len(run['marks']) != STARS:
            self.page(409, {'error': '아직 별을 모두 줍지 않았습니다.'})
            return
        report = data.get('checkpoints')
        if not valid_report(report):
            self.page(400, {'error': '기록 코드의 형식을 확인하세요.'})
            return
        value = recorded_time(run['marks'], report)
        if value is None:
            self.page(422, {'error': '기록이 서버가 확인한 시간과 맞지 않습니다.'})
            return
        run['done'] = True
        track.best = value if track.best is None else min(track.best, value)
        self.page(200, {**track.snapshot(), 'notice': f'{value / 1000:.2f}초 기록을 등록했습니다.'})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
