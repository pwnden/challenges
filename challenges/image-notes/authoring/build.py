"""Generate a real PNG with an export receipt and retained versioned memos."""
import binascii
import json
from pathlib import Path
import struct
import zlib

KEY = 'pwnden{picture_pixels_are_not_all}'
RECEIPT = {'asset_id': 'banner-17', 'revision': 3}
RECORDS = [
    {'asset_id': 'banner-09', 'revision': 3, 'state': 'active', 'recovery_code': 'pwnden{other_board_example}'},
    {'asset_id': 'banner-17', 'revision': 2, 'state': 'retired', 'recovery_code': 'pwnden{retired_picture_code}'},
    {'asset_id': 'banner-17', 'revision': 3, 'state': 'active', 'recovery_code': KEY},
]


def chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', binascii.crc32(kind + data))


def image(with_memo=True):
    width, height = 320, 80
    pixels = b''.join(b'\0' + b''.join(bytes((35, 95, 150)) if y < 20 or y > 60
                        else bytes((225, 240, 250)) for x in range(width)) for y in range(height))
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0))
    if with_memo:
        memo = {'exporter': 'board-export/2', 'records': RECORDS}
        data += chunk(b'tEXt', b'Description\0' + json.dumps(RECEIPT, separators=(',', ':')).encode())
        data += chunk(b'tEXt', b'Comment\0' + json.dumps(memo, separators=(',', ':')).encode())
    return data + chunk(b'IDAT', zlib.compress(pixels, level=9)) + chunk(b'IEND', b'')


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'files'
    target.mkdir(exist_ok=True)
    (target / 'notice.png').write_bytes(image())
