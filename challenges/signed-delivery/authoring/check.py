from build import build, DOCUMENT, OLD_DOCUMENT
import hashlib
from pathlib import Path
import subprocess
import tempfile
import tomllib


def verify(document, public, signature):
    result = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(public), '-signature', str(signature), str(document)], capture_output=True)
    assert result.returncode in (0, 1), result.stderr
    return result.returncode == 0


files = Path('files')
public, signature = files / 'sender-public.pem', files / 'delivery-v2.sig'
assert subprocess.run(['openssl', 'pkey', '-pubin', '-in', str(public), '-noout'], capture_output=True).returncode == 0
copies = sorted(files.glob('copy-*.txt'))
assert len(copies) == 3 and {p.name for p in copies if verify(p, public, signature)} == {'copy-c.txt'}
assert {p.name for p in copies if verify(p, public, files / 'delivery.sig')} == {'copy-b.txt'}
assert (files / 'copy-c.txt').read_bytes() == DOCUMENT
assert (files / 'copy-b.txt').read_bytes() == OLD_DOCUMENT
assert 'Approved revision: 2.' in (files / 'trust-note.txt').read_text()
assert 'signature=delivery-v2.sig' in (files / 'trust-note.txt').read_text()
assert len(signature.read_bytes()) == 256
assert len({p.read_bytes() for p in copies}) == 3
assert len({p.stat().st_size for p in copies}) == 1
with tempfile.TemporaryDirectory(dir='/tmp') as name:
    root = Path(name)
    changed = root / 'changed.txt'
    changed.write_bytes(bytes([DOCUMENT[0] ^ 1]) + DOCUMENT[1:])
    assert not verify(changed, public, signature)
    bad_signature = root / 'changed.sig'
    raw = signature.read_bytes()
    bad_signature.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    assert not verify(files / 'copy-c.txt', public, bad_signature)
    build(root / 'regenerated')
    other = root / 'regenerated'
    assert (other / 'sender-public.pem').read_bytes() != public.read_bytes()
    assert not verify(files / 'copy-c.txt', other / 'sender-public.pem', signature)
    assert {p.name for p in other.glob('copy-*.txt') if verify(p, other / 'sender-public.pem', other / 'delivery-v2.sig')} == {'copy-c.txt'}
    assert {p.name for p in other.glob('copy-*.txt') if verify(p, other / 'sender-public.pem', other / 'delivery.sig')} == {'copy-b.txt'}
    assert (other / 'copy-c.txt').read_bytes() == DOCUMENT
    assert len({p.stat().st_mtime_ns for p in other.glob('copy-*.txt')}) == 1
    assert not any(b'PRIVATE KEY' in p.read_bytes() for p in other.iterdir())
assert not any(b'PRIVATE KEY' in p.read_bytes() for p in files.iterdir())
def confirmation(data):
    codes = [line.removeprefix('Confirmation code: ') for line in data.decode().splitlines() if line.startswith('Confirmation code: ')]
    assert len(codes) == 1 and codes[0].startswith('pwnden{') and codes[0].endswith('}')
    return codes[0]


answer = confirmation(DOCUMENT)
assert hashlib.sha256(answer.encode()).hexdigest() == tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
for copy in copies:
    if copy.read_bytes() != DOCUMENT:
        wrong = confirmation(copy.read_bytes())
        assert hashlib.sha256(wrong.encode()).hexdigest() != tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
assert answer not in Path('README.md').read_text()
assert len({confirmation(copy.read_bytes()) for copy in copies}) == 3
print('Genuine old and current approvals, rejected stale/tampered codes, equal lengths, changed byte/signature/key and regeneration passed')
