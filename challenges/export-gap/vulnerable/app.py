"""A local note API with per-operation ownership checks."""
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import secrets
from urllib.parse import urlsplit
from policy import export_allowed

NOTES = {7: {'id': 7, 'owner': 'guest', 'title': 'Guest meeting note', 'body': 'Meeting is on Friday.'},
         42: {'id': 42, 'owner': 'staff', 'title': 'Internal recovery procedure', 'body': os.environ['FLAG']}}
SESSIONS = {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, value, cookie=None):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(data)

    def identity(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
        except CookieError:
            return None
        token = cookie.get('session')
        return SESSIONS.get(token.value) if token else None

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/healthz':
            return self.reply(200, {'status': 'ok'})
        if path == '/':
            return self.reply(200, {'service': 'Lab notes API', 'operations': ['/api/login', '/api/catalog', '/api/notes/<id>', '/api/exports']})
        user = self.identity()
        if user is None:
            return self.reply(401, {'error': 'login_required'})
        if path == '/api/catalog':
            return self.reply(200, {'notes': [{k: note[k] for k in ('id', 'owner', 'title')} for note in NOTES.values()]})
        match = re.fullmatch(r'/api/notes/([0-9]+)', path)
        if match:
            note = NOTES.get(int(match[1]))
            if note is None:
                return self.reply(404, {'error': 'not_found'})
            if note['owner'] != user:
                return self.reply(403, {'error': 'not_owner'})
            return self.reply(200, note)
        self.reply(404, {'error': 'not_found'})

    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 4096:
                return self.reply(400, {'error': 'invalid_body_size'})
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError('expected object')
        except (ValueError, UnicodeError):
            return self.reply(400, {'error': 'invalid_json'})
        path = urlsplit(self.path).path
        if path == '/api/login':
            if body.get('username') != 'guest' or body.get('password') != 'lab-guest':
                return self.reply(401, {'error': 'invalid_login'})
            token = secrets.token_urlsafe(24)
            SESSIONS[token] = 'guest'
            return self.reply(200, {'user': 'guest'}, 'session=' + token + '; Path=/; HttpOnly; SameSite=Lax')
        user = self.identity()
        if user is None:
            return self.reply(401, {'error': 'login_required'})
        if path == '/api/exports':
            identity = body.get('note_id')
            if type(identity) is not int:
                return self.reply(400, {'error': 'integer_note_id_required'})
            note = NOTES.get(identity)
            if note is None:
                return self.reply(404, {'error': 'not_found'})
            if not export_allowed(note, user):
                return self.reply(403, {'error': 'not_owner'})
            return self.reply(200, {'export': note})
        self.reply(404, {'error': 'not_found'})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
