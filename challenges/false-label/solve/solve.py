"""Inspect bytes and stream an archive member; do not extract files to disk."""
from pathlib import Path
import re
import subprocess


def solve():
    source = Path('files/banner.png')
    assert source.read_bytes().startswith(b'\x1f\x8b\x08')
    listing = subprocess.run(['tar', '-tzf', str(source)], capture_output=True, text=True, check=True, timeout=5)
    assert 'recovery/key.txt' in listing.stdout.splitlines()
    result = subprocess.run(['tar', '-xOzf', str(source), 'recovery/key.txt'], capture_output=True, text=True, check=True, timeout=5)
    flag = re.fullmatch(r'pwnden\{[a-z_]+\}', result.stdout.strip())
    assert flag
    print(flag[0])


if __name__ == '__main__':
    solve()
