"""Confirm ordinary names still work, and the former overflow length is rejected before it reaches the vault binary."""
import socket
import sys


def ask(payload: bytes) -> str:
    with socket.create_connection(('app', 9100), timeout=5) as sock:
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    return data.decode('utf-8', 'replace')


def check(condition, message):
    if not condition:
        sys.exit('check failed: ' + message)


def main():
    guest = ask(b'guest\n')
    check('손님 접근만 허용됩니다.' in guest, 'a plain guest name changed behavior')

    boundary = ask(b'C' * 63 + b'\n')
    check('손님 접근만 허용됩니다.' in boundary, 'a name at the buffer boundary was rejected or changed behavior')

    overflow = ask(b'A' * 77 + b'\n')
    check(overflow.strip() == 'ERR name_too_long', 'the former overflow payload was not rejected before reaching the vault binary')
    check('pwnden{' not in overflow, 'the former overflow payload still leaked a flag')

    longer = ask(b'B' * 200 + b'\n')
    check(longer.strip() == 'ERR name_too_long', 'a much longer name was not rejected')

    print('ordinary names still reach the vault binary; the former overflow length and longer names are rejected before they do')


if __name__ == '__main__':
    main()
