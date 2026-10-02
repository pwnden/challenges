from build import bundle, KEY
import gzip
import hashlib
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import tomllib

with tempfile.TemporaryDirectory(dir='/tmp') as name:
    root = Path(name)
    for label, data in [('release', Path('files/source.tar.gz').read_bytes()), ('control', bundle(False))]:
        destination = root / label
        destination.mkdir()
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            archive.extractall(destination, filter='data')
        repo = destination / 'source'
        assert not (repo / 'config/runtime.env').exists()
        assert KEY not in ''.join(path.read_text() for path in repo.rglob('*') if path.is_file() and '.git' not in path.parts)
        assert subprocess.check_output(['git', '-C', str(repo), 'remote']) == b''
        assert subprocess.check_output(['git', '-C', str(repo), 'rev-list', '--count', '--all']).strip() == b'6'
        history = subprocess.check_output(['git', '-C', str(repo), 'log', '--all', '-p'], text=True)
        assert (KEY in history) == (label == 'release')
        assert subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain']) == b''
assert hashlib.sha256(KEY.encode()).hexdigest() == tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
assert KEY not in Path('README.md').read_text()
print('Six real commits, clean current tree, retained secret, absent remote and sanitized-history control passed')
