#!/usr/bin/env python3
"""Check command coverage and functional fixtures with the player limits."""
import argparse
import json
import subprocess
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--profile", choices=("extended", "specialized", "restricted"), default="restricted")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    inspection = json.loads(subprocess.check_output(["docker", "image", "inspect", args.image]))[0]
    assert inspection["Architecture"] == "amd64"
    assert inspection["Config"]["User"] == "10001:10001"
    assert not inspection["Config"].get("Volumes")
    groups = json.loads((HERE / "commands.json").read_text())
    commands = []
    for profile, names in groups.items():
        commands.extend(names)
        if profile == args.profile:
            break
    source = "COMMANDS = " + repr(commands) + "\n" + (HERE / "probe_toolbox.py").read_text()
    name = "pwnden-cli-verify-" + uuid.uuid4().hex[:12]
    print("container", name, flush=True)
    argv = ["docker", "run", "--name", name, "-i", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--cpus", "2",
            "--memory", "2g", "--memory-swap", "2g", "--pids-limit", "256",
            "--tmpfs", "/tmp:rw,exec,nosuid,nodev,size=128m",
            "--tmpfs", "/home/pwnden:rw,nosuid,nodev,uid=10001,gid=10001,size=64m",
            "--tmpfs", "/challenge:rw,exec,nosuid,nodev,uid=10001,gid=10001,size=256m,nr_inodes=32768",
            args.image, "/usr/bin/python3", "-"]
    try:
        result = subprocess.run(argv, input=source, text=True, capture_output=True, timeout=900)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        state = json.loads(subprocess.check_output(["docker", "inspect", name]))[0]
        report = {"image": args.image, "id": inspection["Id"], "size": inspection.get("Size"),
                  "profile": args.profile, "exit_code": result.returncode,
                  "oom_killed": state["State"]["OOMKilled"], "checks": rows, "stderr": result.stderr[-3000:]}
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        failures = [row["name"] for row in rows if not row["passed"]]
        print(json.dumps({"passed": len(rows) - len(failures), "failed": failures,
                          "commands": len(commands), "exit": result.returncode, "report": str(args.report)}))
        raise SystemExit(1 if failures or result.returncode or not rows else 0)
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


if __name__ == "__main__":
    main()
