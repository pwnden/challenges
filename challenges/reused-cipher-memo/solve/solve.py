"""CHECK reuses the exact pad bytes MEMO used; XOR a zero string of the same length to recover the pad."""
import socket
import sys

HOST, PORT = 'app', 9200


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
        if not banner.startswith('MEMO-VAULT'):
            print('unexpected banner: ' + banner, file=sys.stderr)
            raise SystemExit(1)
        send(sock, 'MEMO')
        reply = recv_line(sock)
        if not reply.startswith('OK '):
            print('MEMO failed: ' + reply, file=sys.stderr)
            raise SystemExit(2)
        sealed = bytes.fromhex(reply[len('OK '):])
        send(sock, 'CHECK ' + ('00' * len(sealed)))
        reply = recv_line(sock)
        if not reply.startswith('OK '):
            print('CHECK failed: ' + reply, file=sys.stderr)
            raise SystemExit(5)
        pad = bytes.fromhex(reply[len('OK '):])
        plain = bytes(a ^ b for a, b in zip(sealed, pad))
        try:
            text = plain.decode('ascii')
        except UnicodeDecodeError:
            text = ''
        if not text.startswith('pwnden{'):
            print('CHECK pad no longer matches MEMO: ' + plain.hex(), file=sys.stderr)
            raise SystemExit(3)
        print(text)


if __name__ == '__main__':
    main()
