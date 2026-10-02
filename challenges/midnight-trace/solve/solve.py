"""Correlate the exact distributed records; do not guess from matching times."""
import json
from pathlib import Path
import re

access = [json.loads(line) for line in Path("files/access.log").read_text().splitlines() if not line.startswith("#")]
audit = [json.loads(line) for line in Path("files/audit.jsonl").read_text().splitlines()]
by_id = {row["request_id"]: row for row in audit}
if len(by_id) != len(audit):
    raise SystemExit("ambiguous audit request IDs")
leaks = []
for row in access:
    event = by_id[row["request_id"]]
    if row["status"] == 200 and row["user"] == "guest" and event["owner"] != row["user"]:
        leaks.append(event["response"]["recovery_key"])
if len(leaks) != 1 or re.fullmatch(r"pwnden\{[a-z_]+\}", leaks[0]) is None:
    raise SystemExit("expected exactly one successful guest access to another owner's export")
print(leaks[0])
