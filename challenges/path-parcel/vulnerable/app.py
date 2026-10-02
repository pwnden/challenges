"""Actual file reads in an ephemeral container directory."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from policy import locate

ROOT = Path('/tmp/parcels')
PUBLIC = ROOT / 'public'
STYLE = 'body{max-width:48rem;margin:2rem auto;padding:1rem;background:#101722;color:#dae4f2;font:17px/1.7 sans-serif}input,button{font:inherit;padding:.5rem}input{width:22rem;max-width:90%}a{color:#8bbfff}'


def prepare():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (ROOT / 'private').mkdir(exist_ok=True)
    (PUBLIC / 'welcome.txt').write_text('택배 접수\n접수 번호와 배송 주소를 확인해 주세요.\n', encoding='utf-8')
    (PUBLIC / 'guide.txt').write_text('공개 자료는 public/, 운영 자료는 같은 상위 폴더의 private/에 보관합니다.\n운영 복구 기록의 파일명은 recovery.txt입니다.\n', encoding='utf-8')
    (ROOT / 'private/recovery.txt').write_text('운영 복구 키=' + os.environ['FLAG'] + '\n', encoding='utf-8')


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind='text/plain'):
        data = body.encode()
        self.send_response(status)
        self.send_header('Content-Type', kind + '; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == '/healthz':
            self.reply(200, 'ok')
        elif url.path == '/':
            body = '<h1>주소 없는 택배함</h1><p>접수 안내 문서를 파일명으로 찾아 읽는 사이트입니다.</p><p><a href="/view?file=welcome.txt">welcome.txt</a> · <a href="/view?file=guide.txt">guide.txt</a></p><form action="/view"><label>파일명 <input name="file" value="welcome.txt" maxlength="256" required></label> <button>읽기</button></form>'
            self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>택배함</title><style>' + STYLE + '</style><body>' + body + '</body></html>', 'text/html')
        elif url.path == '/view':
            name = parse_qs(url.query).get('file', [''])[0]
            if not name or len(name) > 256 or '\x00' in name:
                self.reply(400, '파일명을 입력하세요.')
                return
            try:
                self.reply(200, locate(PUBLIC, name).read_text(encoding='utf-8'))
            except PermissionError:
                self.reply(403, '공개 자료 범위 밖입니다.')
            except (OSError, UnicodeError, ValueError):
                self.reply(404, '읽을 수 있는 자료를 찾지 못했습니다.')
        else:
            self.reply(404, '페이지를 찾을 수 없습니다.')


if __name__ == '__main__':
    prepare()
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
