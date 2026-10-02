from build import build, KEY
import csv
import hashlib
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import tomllib

query = 'SELECT r.body FROM documents d JOIN revisions r ON r.document_id = d.id WHERE d.status = "deleted" ORDER BY r.version DESC LIMIT 1;'
path = Path('files/snapshot.sqlite')
assert KEY in subprocess.check_output(['sqlite3', '-readonly', str(path), query], text=True)
with path.open('rb') as source:
    assert source.read(16) == b'SQLite format 3\0'
with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True) as db:
    active = list(db.execute('SELECT id, title FROM documents WHERE status = "active" ORDER BY id'))
    with Path('files/visible-documents.csv').open() as source:
        rows = list(csv.DictReader(source))
    assert active == [(int(row['id']), row['title']) for row in rows]
    assert list(db.execute('SELECT id FROM documents WHERE status = "deleted"')) == [(26,)]
with tempfile.TemporaryDirectory(dir='/tmp') as name:
    root = Path(name)
    build(root / 'regenerated')
    with sqlite3.connect(path) as original, sqlite3.connect(root / 'regenerated/snapshot.sqlite') as regenerated:
        assert list(original.iterdump()) == list(regenerated.iterdump())
    control = root / 'control.sqlite'
    shutil.copyfile(path, control)
    with sqlite3.connect(control) as db:
        db.execute('PRAGMA secure_delete = ON')
        db.execute('DELETE FROM revisions WHERE document_id = 26')
        db.commit()
        db.execute('VACUUM')
    assert subprocess.check_output(['sqlite3', '-readonly', str(control), query]) == b''
    assert KEY.encode() not in control.read_bytes()
assert hashlib.sha256(KEY.encode()).hexdigest() == tomllib.loads(Path('challenge.toml').read_text())['flag']['sha256']
assert KEY not in Path('README.md').read_text()
print('Real SQLite state, matching visible list, retained last revision, regeneration and purged-body control passed')
