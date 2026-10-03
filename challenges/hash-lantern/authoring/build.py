"""Rebuild the unsalted-hash teaching evidence."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ['pwnden{' + value + '}' for value in ['mintmoon42', 'riverlamp8', 'rainboat27', 'quietdock6', 'cedarstep3', 'paperkite9']]


def build():
    files = ROOT / 'files'
    files.mkdir(exist_ok=True)
    digest = hashlib.sha256(b'pwnden{rainboat27}').hexdigest()
    (files / 'account.txt').write_text('account=backup-reader\nalgorithm=SHA-256\nencoding=UTF-8\nsalt=none\npassword_hash=' + digest + '\n', encoding='utf-8')
    (files / 'candidates.txt').write_text('\n'.join(CANDIDATES) + '\n', encoding='utf-8')


if __name__ == '__main__':
    build()
