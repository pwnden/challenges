"""Actual file reads in an ephemeral container directory."""
from http.server import ThreadingHTTPServer
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from policy import locate
from web.server import TargetHandler

ROOT = Path('/tmp/parcels')
PUBLIC = ROOT / 'public'


def prepare():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (ROOT / 'private').mkdir(exist_ok=True)
    (PUBLIC / 'welcome.txt').write_text('택배 접수\n접수 번호와 배송 주소를 확인해 주세요.\n', encoding='utf-8')
    (PUBLIC / 'guide.txt').write_text('공개 자료는 public/, 운영 자료는 같은 상위 폴더의 private/에 보관합니다.\n운영 복구 기록의 파일명은 recovery.txt입니다.\n', encoding='utf-8')
    (ROOT / 'private/recovery.txt').write_text('운영 복구 키=' + os.environ['FLAG'] + '\n', encoding='utf-8')


class Handler(TargetHandler):
    reply = TargetHandler.document
    def do_GET(self):
        if self.assets():
            return
        url = urlsplit(self.path)
        if url.path == '/healthz':
            self.reply(200, 'ok')
        elif url.path == '/':
            self.page(200, {'files': ['welcome.txt', 'guide.txt']})
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
