"""A lab fallback page uses 200 even when the requested resource is absent."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlsplit
from policy import ALLOW_PRIVATE


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        path = urlsplit(self.path).path
        status = 200
        if path in ('/', '/help'):
            body = {'service': 'Lab delivery board', 'public': ['/help', '/healthz'],
                    'help': 'Public information only; operational recovery data is staff-only.'}
        elif path == '/healthz':
            body = {'status': 'ok', 'service': 'Lab delivery board'}
        elif path == '/ops-check':
            if ALLOW_PRIVATE:
                body = {'audience': 'staff', 'purpose': 'Delivery board recovery',
                        'recovery_code': os.environ['FLAG']}
            else:
                status, body = 403, {'error': 'staff_access_required'}
        else:
            body = {'view': 'fallback', 'message': 'No public document at this address.'}
        data = json.dumps(body, separators=(',', ':')).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
