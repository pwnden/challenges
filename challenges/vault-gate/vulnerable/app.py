"""Wrap the compiled vault program so each TCP connection gets its own process."""
import os
import socketserver
import subprocess

from policy import MAX_LINE_BYTES

BINARY = '/app/vault'


class VaultHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(5)
        try:
            line = self.rfile.readline(1025)
        except OSError:
            return
        if MAX_LINE_BYTES is not None and len(line) > MAX_LINE_BYTES:
            try:
                self.wfile.write(b'ERR name_too_long\n')
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        proc = subprocess.Popen([BINARY], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, env=dict(os.environ))
        try:
            proc.stdin.write(line)
            proc.stdin.close()
        except BrokenPipeError:
            pass
        try:
            out = proc.stdout.read()
        finally:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        try:
            self.wfile.write(out)
        except (BrokenPipeError, ConnectionResetError):
            pass


class VaultServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    VaultServer(('0.0.0.0', 9100), VaultHandler).serve_forever()
