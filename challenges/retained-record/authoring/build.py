"""Apply a logical deletion and export a list and DB from the same state."""
import csv
from pathlib import Path
import sqlite3

KEY = 'pwnden{hidden_rows_remain_in_backup}'


def build(target):
    target.mkdir(parents=True, exist_ok=True)
    path = target / 'snapshot.sqlite'
    if path.exists():
        path.unlink()
    with sqlite3.connect(path) as db:
        db.executescript('''
            CREATE TABLE documents(id INTEGER PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL);
            CREATE TABLE revisions(document_id INTEGER NOT NULL REFERENCES documents(id), version INTEGER NOT NULL,
                                   body TEXT NOT NULL, PRIMARY KEY(document_id, version));
        ''')
        db.executemany('INSERT INTO documents VALUES (?, ?, ?)',
                       [(10, 'Public meeting notice', 'active'), (26, 'Board recovery procedure', 'active'),
                        (31, 'Public contact guide', 'active')])
        db.executemany('INSERT INTO revisions VALUES (?, ?, ?)',
                       [(10, 1, 'Meeting is on Friday.'), (26, 1, 'Old recovery code was retired.'),
                        (26, 2, 'Internal board recovery code: ' + KEY),
                        (31, 1, 'Contact the board manager for assistance.')])
        db.execute('UPDATE documents SET status = "deleted" WHERE id = 26')
        with (target / 'visible-documents.csv').open('w', newline='') as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(['id', 'title'])
            writer.writerows(db.execute('SELECT id, title FROM documents WHERE status = "active" ORDER BY id'))


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1] / 'files')
