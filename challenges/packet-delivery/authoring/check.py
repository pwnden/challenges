from build import build, capture, checksum, DOCUMENT, KEY, NOTICE
import hashlib
import io
from pathlib import Path
import struct
import subprocess
import tarfile
import tempfile
import tomllib


def unpack(path):
    raw = path.read_bytes()
    assert struct.unpack('<IHHIIII', raw[:24]) == (0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    offset, frames = 24, []
    while offset < len(raw):
        _, _, size, wire = struct.unpack('<IIII', raw[offset:offset + 16])
        assert size == wire
        offset += 16
        frame = raw[offset:offset + size]
        assert len(frame) == size
        frames.append(frame)
        offset += size
    assert offset == len(raw)
    return frames


def validate_packets(frames):
    states, bodies = {}, {}
    for frame in frames:
        assert frame[12:14] == b'\x08\x00'
        ip, tcp = frame[14:34], frame[34:]
        assert ip[0] == 0x45 and ip[9] == 6
        assert struct.unpack('!H', ip[2:4])[0] == len(ip) + len(tcp)
        assert checksum(ip) == 0
        assert checksum(ip[12:20] + struct.pack('!BBH', 0, 6, len(tcp)) + tcp) == 0
        sport, dport, seq, ack = struct.unpack('!HHII', tcp[:12])
        assert tcp[12] == 5 << 4
        client, port = dport == 80, sport if dport == 80 else dport
        flags, data = tcp[13], tcp[20:]
        state = states.setdefault(port, {True: None, False: None})
        if state[client] is None:
            assert flags & 2 and seq == (1000 if client else 2000)
            state[client] = seq
        assert seq == state[client]
        if flags & 16:
            assert ack == state[not client]
        state[client] += len(data) + bool(flags & 2) + bool(flags & 1)
        bodies.setdefault((port, client), bytearray()).extend(data)
    assert len(states) == 2
    return bodies


def exports(path, output):
    output.mkdir()
    result = subprocess.run(['tshark', '-r', str(path), '--export-objects', 'http,' + str(output)], capture_output=True)
    assert result.returncode == 0, result.stderr
    return {item.name: item.read_bytes() for item in output.iterdir()}


path = Path('files/delivery.pcap')
frames = unpack(path)
bodies = validate_packets(frames)
assert KEY.encode() not in path.read_bytes()
requests = subprocess.check_output(['tshark', '-r', str(path), '-Y', 'http.request', '-T', 'fields', '-e', 'http.request.uri'], stderr=subprocess.DEVNULL)
assert requests.splitlines() == [b'/notice.txt', b'/delivery.tar.gz']
with tempfile.TemporaryDirectory(dir='/tmp') as name:
    root = Path(name)
    objects = exports(path, root / 'objects')
    assert objects['notice.txt'] == NOTICE
    assert objects['delivery.tar.gz'] == bytes(bodies[(45679, False)]).split(b'\r\n\r\n', 1)[1]
    assert hashlib.sha256(objects['delivery.tar.gz']).digest() == hashlib.sha256(bytes(bodies[(45679, False)]).split(b'\r\n\r\n', 1)[1]).digest()
    with tarfile.open(fileobj=io.BytesIO(objects['delivery.tar.gz']), mode='r:gz') as archive:
        assert archive.extractfile('internal/recovery.txt').read() == DOCUMENT
        assert archive.extractfile('public/notice.txt').read() == NOTICE
    bad_index = next(index for index, frame in enumerate(frames) if struct.unpack('!H', frame[36:38])[0] == 45679 and len(frame) > 54 and b'HTTP/' not in frame[54:])
    incomplete = root / 'incomplete.pcap'
    incomplete.write_bytes(capture(frames[:bad_index] + frames[bad_index + 1:]))
    broken = exports(incomplete, root / 'broken')
    if 'delivery.tar.gz' in broken:
        try:
            with tarfile.open(fileobj=io.BytesIO(broken['delivery.tar.gz']), mode='r:gz') as archive:
                recovered = archive.extractfile('internal/recovery.txt').read()
        except (tarfile.TarError, EOFError, OSError):
            recovered = b''
        assert KEY.encode() not in recovered
    invalid = root / 'invalid.pcap'
    invalid.write_bytes(b'not a capture\n')
    assert subprocess.run(['tshark', '-r', str(invalid)], capture_output=True).returncode != 0
    build(root / 'regenerated')
    rebuilt = exports(root / 'regenerated/delivery.pcap', root / 'rebuilt')
    with tarfile.open(fileobj=io.BytesIO(rebuilt['delivery.tar.gz']), mode='r:gz') as archive:
        assert archive.extractfile('internal/recovery.txt').read() == DOCUMENT
assert hashlib.sha256(KEY.encode()).hexdigest() == tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
assert KEY not in Path('README.md').read_text()
print('Actual HTTP bytes, checksums, TCP sequence/ACK, object equality, missing segment, invalid capture and regeneration passed')
