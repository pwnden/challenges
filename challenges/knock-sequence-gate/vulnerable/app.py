"""Maintenance gate guarded by a port-knock sequence; progress is tracked as a set, not a step index."""
import os
import socketserver
import threading

from policy import ORDERED_KNOCKS

FLAG = os.environ['FLAG']
# The required order is 7003 -> 7001 -> 7002; it has nothing to do with port
# magnitude, so a plain ascending scan of the knock range does not happen to
# match it.
KNOCK_PORTS = (7003, 7001, 7002)
GATE_PORT = 7000

_lock = threading.Lock()
_progress = {}


def _register(ip, port):
    with _lock:
        if ORDERED_KNOCKS:
            index = _progress.get(ip, 0)
            if not isinstance(index, int):
                index = 0
            if index < len(KNOCK_PORTS) and KNOCK_PORTS[index] == port:
                _progress[ip] = index + 1
            elif port == KNOCK_PORTS[0]:
                _progress[ip] = 1
            else:
                _progress[ip] = 0
        else:
            knocked = _progress.setdefault(ip, set())
            if not isinstance(knocked, set):
                knocked = _progress[ip] = set()
            knocked.add(port)


def _unlocked(ip):
    with _lock:
        value = _progress.get(ip)
        if ORDERED_KNOCKS:
            return value == len(KNOCK_PORTS)
        return isinstance(value, set) and set(KNOCK_PORTS) <= value


class KnockHandler(socketserver.BaseRequestHandler):
    def handle(self):
        _register(self.client_address[0], self.server.server_address[1])
        try:
            self.request.close()
        except OSError:
            pass


class GateHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        try:
            if _unlocked(self.client_address[0]):
                self.wfile.write(('OK ' + FLAG + '\n').encode())
            else:
                self.wfile.write(b'DENIED not_unlocked\n')
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    knock_servers = [Server(('0.0.0.0', port), KnockHandler) for port in KNOCK_PORTS]
    for server in knock_servers:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    Server(('0.0.0.0', GATE_PORT), GateHandler).serve_forever()


if __name__ == '__main__':
    main()
