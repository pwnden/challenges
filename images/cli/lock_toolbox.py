#!/usr/bin/env python3
"""Resolve signed Kali package indexes in a disposable preparation container.

Run after apt-get update in the digest-pinned base image; builds use the saved
package URLs and SHA256s, without consulting a moving package index.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("container")
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    groups = json.loads((directory / "toolbox-packages.json").read_text())

    def run(*argv):
        return subprocess.check_output(["docker", "exec", args.container, *argv], text=True)

    selected = []
    for profile, names in groups.items():
        selected.extend(names)
        output = run("apt-get", "--simulate", "--no-install-recommends", "install", *selected)
        packages = re.findall(r"^Inst (\S+)(?: \[[^]]+\])? \((\S+)", output, re.M)
        records = []
        metadata = run("apt-cache", "show", *(f"{name}={version}" for name, version in packages))
        for paragraph in metadata.strip().split("\n\n"):
            fields = dict(line.split(": ", 1) for line in paragraph.splitlines() if ": " in line and not line.startswith(" "))
            records.append((fields["Package"], fields["Version"], "https://kali.download/kali/" + fields["Filename"], fields["SHA256"]))
        content = "# package\tversion\turl\tsha256\n" + "".join("\t".join(record) + "\n" for record in sorted(records))
        (directory / f"{profile}.apt.lock").write_text(content)
        print(f"{profile}: {len(records)} packages, lock sha256 {hashlib.sha256(content.encode()).hexdigest()}", flush=True)


if __name__ == "__main__":
    main()
