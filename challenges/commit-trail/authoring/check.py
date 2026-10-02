from build import bundle, KEY, OLD_KEY
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
        assert not (repo / 'config/worker.env').exists()
        assert KEY not in ''.join(path.read_text() for path in repo.rglob('*') if path.is_file() and '.git' not in path.parts)
        assert subprocess.check_output(['git', '-C', str(repo), 'remote']) == b''
        assert subprocess.check_output(['git', '-C', str(repo), 'rev-list', '--count', '--all']).strip() == b'8'
        history = subprocess.check_output(['git', '-C', str(repo), 'log', '--all', '-p'], text=True)
        assert (KEY in history) == (label == 'release')
        assert (OLD_KEY in history) == (label == 'release')
        deleted = subprocess.check_output(['git', '-C', str(repo), 'log', '--diff-filter=D', '--format=%H', '--', 'config/worker.env'], text=True).strip()
        previous = subprocess.check_output(['git', '-C', str(repo), 'show', deleted + '^:config/worker.env'], text=True)
        assert (KEY in previous) == (label == 'release')
        assert OLD_KEY not in previous
        followed = subprocess.check_output(['git', '-C', str(repo), 'log', '--follow', '--format=%s', deleted + '^', '--', 'config/worker.env'], text=True)
        assert 'Rename runtime configuration' in followed and 'Rotate recovery key' in followed
        assert subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain']) == b''
assert hashlib.sha256(KEY.encode()).hexdigest() == tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
assert KEY not in Path('README.md').read_text()
assert hashlib.sha256(OLD_KEY.encode()).hexdigest() != tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
print('Eight commits, key rotation, rename following, release-specific key, retired-key rejection and sanitized-history control passed')
