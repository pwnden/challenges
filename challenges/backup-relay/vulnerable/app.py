"""Backup relay for the ops team; the session must remember whether AUTH succeeded."""
import os
import socket
import socketserver

from policy import READ_REQUIRES_AUTH

TOKEN = 'relay-guest-7f2c'
FLAG = os.environ['FLAG']


class RelayHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        authenticated = False
        try:
            self.wfile.write(b'BACKUP-RELAY/1\n')
            self.wfile.flush()
            while True:
                try:
                    line = self.rfile.readline(1025)
                except socket.timeout:
                    break
                if not line:
                    break
                if len(line) > 128 or not line.endswith(b'\n'):
                    self._send('ERR newline_required_or_command_too_long')
                    continue
                command = line.strip().decode('utf-8', 'replace')
                if command == 'HELLO':
                    self._send('OK commands: HELLO, AUTH <token>, STATUS, READ <name>')
                elif command.startswith('AUTH '):
                    authenticated = command[len('AUTH '):] == TOKEN
                    self._send('OK authenticated' if authenticated else 'DENIED bad_token')
                elif command == 'STATUS':
                    self._send('OK role=' + ('staff' if authenticated else 'guest'))
                elif command == 'READ backup-retired':
                    self._send('OK pwnden{retired_backup_cleared}')
                elif command == 'READ backup-current':
                    if authenticated or not READ_REQUIRES_AUTH:
                        self._send('OK ' + FLAG)
                    else:
                        self._send('DENIED staff_auth_required')
                elif command.startswith('READ '):
                    self._send('ERR unknown_resource')
                else:
                    self._send('ERR unsupported_command')
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send(self, text):
        self.wfile.write((text + '\n').encode())
        self.wfile.flush()


class RelayServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    RelayServer(('0.0.0.0', 9000), RelayHandler).serve_forever()
