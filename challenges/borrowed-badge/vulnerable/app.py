"""Local document policy: star patterns and deny precedence per operation."""
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qs, urlencode, urlsplit

POLICY = json.loads(Path(__file__).with_name('policy.json').read_text())
ITEMS = {'locker/team-notes': '팀 회의는 금요일입니다.', 'locker/team-admin': '운영 복구 키=' + os.environ['FLAG'], 'locker/personal-draft': '개인 작업 메모'}
VERSIONS = {
    'locker/team-notes': {'r1': ('첫 작성', '팀 회의는 목요일입니다.'), 'r2': ('일정 수정', ITEMS['locker/team-notes'])},
    'locker/team-admin': {'r1': ('복구 절차 첫 작성', ITEMS['locker/team-admin']), 'r2': ('민감한 값 분리', '복구 키는 별도 운영 기록으로 옮겼습니다.')},
    'locker/personal-draft': {'r1': ('첫 작성', ITEMS['locker/personal-draft'])},
}
STYLE = 'body{max-width:48rem;margin:2rem auto;padding:1rem;background:#101722;color:#dae4f2;font:17px/1.7 sans-serif}input,button{font:inherit;padding:.5rem}input{width:22rem;max-width:90%}pre{overflow:auto;background:#182334;padding:1rem}a{color:#8bbfff}'


def matches(pattern, value):
    return re.fullmatch(re.escape(pattern).replace(r'\*', '.*'), value) is not None


def allowed(action, resource):
    permitted = False
    for rule in POLICY['Statement']:
        if not matches(rule['Action'], action) or not matches(rule['Resource'], resource):
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
            body = '<h1>팀 문서 사이트</h1><p>현재 계정: team-reader. 공유 작업 노트를 읽고 변경 기록을 확인할 수 있습니다.</p><h2>문서 목록</h2><ul><li>locker/team-notes — 팀 공유 작업 노트 <a href="/read?resource=locker%2Fteam-notes">현재 문서</a> · <a href="/history?resource=locker%2Fteam-notes">변경 기록</a></li><li>locker/team-admin — 운영자의 복구 문서 <a href="/read?resource=locker%2Fteam-admin">현재 문서</a></li><li>locker/personal-draft — 다른 사용자의 개인 초안</li></ul><h2>이 계정의 접근 규칙</h2><p>Allow는 허용, Deny는 거절입니다. Action은 기능, Resource는 문서 이름입니다. *는 해당 위치의 글자를 대신합니다. 요청 기능과 문서 이름에 맞는 Deny 규칙이 있으면 거절합니다.</p><pre>' + escape(json.dumps(POLICY, ensure_ascii=False, indent=2)) + '</pre><h2>기능 안내</h2><ul><li>현재 문서: read</li><li>변경 기록 목록: read-history</li><li>기록에 저장된 문서: read-version</li></ul><form action="/read"><label>문서 이름 <input name="resource" value="locker/team-notes" maxlength="128" required></label> <button>읽기</button></form>'
            self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>팀 문서 사이트</title><style>' + STYLE + '</style><body>' + body + '</body></html>', 'text/html')
        elif url.path in ('/read', '/history', '/version'):
            query = parse_qs(url.query)
            resource = query.get('resource', [''])[0]
            action = {'/read': 'read', '/history': 'read-history', '/version': 'read-version'}[url.path]
            if not resource or len(resource) > 128:
                self.reply(400, '문서 이름을 입력하세요.')
            elif not allowed(action, resource):
                self.reply(403, '현재 권한으로는 이 문서를 읽을 수 없습니다.')
            elif resource not in ITEMS:
                self.reply(404, '문서를 찾을 수 없습니다.')
            elif url.path == '/read':
                self.reply(200, ITEMS[resource])
            elif url.path == '/history':
                rows = ''.join('<li><a href="/version?' + escape(urlencode({'resource': resource, 'version': version}), quote=True) + '">' + escape(version + ' — ' + title) + '</a></li>' for version, (title, _) in VERSIONS[resource].items())
                self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8"><title>변경 기록</title><style>' + STYLE + '</style><h1>' + escape(resource) + ' 변경 기록</h1><ul>' + rows + '</ul>', 'text/html')
            else:
                version = query.get('version', [''])[0]
                record = VERSIONS[resource].get(version)
                if record is None:
                    self.reply(404, '변경 기록을 찾을 수 없습니다.')
                else:
                    self.reply(200, record[1])
        else:
            self.reply(404, '페이지를 찾을 수 없습니다.')


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
