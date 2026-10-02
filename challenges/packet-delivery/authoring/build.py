"""Use real localhost HTTP bytes to construct a small synthetic Ethernet PCAP."""
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import socket
import struct
import tarfile
import threading

KEY = 'pwnden{tcp_reassembles_the_delivery}'
NOTICE = b'Public delivery notice: the approved package is LAB-17 revision 2.\n'
DOCUMENT = ('Staff recovery procedure\nFor operations staff only.\nRecovery code: ' + KEY + '\n').encode()
OLD_DOCUMENT = DOCUMENT.replace(KEY.encode(), b'pwnden{retired_delivery_code}')


def bundle(revision):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w') as archive:
        receipt = json.dumps({'batch': 'LAB-17', 'revision': revision,
                              'status': 'approved' if revision == 2 else 'retired'}).encode()
        document = DOCUMENT if revision == 2 else OLD_DOCUMENT
        for name, data in [('public/notice.txt', NOTICE), ('public/receipt.json', receipt),
                           ('internal/recovery.txt', document)]:
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            archive.addfile(info, io.BytesIO(data))
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode='wb', mtime=0) as writer:
        writer.write(raw.getvalue())
    return compressed.getvalue()


def http_bytes():
    payloads = [('/notice.txt', NOTICE), ('/delivery.tar.gz', bundle(1)), ('/delivery.tar.gz', bundle(2))]

    class Handler(BaseHTTPRequestHandler):
        index = 0
        def log_message(self, *_):
            pass

        def do_GET(self):
            path, data = payloads[type(self).index]
            assert self.path == path
            type(self).index += 1
            self.send_response_only(200)
            self.send_header('Content-Type', 'application/gzip' if self.path.endswith('.gz') else 'text/plain')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    pairs = []
    try:
        for path, payload in payloads:
            request = ('GET ' + path + ' HTTP/1.1\r\nHost: delivery.lab\r\nConnection: close\r\n\r\n').encode()
            with socket.create_connection(server.server_address, timeout=3) as connection:
                connection.sendall(request)
                response = b''
                while data := connection.recv(65535):
                    response += data
            assert response.split(b'\r\n\r\n', 1)[1] == payload
            pairs.append((request, response))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    return pairs


def checksum(data):
    if len(data) % 2:
        data += b'\0'
    total = sum(struct.unpack('!' + 'H' * (len(data) // 2), data))
    while total >> 16:
        total = (total & 65535) + (total >> 16)
    return (~total) & 65535


def packet(client, port, seq, ack, flags, data=b''):
    src, dst = (socket.inet_aton(ip) for ip in
                (('192.0.2.1', '192.0.2.2') if client else ('192.0.2.2', '192.0.2.1')))
    sport, dport = (port, 80) if client else (80, port)
    tcp = struct.pack('!HHIIBBHHH', sport, dport, seq, ack, 5 << 4, flags, 65535, 0, 0)
    value = checksum(src + dst + struct.pack('!BBH', 0, 6, len(tcp) + len(data)) + tcp + data)
    tcp = tcp[:16] + struct.pack('!H', value) + tcp[18:]
    ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 40 + len(data), 1, 0, 64, 6, 0, src, dst)
    ip = ip[:10] + struct.pack('!H', checksum(ip)) + ip[12:]
    return b'\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x01\x08\x00' + ip + tcp + data


def frames(pairs):
    result = []
    for port, (request, response) in enumerate(pairs, 45678):
        result.extend([packet(True, port, 1000, 0, 2), packet(False, port, 2000, 1001, 18),
                       packet(True, port, 1001, 2001, 16), packet(True, port, 1001, 2001, 24, request)])
        client, server = 1001 + len(request), 2001
        result.append(packet(False, port, server, client, 16))
        for start in range(0, len(response), 90):
            chunk = response[start:start + 90]
            result.append(packet(False, port, server, client, 24, chunk))
            server += len(chunk)
            result.append(packet(True, port, client, server, 16))
        result.extend([packet(False, port, server, client, 17), packet(True, port, client, server + 1, 16),
                       packet(True, port, client, server + 1, 17), packet(False, port, server + 1, client + 1, 16)])
    return result


def capture(items):
    data = struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    for index, frame in enumerate(items):
        data += struct.pack('<IIII', 1700000000, index * 1000, len(frame), len(frame)) + frame
    return data


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'delivery.pcap').write_bytes(capture(frames(http_bytes())))
    (output / 'public-list.txt').write_text('Approved delivery: batch LAB-17, revision 2, status approved.\nPublic delivery: public/notice.txt and public/receipt.json only.\nStaff-only: internal recovery procedures and codes.\nRepeated URL names can represent different delivery revisions; inspect each receipt.\nSource: synthetic teaching PCAP made from actual localhost HTTP request/response bytes.\nNo live capture or external traffic.\n')


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1] / 'files')
