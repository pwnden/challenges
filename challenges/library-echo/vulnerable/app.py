"""Relay a TCP connection transparently to a fresh terminal process.

Unlike the earlier two-stage wrappers, this program's own return-to-main loop
can make it read from stdin more than once within the same process, so the
relay is a plain full-duplex proxy: one thread copies the socket into the
child's stdin, the main loop copies the child's stdout back to the socket.
Neither side ever shares a buffered stream with the other direction, so a
client that pipelines its writes cannot lose bytes the way a part-buffered,
part-raw read split could (see greeting-echo/night-console's fix for that
class of bug).
"""
import os
import socket
import subprocess
import threading

from policy import BINARY

HOST, PORT = '0.0.0.0', 9400


def handle(conn):
    conn.settimeout(30)
    proc = subprocess.Popen([BINARY], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, env=dict(os.environ))

    def client_to_child():
        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                try:
                    proc.stdin.write(chunk)
                    proc.stdin.flush()
                except (BrokenPipeError, OSError):
                    break
        except OSError:
            pass
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass

    feeder = threading.Thread(target=client_to_child, daemon=True)
    feeder.start()

    try:
        while True:
            # `.read(n)` on a subprocess pipe is a regular buffered read: it
            # blocks until `n` bytes arrive or the child exits, so a reply
            # shorter than the buffer would never show up until the child
            # closes stdout. `.read1(n)` instead returns as soon as the pipe
            # has *any* data, which is what a live, two-way exchange needs.
            chunk = proc.stdout.read1(4096)
            if not chunk:
                break
            try:
                conn.sendall(chunk)
            except OSError:
                break
    finally:
        try:
            conn.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        feeder.join(timeout=5)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        try:
            conn.close()
        except OSError:
            pass


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
