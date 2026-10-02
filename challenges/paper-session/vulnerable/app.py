"""Real cookies with a server-owned guest session and replaceable role policy."""
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer
import os
import secrets
from urllib.parse import urlsplit
from policy import role
from web.server import TargetHandler

SID = secrets.token_hex(24)
SESSIONS = {SID: 'guest'}


class Handler(TargetHandler):
    reply = TargetHandler.document
    def do_GET(self):
        if self.assets():
            return
        cookie = SimpleCookie()
        cookie.load(self.headers.get('Cookie', ''))
        values = {key: item.value for key, item in cookie.items()}
        path = urlsplit(self.path).path
        if path == '/healthz':
            self.reply(200, 'ok')
        elif path == '/key':
            self.reply(200, '장비 복구 키\n' + os.environ['FLAG']) if role(values, SESSIONS) == 'staff' else self.reply(403, '복구 키는 운영자(staff)만 읽을 수 있습니다.')
        elif path == '/':
            current = role(values, SESSIONS)
            cookies = () if values.get('paper_sid') == SID else ('paper_sid=' + SID + '; HttpOnly; Path=/; SameSite=Lax', 'paper_role=guest; Path=/; SameSite=Lax')
            self.page(200, {'role': current, 'claim_cookie': 'paper_role', 'note': '작업 노트'}, cookies)
        else:
            self.reply(404, '페이지를 찾을 수 없습니다.')


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
