"""Local archive target; the policy file selects vulnerable or patched access."""
from http.server import ThreadingHTTPServer
import os
from urllib.parse import urlsplit

from policy import expose_backup
from web.server import TargetHandler

BACKUP_PATH = "/archive/site-backup.txt"
BACKUP = "Archive export\ncollection=small-web\nrecovery_key=" + os.environ["FLAG"] + "\n"


class Handler(TargetHandler):
    reply = TargetHandler.send
    def do_GET(self):
        if self.assets():
            return
        path = urlsplit(self.path).path
        if path == "/healthz":
            self.reply(200, "ok")
        elif path == "/robots.txt":
            self.reply(200, "User-agent: *\nDisallow: /archive/\n" if expose_backup() else "User-agent: *\nDisallow:\n")
        elif path == BACKUP_PATH:
            self.reply(200, BACKUP) if expose_backup() else self.reply(404, "자료를 찾을 수 없습니다.")
        elif path in ("/", "/about"):
            self.page(200, {'collections': ['별빛 우체국', '종이배 클럽']} if path == '/' else {'export': 'site-backup.txt', 'crawler': '/robots.txt'})
        else:
            self.reply(404, "자료를 찾을 수 없습니다.")


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
