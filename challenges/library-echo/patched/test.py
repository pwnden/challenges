"""Confirm normal usage still works and the former leak+system() chain no longer runs."""
import socket
import struct
import sys

HOST, PORT = 'app', 9400
PROMPT = '이름을 입력하세요: '.encode()
WELCOME = '환영합니다\n'.encode()
POP_RDI_RET = 0x401156
MAIN = 0x40115B
PUTS_GOT = 0x404000
PUTS_PLT = 0x401030
FILLER = 104


def p64(value):
    return struct.pack('<Q', value)


def ask(payload: bytes) -> bytes:
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)
        data = b''
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
    return data


def check(condition, message):
    if not condition:
        sys.exit('check failed: ' + message)


def main():
    normal = ask(b'guest\n')
    check(normal == PROMPT + WELCOME, 'normal usage changed')
    check(b'pwnden{' not in normal, 'a normal request leaked a flag')

    boundary = ask(b'B' * 63 + b'\n')
    check(boundary.startswith(PROMPT + WELCOME), 'a name at the buffer boundary changed behavior')
    check(b'pwnden{' not in boundary, 'the boundary name leaked a flag')

    leak_attempt = (b'A' * FILLER + p64(POP_RDI_RET) + p64(PUTS_GOT)
                     + p64(PUTS_PLT) + p64(MAIN))
    leaked = ask(leak_attempt)
    check(leaked == PROMPT + WELCOME, 'the former leak payload changed the normal reply')
    check(b'pwnden{' not in leaked, 'the former leak payload leaked a flag')

    print('normal names, the boundary-length name, and the former leak payload all stay on the ordinary reply; no flag leaks')


if __name__ == '__main__':
    main()
