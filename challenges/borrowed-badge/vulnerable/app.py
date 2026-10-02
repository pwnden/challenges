"""Explicit local policy subset: exact actions, star resources, deny precedence."""
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

POLICY = json.loads(Path(__file__).with_name('policy.json').read_text())
ITEMS = {'locker/team-notes': '팀 회의는 금요일입니다.', 'locker/team-admin': '운영 복구 키=' + os.environ['FLAG'], 'locker/personal-draft': '개인 작업 메모'}
STYLE = 'body{max-width:48rem;margin:2rem auto;padding:1rem;background:#101722;color:#dae4f2;font:17px/1.7 sans-serif}input,button{font:inherit;padding:.5rem}input{width:22rem;max-width:90%}pre{overflow:auto;background:#182334;padding:1rem}a{color:#8bbfff}'


def allowed(action, resource):
    permitted = False
    for rule in POLICY['Statement']:
        pattern = re.escape(rule['Resource']).replace(r'\*', '.*')
        if rule['Action'] not in (action, '*') or re.fullmatch(pattern, resource) is None:
            continue
        if rule['Effect'] == 'Deny':
            return False
        if rule['Effect'] == 'Allow':
            permitted = True
    return permitted


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
            body = '<h1>팀 문서 사이트</h1><p>현재 팀원용 권한인 team-reader로 문서를 읽을 수 있습니다.</p><h2>문서 목록</h2><ul><li>locker/team-notes — 팀 공유 작업 노트</li><li>locker/team-admin — 운영자의 복구 문서</li><li>locker/personal-draft — 다른 사용자의 개인 초안</li></ul><h2>이 계정의 접근 규칙</h2><p>Effect의 Allow는 허용, Action의 read는 읽기, Resource는 문서 이름입니다. 이름의 *는 뒤에 오는 글자 전체를 대신합니다. 허용 규칙에 맞지 않거나 Deny 규칙에 맞으면 거절합니다.</p><pre>' + escape(json.dumps(POLICY, ensure_ascii=False, indent=2)) + '</pre><form action="/read"><label>문서 이름 <input name="resource" value="locker/team-notes" maxlength="128" required></label> <button>읽기</button></form>'
            self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>팀 문서 사이트</title><style>' + STYLE + '</style><body>' + body + '</body></html>', 'text/html')
        elif url.path == '/read':
            resource = parse_qs(url.query).get('resource', [''])[0]
            if not resource or len(resource) > 128:
                self.reply(400, '문서 이름을 입력하세요.')
            elif not allowed('read', resource):
                self.reply(403, '현재 권한으로는 이 문서를 읽을 수 없습니다.')
            elif resource not in ITEMS:
                self.reply(404, '문서를 찾을 수 없습니다.')
            else:
                self.reply(200, ITEMS[resource])
        else:
            self.reply(404, '페이지를 찾을 수 없습니다.')


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
