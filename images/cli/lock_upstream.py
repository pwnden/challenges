#!/usr/bin/env python3
"""Refresh upstream source/release checksums deliberately, never at runtime."""
import hashlib
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(url):
    request = urllib.request.Request(url, headers={"User-Agent": "pwnden-toolbox-lock"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def main():
    records = {}
    releases = {
        "yq": ("mikefarah/yq", "yq_linux_amd64"),
        "grype": ("anchore/grype", "_linux_amd64.tar.gz"),
        "trivy": ("aquasecurity/trivy", "_Linux-64bit.tar.gz"),
        "foundry": ("foundry-rs/foundry", "_linux_amd64.tar.gz"),
        "pwndbg": ("pwndbg/pwndbg", "_x86_64-portable.tar.xz"),
        "mc": ("minio/mc", "mc.linux-amd64.RELEASE."),
    }
    for name, (repo, match) in releases.items():
        release = json.loads(read(f"https://api.github.com/repos/{repo}/releases/latest"))
        asset = next(item for item in release["assets"] if match in item["name"] and
                     not item["name"].endswith((".asc", ".minisig", ".sha256sum", ".shasum")) and
                     not item["name"].startswith("pwndbg-lldb"))
        records[name] = {"version": release["tag_name"], "url": asset["browser_download_url"],
                         "sha256": asset["digest"].removeprefix("sha256:")}
    for name, repo in {
        "honggfuzz": "google/honggfuzz", "jwt_tool": "ticarpi/jwt_tool",
        "rsactftool": "RsaCtfTool/RsaCtfTool", "nuclei_templates": "projectdiscovery/nuclei-templates",
        "capa_rules": "mandiant/capa-rules",
    }.items():
        commit = json.loads(read(f"https://api.github.com/repos/{repo}/commits/HEAD"))["sha"]
        url = f"https://codeload.github.com/{repo}/tar.gz/{commit}"
        records[name] = {"version": commit, "url": url, "sha256": hashlib.sha256(read(url)).hexdigest()}
    # Solidity's release list supplies its own content hash for the compiler.
    compilers = json.loads(read("https://binaries.soliditylang.org/linux-amd64/list.json"))
    version = compilers["latestRelease"]
    build = next(item for item in compilers["builds"] if item["path"] == compilers["releases"][version])
    records["solc"] = {"version": version, "url": "https://binaries.soliditylang.org/linux-amd64/" + build["path"],
                       "sha256": build["sha256"].removeprefix("0x")}
    (HERE / "upstream.lock.json").write_text(json.dumps(records, indent=2) + "\n")
    print("locked", ", ".join(records), flush=True)


if __name__ == "__main__":
    main()
