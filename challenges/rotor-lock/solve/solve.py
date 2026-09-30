"""Invert the byte transform, then exercise the distributed checker."""

from pathlib import Path
import runpy
import subprocess
import sys


def solve():
    root = Path(__file__).resolve().parents[1]
    checker = root / "files" / "checker.py"
    target = runpy.run_path(str(checker))["TARGET"]
    previous = 0xA7
    decoded = bytearray()
    for index, encoded in enumerate(target):
        shift = index % 7 + 1
        mixed = ((encoded >> shift) | (encoded << (8 - shift))) & 0xFF
        decoded.append(mixed ^ ((0x53 + 13 * index) & 0xFF) ^ previous)
        previous = encoded
    flag = decoded.decode("utf-8")
    accepted = subprocess.run(
        [sys.executable, str(checker), flag], capture_output=True, check=False,
    )
    rejected = subprocess.run(
        [sys.executable, str(checker), flag + "!"], capture_output=True, check=False,
    )
    if accepted.returncode != 0 or accepted.stdout.strip() != b"unlocked":
        raise SystemExit("recovered input did not open the lock")
    if rejected.returncode != 1:
        raise SystemExit("checker accepted an invalid input")
    print(flag)


if __name__ == "__main__":
    solve()
