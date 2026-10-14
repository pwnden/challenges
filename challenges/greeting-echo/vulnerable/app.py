"""Relay a TCP connection to a fresh kiosk process in two known stages.

Stage 1 (echo): the client sends one line, a byte count. The kiosk prints a
fixed prompt, echoes exactly that many raw bytes, a newline, then its next
fixed prompt. All four pieces have known lengths, so the wrapper reads exactly
that much from the child and forwards it untouched.

Stage 2 (greet): the wrapper forwards every remaining byte from the client to
the child's stdin until the client closes its write side, then closes the
child's stdin and forwards everything the child prints until it exits.
"""
import os
import subprocess

from policy import ECHO_MAX

BINARY = '/app/kiosk'
PROMPT1 = '몇 바이트를 돌려받을까요 (0-64)? '.encode()
PROMPT2 = '이름을 입력하세요: '.encode()
HOST, PORT = '0.0.0.0', 9200


def read_exact(stream, size):
    data = b''
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            break
        data += chunk
    return data


def handle(conn):
    conn.settimeout(10)
    rfile = conn.makefile('rb')
    try:
        line = rfile.readline(1024)
    except OSError:
        return
    try:
        count = int(line.strip())
    except ValueError:
        count = -1
    if count < 0 or (ECHO_MAX is not None and count > ECHO_MAX):
        try:
            conn.sendall(b'ERR echo_count_out_of_range\n')
        except OSError:
            pass
        return
    proc = subprocess.Popen([BINARY], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, env=dict(os.environ))
    try:
        proc.stdin.write(line)
        proc.stdin.flush()
        echo_phase = read_exact(proc.stdout, len(PROMPT1) + count + 1 + len(PROMPT2))
        conn.sendall(echo_phase)
        # Every later read uses `rfile` too: it already buffers from the same
        # socket, and a client that pipelines its writes (sends the name
        # before reading the echo reply) can leave bytes sitting in that
        # buffer where a raw `conn.recv()` here would never see them.
        while True:
            try:
                chunk = rfile.read(4096)
            except OSError:
                chunk = b''
            if not chunk:
                break
            try:
                proc.stdin.write(chunk)
                proc.stdin.flush()
            except (BrokenPipeError, OSError):
                break
        try:
            proc.stdin.close()
        except OSError:
            pass
        rest = proc.stdout.read()
        try:
            conn.sendall(rest)
        except OSError:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        rfile.close()


def serve():
    import socket
    import threading
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(16)
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == '__main__':
    serve()
