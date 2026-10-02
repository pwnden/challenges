"""Capture actual loopback DNS messages from a self-contained teaching fixture."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import socketserver
import struct
import threading

ROOT = Path(__file__).resolve().parents[1]
FLAG = b'pwnden{dns_leaks_data_ok}'


def question_name(packet):
    offset, labels = 12, []
    while packet[offset]:
        size = packet[offset]
        labels.append(packet[offset + 1:offset + 1 + size].decode('ascii'))
        offset += size + 1
    assert packet[offset + 1:offset + 5] == struct.pack('!HH', 1, 1)
    return '.'.join(labels)


def capture():
    rows = []

    def record(direction, packet):
        rows.append({'time': datetime.now(timezone.utc).isoformat(), 'direction': direction,
                     'id': struct.unpack('!H', packet[:2])[0], 'type': 'A', 'qname': question_name(packet)})

    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            packet, transport = self.request
            record('Q', packet)
            response = struct.pack('!6H', struct.unpack('!H', packet[:2])[0], 0x8180, 1, 1, 0, 0) + packet[12:]
            response += b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 60, 4) + socket.inet_aton('192.0.2.7')
            transport.sendto(response, self.client_address)
            record('R', response)

    encoded = base64.b32encode(FLAG).decode()
    assert len(encoded) == 40 and '=' not in encoded
    chunks = [encoded[:20], encoded[20:]]
    names = ['status.box.test', '2-' + chunks[1] + '.sync.box.test',
             'assets.box.test', '1-' + chunks[0] + '.sync.box.test',
             '2-' + chunks[1] + '.sync.box.test']
    server = socketserver.UDPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(3)
            for identity, name in enumerate(names, 1001):
                question = b''.join(bytes([len(label)]) + label.encode() for label in name.split('.')) + b'\0' + struct.pack('!HH', 1, 1)
                packet = struct.pack('!6H', identity, 0x0100, 1, 0, 0, 0) + question
                client.sendto(packet, server.server_address)
                response, address = client.recvfrom(4096)
                assert address == server.server_address and response[:2] == packet[:2]
                assert response[2] & 0x80
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)
    assert len(rows) == 10
    return rows


if __name__ == '__main__':
    rows = capture()
    (ROOT / 'files/dns.jsonl').write_text('\n'.join(json.dumps(row, ensure_ascii=False) for row in rows) + '\n', encoding='utf-8')
