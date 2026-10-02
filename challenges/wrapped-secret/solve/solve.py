"""Verify the exact no-programming command available in the player toolbox."""
import re
import subprocess

result = subprocess.run(["base64", "--decode", "files/recovery.txt"], check=True, capture_output=True, text=True)
flag = result.stdout.strip()
if re.fullmatch(r"pwnden\{[a-z_]+\}", flag) is None:
    raise SystemExit("the decoded material did not contain a recovery key")
print(flag)
