"""Memo vault with a one-time-pad 'reseal' check; the pad is never actually rotated."""
import os
import socketserver

from policy import ROTATE_CHECK_KEY

FLAG = os.environ['FLAG'].encode()
PAD_LENGTH = 128
MAX_CHECK_LENGTH = PAD_LENGTH

_memo_pad = os.urandom(PAD_LENGTH)


def _xor(data, pad):
    return bytes(byte ^ pad[i] for i, byte in enumerate(data))


class VaultHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        try:
            self.wfile.write(b'MEMO-VAULT/1\n')
            self.wfile.flush()
            while True:
                try:
                    line = self.rfile.readline(1025)
                except TimeoutError:
                    break
                if not line:
                    break
                if len(line) > 512 or not line.endswith(b'\n'):
                    self._send('ERR newline_required_or_command_too_long')
                    continue
                command = line.strip().decode('utf-8', 'replace')
                if command == 'HELLO':
                    self._send('OK commands: HELLO, MEMO, CHECK <hex>')
                elif command == 'MEMO':
                    sealed = _xor(FLAG, _memo_pad[:len(FLAG)])
                    self._send('OK ' + sealed.hex())
                elif command.startswith('CHECK '):
                    self._handle_check(command[len('CHECK '):])
                else:
                    self._send('ERR unsupported_command')
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_check(self, hex_text):
        try:
            data = bytes.fromhex(hex_text)
        except ValueError:
            self._send('ERR invalid_hex')
            return
        if not data or len(data) > MAX_CHECK_LENGTH:
            self._send('ERR length_1_to_' + str(MAX_CHECK_LENGTH))
            return
        pad = _memo_pad[:len(data)] if not ROTATE_CHECK_KEY else os.urandom(len(data))
        self._send('OK ' + _xor(data, pad).hex())

    def _send(self, text):
        self.wfile.write((text + '\n').encode())
        self.wfile.flush()


class VaultServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    VaultServer(('0.0.0.0', 9200), VaultHandler).serve_forever()
