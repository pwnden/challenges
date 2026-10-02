"""Local document policy: star patterns and deny precedence per operation."""
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from web.server import TargetHandler

POLICY = json.loads(Path(__file__).with_name('policy.json').read_text())
ITEMS = {'locker/team-notes': '팀 회의는 금요일입니다.', 'locker/team-admin': '운영 복구 키=' + os.environ['FLAG'], 'locker/personal-draft': '개인 작업 메모'}
VERSIONS = {
    'locker/team-notes': {'r1': ('첫 작성', '팀 회의는 목요일입니다.'), 'r2': ('일정 수정', ITEMS['locker/team-notes'])},
    'locker/team-admin': {'r1': ('복구 절차 첫 작성', ITEMS['locker/team-admin']), 'r2': ('민감한 값 분리', '복구 키는 별도 운영 기록으로 옮겼습니다.')},
    'locker/personal-draft': {'r1': ('첫 작성', ITEMS['locker/personal-draft'])},
}


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


class Handler(TargetHandler):
    reply = TargetHandler.document
    def do_GET(self):
        if self.assets():
            return
        url = urlsplit(self.path)
        if url.path == '/healthz':
            self.reply(200, 'ok')
        elif url.path == '/':
            self.page(200, {'policy': POLICY, 'user': 'team-reader'})
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
                self.page(200, {'resource': resource, 'versions': [{'version': version, 'title': title} for version, (title, _) in VERSIONS[resource].items()]})
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
