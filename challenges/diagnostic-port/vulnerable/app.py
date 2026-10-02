"""HTTP protects recovery data; the lab diagnostic listener has its own policy."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import socket
import socketserver
import threading
from urllib.parse import urlsplit
from policy import ALLOW_RECOVERY


class HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ('/', '/healthz'):
            status, body = 200, {'service': 'Lab board', 'status': 'ok'}
        elif path == '/api/recovery':
            status, body = 403, {'error': 'staff_access_required'}
        else:
            status, body = 404, {'error': 'not_found'}
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class DiagnosticHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        try:
            self.wfile.write(b'LAB-DIAG/1\n')
            self.wfile.flush()
            try:
                line = self.rfile.readline(1025)
            except socket.timeout:
                line = b''
            if len(line) > 128 or not line.endswith(b'\n'):
                reply = 'ERR newline_required_or_command_too_long'
            elif line.strip() == b'HELP':
                reply = 'OK commands: HELP, STATUS, READ <resource>'
            elif line.strip() == b'STATUS':
                reply = 'OK board=ready'
            elif line.strip() == b'READ recovery':
                reply = ('OK ' + os.environ['FLAG']) if ALLOW_RECOVERY else 'DENIED protected_recovery'
            elif line.strip().startswith(b'READ '):
                reply = 'ERR unknown_resource'
            else:
                reply = 'ERR unsupported_command'
            self.wfile.write((reply + '\n').encode())
        except (BrokenPipeError, ConnectionResetError):
            pass


class DiagnosticServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    diagnostic = DiagnosticServer(('0.0.0.0', 8007), DiagnosticHandler)
    threading.Thread(target=diagnostic.serve_forever, daemon=True).start()
    ThreadingHTTPServer(('0.0.0.0', 8000), HTTPHandler).serve_forever()
