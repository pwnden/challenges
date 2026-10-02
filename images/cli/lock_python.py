#!/usr/bin/env python3
"""Convert a Linux amd64 / Python 3.13 pip --report resolution to a hash lock."""
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
lines = ["# Python 3.13 / Linux amd64. Resolved with pip --report; artifact hashes included."]
for item in sorted(report["install"], key=lambda item: item["metadata"]["name"].lower()):
    lines.append(item["metadata"]["name"] + "==" + item["metadata"]["version"] +
                 " --hash=sha256:" + item["download_info"]["archive_info"]["hashes"]["sha256"])
Path(__file__).with_name("python-toolbox.lock").write_text("\n".join(lines) + "\n")
print(len(report["install"]), "pinned Python distributions")
