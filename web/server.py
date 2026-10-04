"""Serve locally built Vue assets and preserve each target's HTTP behavior."""
from http.server import BaseHTTPRequestHandler
import json
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlsplit


PUBLIC = Path(__file__).resolve().parents[1] / 'public'


class TargetHandler(BaseHTTPRequestHandler):
    def send(self, status, body, kind='text/plain', cookies=()):
        payload = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', kind + ('; charset=utf-8' if kind.startswith(('text/', 'application/json')) else ''))
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for cookie in cookies:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(payload)

    def assets(self):
        path = urlsplit(self.path).path
        if not path.startswith('/assets/'):
            return False
        candidate = (PUBLIC / unquote(path).lstrip('/')).resolve()
        if not candidate.is_relative_to((PUBLIC / 'assets').resolve()) or not candidate.is_file():
            self.send(404, '자료를 찾을 수 없습니다.')
        else:
            kind = mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream'
            # Browsers require a JavaScript MIME type for module scripts.
            if candidate.suffix == '.js':
                kind = 'text/javascript'
            self.send(200, candidate.read_bytes(), kind)
        return True

    def page(self, status, data, cookies=()):
        if 'text/html' in self.headers.get('Accept', ''):
            # Data is inert JSON, including when a document contains HTML text.
            payload = json.dumps({'status': status, 'data': data}, ensure_ascii=False)
            payload = payload.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
            bootstrap = '<script id="pwnden-page-data" type="application/json">' + payload + '</script>'
            page = (PUBLIC / 'index.html').read_text(encoding='utf-8')
            self.send(status, page.replace('</head>', bootstrap + '</head>', 1), 'text/html', cookies)
        else:
            self.send(status, json.dumps(data, ensure_ascii=False), 'application/json', cookies)

    def document(self, status, body, cookies=()):
        if 'text/html' in self.headers.get('Accept', ''):
            self.page(status, {'body': body}, cookies)
        else:
            self.send(status, body, cookies=cookies)
