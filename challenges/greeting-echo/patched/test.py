"""Confirm normal echo/greet usage still works and the former 120-byte request is rejected."""
import socket
import sys

HOST, PORT = 'app', 9200
PROMPT1 = '몇 바이트를 돌려받을까요 (0-64)? '.encode()
PROMPT2 = '이름을 입력하세요: '.encode()


def ask(first_line: bytes, rest: bytes = b'') -> bytes:
    with socket.create_connection((HOST, PORT), timeout=5) as sock:
        sock.sendall(first_line)
        if rest:
            sock.sendall(rest)
        sock.shutdown(socket.SHUT_WR)
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    return data


def check(condition, message):
    if not condition:
        sys.exit('check failed: ' + message)


def main():
    normal = ask(b'10\n', b'guest\n')
    check(normal.startswith(PROMPT1), 'the normal echo prompt changed')
    check(PROMPT2 in normal, 'the normal greet prompt is missing')
    check(b'pwnden{' not in normal, 'a normal request leaked a flag')

    boundary = ask(b'64\n', b'guest\n')
    check(boundary.startswith(PROMPT1), 'the boundary (64-byte) echo request changed behavior')
    check(b'pwnden{' not in boundary, 'the boundary request leaked a flag')

    overflow = ask(b'120\n')
    check(overflow.strip() == b'ERR echo_count_out_of_range', 'the former 120-byte echo request was not rejected')
    check(b'pwnden{' not in overflow, 'the former overflow request still leaked a flag')

    negative = ask(b'-1\n')
    check(negative.strip() == b'ERR echo_count_out_of_range', 'a negative echo count was not rejected')

    print('normal echo/greet usage and the 64-byte boundary stay intact; the former 120-byte canary leak is rejected')


if __name__ == '__main__':
    main()
