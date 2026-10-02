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
                                   publication TEXT NOT NULL CHECK(publication IN ('published','draft')),
                                   body TEXT NOT NULL, PRIMARY KEY(document_id, version));
        ''')
        db.executemany('INSERT INTO documents VALUES (?, ?, ?)',
                       [(10, 'Public meeting notice', 'active'), (26, 'Board recovery procedure', 'active'),
                        (31, 'Public contact guide', 'active'), (40, 'Retired test board', 'deleted')])
        db.executemany('INSERT INTO revisions VALUES (?, ?, ?, ?)',
                       [(10, 1, 'published', 'Meeting is on Friday.'),
                        (26, 1, 'published', 'Retired code: pwnden{previous_backup_code}'),
                        (26, 2, 'published', 'Internal board recovery code: ' + KEY),
                        (26, 3, 'draft', 'Unapproved draft code: pwnden{draft_is_not_published}'),
                        (31, 1, 'published', 'Contact the board manager for assistance.'),
                        (40, 99, 'published', 'Other test board code: pwnden{unrelated_deleted_board}')])
        db.execute('UPDATE documents SET status = "deleted" WHERE id = 26')
        with (target / 'visible-documents.csv').open('w', newline='') as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(['id', 'title'])
            writer.writerows(db.execute('SELECT id, title FROM documents WHERE status = "active" ORDER BY id'))


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1] / 'files')
