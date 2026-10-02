"""Reassemble DNS query labels in sequence order, preserving retransmission semantics."""
import json
from pathlib import Path
import re
import subprocess


def assemble(rows):
    chunks = {}
    for row in rows:
        if row['direction'] != 'Q':
            continue
        match = re.fullmatch(r'([12])-([A-Z2-7]{20})\.sync\.box\.test\.?', row['qname'], re.IGNORECASE)
        if not match:
            continue
        number, value = int(match[1]), match[2].upper()
        if number in chunks and chunks[number] != value:
            raise ValueError('conflicting copies of one sequence number')
        chunks[number] = value
    if set(chunks) != {1, 2}:
        raise ValueError('both query chunks are required')
    return ''.join(chunks[i] for i in (1, 2))


def reconstruct(rows):
    result = subprocess.run(['base32', '--decode'], input=assemble(rows),
                            capture_output=True, text=True, check=True, timeout=5)
    if not re.fullmatch(r'pwnden\{[a-z_]+\}', result.stdout):
        raise ValueError('decoded evidence is not a complete flag')
    return result.stdout


if __name__ == '__main__':
    rows = [json.loads(line) for line in Path('files/dns.jsonl').read_text().splitlines()]
    print(reconstruct(rows))
