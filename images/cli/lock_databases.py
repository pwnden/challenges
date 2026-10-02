#!/usr/bin/env python3
"""Save immutable offline vulnerability DB references for image preparation."""
import hashlib
import json
import urllib.request
from pathlib import Path


def read(url, headers=None):
    request = urllib.request.Request(url, headers={"User-Agent": "grype/0.120.0", **(headers or {})})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def main():
    root = Path(__file__).resolve().parent
    grype = json.loads(read("https://grype.anchore.io/databases/v6/latest.json"))
    records = {"grype": {"version": grype["schemaVersion"], "built": grype["built"],
                          "url": "https://grype.anchore.io/databases/v6/" + grype["path"],
                          "sha256": grype["checksum"].removeprefix("sha256:")}}
    repository = "aquasecurity/trivy-db"
    token = json.loads(read(f"https://ghcr.io/token?scope=repository:{repository}:pull&service=ghcr.io"))["token"]
    manifest_bytes = read(f"https://ghcr.io/v2/{repository}/manifests/2", {
        "Authorization": "Bearer " + token, "Accept": "application/vnd.oci.image.manifest.v1+json"})
    manifest = json.loads(manifest_bytes)
    layer = manifest["layers"][0]
    records["trivy"] = {"version": "schema-2", "manifest": "sha256:" + hashlib.sha256(manifest_bytes).hexdigest(),
                         "repository": repository, "sha256": layer["digest"].removeprefix("sha256:"),
                         "url": f"https://ghcr.io/v2/{repository}/blobs/" + layer["digest"]}
    (root / "databases.lock.json").write_text(json.dumps(records, indent=2) + "\n")
    print(records)


if __name__ == "__main__":
    main()
