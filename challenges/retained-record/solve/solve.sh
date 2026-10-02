#!/bin/bash
set -euo pipefail
sqlite3 -readonly files/snapshot.sqlite '
SELECT r.body FROM documents d JOIN revisions r ON r.document_id = d.id
WHERE d.status = "deleted" ORDER BY r.version DESC LIMIT 1;
' | rg -o 'pwnden\{[^}]+\}'
