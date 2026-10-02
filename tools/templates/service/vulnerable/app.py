"""Add the challenge-specific HTTP behavior here."""

from http.server import ThreadingHTTPServer
import os
from web.server import TargetHandler


FLAG = os.environ['FLAG']


class Handler(TargetHandler):
    def do_GET(self):
        if self.assets():
            return
        if self.path == '/healthz':
            self.send(200, 'ok')
            return
        # TODO: implement the target's routes, data and intended vulnerability.
        self.page(503, {'error': '문제를 준비하고 있습니다.'})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
