"""Relay a TCP connection to a fresh console process in two known stages.

Stage 1 (command): the client sends one line. The binary always replies with
a fixed prompt, a fixed STATUS-or-unknown reply (only "STATUS" matches), and
its next fixed prompt; all three pieces have known lengths, so the wrapper
reads exactly that much from the child and forwards it untouched.

Stage 2 (memo): the wrapper reads every remaining byte the client sends until
it closes its write side, buffers it in full, and only then forwards it to
the child's stdin -- `policy.MEMO_MAX` can reject an oversized memo here
before the child ever sees it. The wrapper then closes the child's stdin and
forwards everything the child prints until it exits.
"""
import os
import socket
import subprocess
import threading

from policy import MEMO_MAX

BINARY = '/app/console'
PROMPT1 = '명령을 입력하세요 (STATUS): '.encode()
PROMPT2 = '메모를 입력하세요: '.encode()
STATUS_REPLY = '상태: 정상\n'.encode()
UNKNOWN_REPLY = '알 수 없는 명령입니다.\n'.encode()
HOST, PORT = '0.0.0.0', 9300


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
        line = rfile.readline(64)
    except OSError:
        return
    proc = subprocess.Popen([BINARY], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, env=dict(os.environ))
    try:
        proc.stdin.write(line)
        proc.stdin.flush()
        reply = STATUS_REPLY if line.strip() == b'STATUS' else UNKNOWN_REPLY
        stage1 = read_exact(proc.stdout, len(PROMPT1) + len(reply) + len(PROMPT2))
        conn.sendall(stage1)

        # Every later read uses `rfile` too: it already buffers from the same
        # socket, and a client that pipelines its writes (sends the memo
        # before reading the stage-1 reply) can leave bytes sitting in that
        # buffer where a raw `conn.recv()` here would never see them.
        memo = b''
        while True:
            try:
                chunk = rfile.read(4096)
            except OSError:
                chunk = b''
            if not chunk:
                break
            memo += chunk
        if MEMO_MAX is not None and len(memo) > MEMO_MAX:
            try:
                conn.sendall(b'ERR memo_too_long\n')
            except OSError:
                pass
            # The child is still blocked reading stage 2; it will never see
            # EOF now, so kill it here instead of leaving the cleanup below
            # to wait out its full timeout on every rejection.
            proc.kill()
            return
        proc.stdin.write(memo)
        proc.stdin.close()
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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(16)
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == '__main__':
    serve()
