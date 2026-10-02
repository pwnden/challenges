#!/usr/bin/env python3
"""Install hash-pinned CLI artifacts and offline assets during image build."""
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path("/opt/toolbox")
CACHE = Path("/tmp/upstream-downloads")


def fetch(name, record, headers=None):
    CACHE.mkdir(parents=True, exist_ok=True)
    destination = CACHE / record["sha256"]
    if not destination.exists():
        request = urllib.request.Request(record["url"], headers={"User-Agent": "grype/0.120.0", **(headers or {})})
        temporary = destination.with_suffix(".part")
        with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        temporary.replace(destination)
    with destination.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != record["sha256"]:
        destination.unlink()
        raise RuntimeError(f"{name}: SHA256 mismatch")
    print(f"verified {name} {record['version']}", flush=True)
    return destination


def extract(archive, directory, strip=False):
    directory.mkdir(parents=True, exist_ok=True)
    command = ["tar", "--no-same-owner", "-xf", str(archive), "-C", str(directory)]
    if strip:
        command += ["--strip-components=1"]
    subprocess.run(command, check=True)


def executable(name, path):
    path.chmod(0o755)
    destination = Path("/usr/local/bin") / name
    destination.symlink_to(path)


def wrapper(name, text):
    path = Path("/usr/local/bin") / name
    path.write_text("#!/bin/sh\nset -eu\n" + text + "\n")
    path.chmod(0o755)


def main():
    sources = json.loads((ROOT / "upstream.lock.json").read_text())
    artifacts = {name: fetch(name, record) for name, record in sources.items()}
    for name in ("yq", "mc", "solc"):
        path = Path("/opt/upstream") / name / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(artifacts[name], path)
        executable(name, path)
    for name in ("foundry", "grype", "trivy"):
        directory = Path("/opt/upstream") / name
        extract(artifacts[name], directory)
        for command in (("cast", "forge", "anvil", "chisel") if name == "foundry" else (name,)):
            # Foundry's unrelated Solidity REPL "chisel" conflicts with the
            # network proxy. Keep the proxy's established command name.
            executable("foundry-chisel" if command == "chisel" else command, directory / command)
    extract(artifacts["pwndbg"], Path("/opt/upstream"))
    executable("pwndbg", Path("/opt/upstream/pwndbg/bin/pwndbg"))
    extract(artifacts["honggfuzz"], Path("/opt/upstream/honggfuzz"), strip=True)
    subprocess.run(["make", "-j2"], cwd="/opt/upstream/honggfuzz", check=True)
    executable("honggfuzz", Path("/opt/upstream/honggfuzz/honggfuzz"))
    for command in ("hfuzz-clang", "hfuzz-clang++", "hfuzz-gcc", "hfuzz-g++"):
        executable(command, Path("/opt/upstream/honggfuzz/hfuzz_cc") / command)
    for name in ("jwt_tool", "rsactftool", "nuclei_templates", "capa_rules"):
        extract(artifacts[name], Path("/opt/upstream") / name, strip=True)
    subprocess.run(["/opt/python-tools/bin/pip", "install", "--no-deps", "--no-build-isolation", "/opt/upstream/rsactftool"], check=True)
    wrapper("jwt_tool.py", 'exec /opt/python-tools/bin/python /opt/toolbox/jwt_launcher.py "$@"')
    wrapper("httpx", 'exec /usr/bin/httpx-toolkit -duc "$@"')
    wrapper("jadx", 'exec /usr/share/jadx/bin/jadx "$@"')
    wrapper("nuclei", '''for argument do
    case "$argument" in -t|-templates|-t=*|-templates=*) exec /usr/bin/nuclei -duc -ni "$@" ;; esac
done
exec /usr/bin/nuclei -duc -ni -t /opt/upstream/nuclei_templates "$@"''')
    wrapper("gdb-gef", 'exec /usr/bin/gdb -nx -iex "source /usr/share/gdb/gef.py" "$@"')
    executable("7zz", Path("/usr/bin/7z"))
    executable("testssl.sh", Path("/usr/bin/testssl"))
    for command in ("semgrep", "capa", "floss", "vol", "volshell", "frida", "frida-ps", "frida-trace", "RsaCtfTool", "rsacrack"):
        executable(command, Path("/opt/python-tools/bin") / command)
    for command, script in (("ssh2john", "ssh2john.py"), ("office2john", "office2john.py")):
        wrapper(command, f'exec /usr/bin/python3 /usr/share/john/{script} "$@"')
    # Ruby resolves only these already verified local gems; no live registry.
    gems = json.loads((ROOT / "ruby-toolbox.lock.json").read_text())
    gem_directory = Path("/tmp/toolbox-gems")
    gem_directory.mkdir()
    for name, record in gems.items():
        shutil.copyfile(fetch(name, record), gem_directory / f"{name}-{record['version']}.gem")
    subprocess.run(["gem", "install", "--local", "--ignore-dependencies", "--no-document", *map(str, gem_directory.glob("*.gem"))], check=True)
    shutil.rmtree(gem_directory)
    # A DB snapshot is training data, not a claim to current vulnerability data.
    databases = json.loads((ROOT / "databases.lock.json").read_text())
    archive = Path("/tmp/grype-db.tar.zst")
    archive.symlink_to(fetch("grype-db", databases["grype"]))
    subprocess.run(["/opt/upstream/grype/grype", "db", "import", str(archive)], check=True,
                   env={**os.environ, "GRYPE_DB_CACHE_DIR": "/opt/grype-db", "GRYPE_CHECK_FOR_APP_UPDATE": "false"})
    archive.unlink()
    repository = databases["trivy"]["repository"]
    token_url = f"https://ghcr.io/token?scope=repository:{repository}:pull&service=ghcr.io"
    token = json.load(urllib.request.urlopen(token_url))["token"]
    extract(fetch("trivy-db", databases["trivy"], {"Authorization": "Bearer " + token}), Path("/opt/trivy-cache/db"))
    subprocess.run(["chmod", "-R", "a+rX", "/opt"], check=True)


if __name__ == "__main__":
    main()
