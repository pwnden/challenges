"""Session-isolated support and staff invitation lab; no external accounts."""
from http.cookies import CookieError, SimpleCookie
from http.server import ThreadingHTTPServer
import json
import os
import secrets
from threading import RLock
from urllib.parse import parse_qs, urlsplit

from policy import invitation_allowed, ticket_allowed
from web.server import TargetHandler

SESSIONS = {}
LOCK = RLock()


class Desk:
    def __init__(self):
        self.user = 'member'
        self.role = 'member'
        self.code = secrets.token_urlsafe(18)
        self.invitation = {'recipient': 'staff-new', 'role': 'staff', 'used': False}
        self.tickets = {
            310: {'id': 310, 'owner': 'member', 'title': '전시 안내 수정',
                  'body': '행사 안내의 날짜를 고쳐 주세요. 답변 알림 #311을 받았는데 내 문의 목록에는 표시되지 않습니다.'},
            311: {'id': 311, 'owner': 'staff-new', 'title': '운영 담당자 합류 안내',
                  'body': 'staff-new 님, 운영 초대 코드입니다. 운영 초대 화면에서 등록하세요. 이 코드는 지정된 계정만 사용할 수 있어야 합니다.',
                  'invitation_code': self.code},
        }

    def snapshot(self):
        return {'user': self.user, 'role': self.role,
                'tickets': [{'id': t['id'], 'title': t['title']} for t in self.tickets.values()
                            if t['owner'] == self.user]}

    def redeem(self, code):
        if code != self.code or self.invitation['used']:
            return False
        if not invitation_allowed(self.invitation, self.user):
            return False
        self.invitation['used'] = True
        self.role = self.invitation['role']
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
        sid = cookie.get('desk_sid')
        return sid.value if sid else ''

    def do_GET(self):
        if self.assets():
            return
        parsed = urlsplit(self.path)
        if parsed.path == '/healthz':
            self.send(200, 'ok')
            return
        with LOCK:
            sid = self.session()
            desk = SESSIONS.get(sid)
            if parsed.path in ('/', '/api/desk'):
                cookies = ()
                if desk is None:
                    sid = secrets.token_hex(24)
                    desk = SESSIONS[sid] = Desk()
                    cookies = ('desk_sid=' + sid + '; HttpOnly; Path=/; SameSite=Lax',)
                self.page(200, desk.snapshot(), cookies)
                return
            if desk is None:
                self.page(401, {'error': '첫 화면에서 시험 계정을 준비하세요.'})
                return
            if parsed.path == '/api/ticket':
                identity = parse_qs(parsed.query).get('id', [''])[0]
                if not identity.isascii() or not identity.isdecimal() or len(identity) > 8:
                    self.page(400, {'error': '문의 번호를 확인하세요.'})
                    return
                ticket = desk.tickets.get(int(identity))
                if ticket is None:
                    self.page(404, {'error': '문의를 찾을 수 없습니다.'})
                elif not ticket_allowed(ticket, desk.user):
                    self.page(403, {'error': '본인의 문의만 읽을 수 있습니다.'})
                else:
                    self.page(200, {'ticket': ticket})
                return
            if parsed.path == '/api/staff':
                if desk.role != 'staff':
                    self.page(403, {'error': '운영 담당자만 열 수 있습니다.'})
                else:
                    self.page(200, {'staff': {'user': desk.user, 'role': desk.role,
                                             'confirmation': os.environ['FLAG']}})
                return
            self.page(404, {'error': '페이지를 찾을 수 없습니다.'})

    def do_POST(self):
        with LOCK:
            desk = SESSIONS.get(self.session())
            if desk is None:
                self.page(401, {'error': '첫 화면에서 시험 계정을 준비하세요.'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 4096:
                    raise ValueError
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError
            except (ValueError, UnicodeError):
                self.page(400, {'error': '요청 형식을 확인하세요.'})
                return
            path = urlsplit(self.path).path
            if path == '/api/invitation':
                code = body.get('code')
                if not isinstance(code, str) or not 0 < len(code) <= 128:
                    self.page(400, {'error': '초대 코드를 입력하세요.'})
                elif not desk.redeem(code):
                    self.page(403, {'error': '현재 계정에서 사용할 수 없는 초대입니다.'})
                else:
                    self.page(200, {**desk.snapshot(), 'notice': '운영 초대를 등록했습니다.'})
            elif path == '/api/reset':
                SESSIONS[self.session()] = Desk()
                self.page(200, {**SESSIONS[self.session()].snapshot(),
                                'notice': '시험 계정과 문의를 처음 상태로 돌렸습니다.'})
            else:
                self.page(404, {'error': '기능을 찾을 수 없습니다.'})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
