"""Deterministically create the mislabeled gzip-compressed tar evidence."""
import gzip
import io
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def archive():
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w', format=tarfile.USTAR_FORMAT) as bundle:
        for name, text in [('notes/transfer.txt', '이전 자료 묶음입니다. 복구 키는 recovery/key.txt에 있습니다.\n'), ('recovery/key.txt', 'pwnden{bytes_tell_the_story}\n')]:
            data = text.encode()
            item = tarfile.TarInfo(name)
            item.size = len(data)
            item.mode = 0o644
            item.mtime = 0
            bundle.addfile(item, io.BytesIO(data))
    compressed = io.BytesIO()
    # GzipFile fixes the OS header across supported Python versions and hosts.
    with gzip.GzipFile(fileobj=compressed, mode='wb', filename='', mtime=0, compresslevel=9) as output:
        output.write(buffer.getvalue())
    return compressed.getvalue()


if __name__ == '__main__':
    (ROOT / 'files/banner.png').write_bytes(archive())
