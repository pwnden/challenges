"""Add the challenge-specific HTTP behavior here."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os


FLAG = os.environ['FLAG']


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthz':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            return
        # TODO: implement the target's routes, data and intended vulnerability.
        self.send_response(503)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write('문제를 준비하고 있습니다.'.encode('utf-8'))


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
