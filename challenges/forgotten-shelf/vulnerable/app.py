"""Local archive target; the policy file selects vulnerable or patched access."""
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from urllib.parse import urlsplit

from policy import expose_backup

BACKUP_PATH = "/archive/site-backup.txt"
BACKUP = "Archive export\ncollection=small-web\nrecovery_key=" + os.environ["FLAG"] + "\n"
STYLE = """body{max-width:48rem;margin:3rem auto;padding:1rem;background:#101722;color:#dae4f2;font:17px/1.7 sans-serif}
a{color:#8bbfff}pre{white-space:pre-wrap;background:#182334;padding:1rem}"""


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind="text/plain"):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/healthz":
            self.reply(200, "ok")
        elif path == "/robots.txt":
            self.reply(200, "User-agent: *\nDisallow: /archive/\n" if expose_backup() else "User-agent: *\nDisallow:\n")
        elif path == BACKUP_PATH:
            self.reply(200, BACKUP) if expose_backup() else self.reply(404, "자료를 찾을 수 없습니다.")
        elif path in ("/", "/about"):
            body = ('<h1>작은 웹 보관소</h1><p>문을 닫은 팬사이트와 개인 홈페이지의 흔적을 보관합니다.</p>'
                    '<ul><li>별빛 우체국 — 공개 전시 준비 중</li><li>종이배 클럽 — 복구 완료</li></ul>'
                    '<p><a href="/about">운영 안내</a></p>' if path == "/" else
                    '<h1>운영 안내</h1><p>최근 자료를 이전하면서 내보낸 백업이 있습니다.</p>'
                    '<p>이전 작업의 내보내기 파일명은 <code>site-backup.txt</code>입니다.</p>'
                    '<p>검색 로봇의 수집 안내는 사이트 루트의 robots.txt에 두었습니다.</p>'
                    '<p><a href="/">보관소로 돌아가기</a></p>')
            self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8">'
                       '<meta name="viewport" content="width=device-width, initial-scale=1">'
                       '<title>작은 웹 보관소</title><style>' + STYLE + '</style><body>' + body + '</body></html>', "text/html")
        else:
            self.reply(404, escape("자료를 찾을 수 없습니다."))


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
