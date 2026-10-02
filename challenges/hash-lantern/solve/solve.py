"""Use the same sha256sum executable supplied to the player."""
from pathlib import Path
import subprocess


def solve():
    account = dict(line.split('=', 1) for line in Path('files/account.txt').read_text().splitlines())
    assert account['algorithm'] == 'SHA-256' and account['encoding'] == 'UTF-8' and account['salt'] == 'none'
    matches = []
    candidates = Path('files/candidates.txt').read_text().splitlines()
    for candidate in candidates:
        result = subprocess.run(['sha256sum'], input=candidate.encode(), capture_output=True, check=True, timeout=5)
        if result.stdout.decode().split()[0] == account['password_hash']:
            matches.append(candidate)
    if len(matches) != 1:
        raise ValueError('evidence must identify exactly one password candidate')
    print('pwnden{' + matches[0] + '}')


if __name__ == '__main__':
    solve()
