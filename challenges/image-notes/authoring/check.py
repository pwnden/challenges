"""Check actual PNG parsing, identical pixels and the metadata-removal control."""
from build import image, KEY, RECEIPT
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import tomllib
import zlib


def pixels(data):
    offset, parts = 8, []
    while offset < len(data):
        length, = struct.unpack('!I', data[offset:offset + 4])
        if data[offset + 4:offset + 8] == b'IDAT':
            parts.append(data[offset + 8:offset + 8 + length])
        offset += length + 12
    return zlib.decompress(b''.join(parts))


original = Path('files/notice.png').read_bytes()
assert original == image()
assert 'PNG image data' in subprocess.check_output(['file', '-b', 'files/notice.png'], text=True)
memo = subprocess.check_output(['exiftool', '-s3', '-Comment', 'files/notice.png'], text=True)
receipt = json.loads(subprocess.check_output(['exiftool', '-s3', '-Description', 'files/notice.png'], text=True))
assert receipt == RECEIPT
records = json.loads(memo)['records']
chosen = [r['recovery_code'] for r in records if r['asset_id'] == receipt['asset_id'] and r['revision'] == receipt['revision'] and r['state'] == 'active']
assert chosen == [KEY]
assert records[0]['recovery_code'] != KEY
assert len({r['recovery_code'] for r in records}) == 3
for record in records:
    if record['recovery_code'] != KEY:
        assert hashlib.sha256(record['recovery_code'].encode()).hexdigest() != tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
with tempfile.TemporaryDirectory(dir='/tmp') as name:
    stripped = Path(name) / 'stripped.png'
    subprocess.run(['exiftool', '-all=', '-o', str(stripped), 'files/notice.png'], check=True, capture_output=True)
    assert pixels(original) == pixels(stripped.read_bytes())
    assert subprocess.check_output(['exiftool', '-s3', '-Comment', str(stripped)]) == b''
    assert subprocess.check_output(['exiftool', '-s3', '-Description', str(stripped)]) == b''
assert hashlib.sha256(KEY.encode()).hexdigest() == tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
assert KEY not in Path('README.md').read_text()
print('PNG receipt/record correlation, three distinct candidates, rejected stale/unrelated codes, metadata removal and identical pixels passed')
