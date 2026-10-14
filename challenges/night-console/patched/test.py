"""Confirm normal command/memo usage still works and the former ROP payload length is rejected."""
import socket
import struct
import sys

HOST, PORT = 'app', 9300
PROMPT1 = '명령을 입력하세요 (STATUS): '.encode()
PROMPT2 = '메모를 입력하세요: '.encode()
STATUS_REPLY = '상태: 정상\n'.encode()
UNKNOWN_REPLY = '알 수 없는 명령입니다.\n'.encode()
POP_RDI_RET = 0x401248
STR_ADDR = 0x40201E
RUN_COMMAND = 0x401196


def ask(cmd: bytes, memo: bytes) -> bytes:
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        sock.sendall(cmd)
        sock.sendall(memo)
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
    normal = ask(b'STATUS\n', b'short memo\n')
    check(normal.startswith(PROMPT1 + STATUS_REPLY + PROMPT2), 'the normal STATUS/memo reply changed')
    check(b'pwnden{' not in normal, 'a normal request leaked a flag')

    unknown = ask(b'HELLO\n', b'short memo\n')
    check(UNKNOWN_REPLY in unknown, 'an unrecognized command stopped being rejected')

    boundary = ask(b'STATUS\n', b'B' * 64)
    check(b'ERR' not in boundary, 'a 64-byte memo at the declared boundary was rejected')
    check(b'pwnden{' not in boundary, 'the boundary memo leaked a flag')

    payload = (b'A' * 104 + struct.pack('<Q', POP_RDI_RET)
               + struct.pack('<Q', STR_ADDR) + struct.pack('<Q', RUN_COMMAND))
    rop = ask(b'STATUS\n', payload)
    check(rop.strip().endswith(b'ERR memo_too_long'), 'the former ROP-chain memo was not rejected')
    check(b'pwnden{' not in rop, 'the former ROP-chain memo still leaked a flag')

    print('normal STATUS/memo usage and the 64-byte boundary stay intact; the former ROP-chain memo is rejected')


if __name__ == '__main__':
    main()
