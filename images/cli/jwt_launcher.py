"""Initialize JWT Tool in the player's temporary home, then run the CLI."""
import configparser
import fcntl
import os
import subprocess
import sys
from pathlib import Path

PYTHON = "/opt/python-tools/bin/python"
SOURCE = Path("/opt/upstream/jwt_tool/jwt_tool.py")


def main():
    if not any(argument in ("-h", "--help") for argument in sys.argv[1:]):
        directory = Path.home() / ".jwt_tool"
        directory.mkdir(mode=0o700, exist_ok=True)
        config_path = directory / "jwtconf.ini"
        # Concurrent terminals can share the same temporary home. Generate
        # per-player keys once, with private permissions and no baked-in keys.
        os.umask(0o077)
        with (directory / ".initialize.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if not config_path.exists():
                result = subprocess.run([PYTHON, str(SOURCE)], capture_output=True,
                                        text=True, timeout=60)
                # Upstream intentionally exits 1 after creating its config.
                if result.returncode != 1 or not config_path.exists():
                    raise RuntimeError("JWT Tool initialization failed:\n" + result.stdout + result.stderr)
                config = configparser.ConfigParser()
                config.optionxform = str
                config.read(config_path)
                config["services"].update(proxy="False", jwksdynamic="", httplistener="")
                for key, filename in (("wordlist", "jwt-common.txt"),
                                      ("commonHeaders", "common-headers.txt"),
                                      ("commonPayloads", "common-payloads.txt")):
                    config["input"][key] = str(SOURCE.parent / filename)
                temporary = config_path.with_suffix(".tmp")
                with temporary.open("w") as output:
                    config.write(output)
                temporary.replace(config_path)
    os.execv(PYTHON, [PYTHON, str(SOURCE), *sys.argv[1:]])


if __name__ == "__main__":
    main()
