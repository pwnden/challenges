# pwnden challenges

Problem definitions, contract ownership, and metadata validation for pwnden. Add each challenge under `challenges/<slug>/` with a `challenge.toml`. This repository owns the [complete problem contract](docs/contract.md) and the machine-readable version, defaults, and result code in [`contract.toml`](contract.toml).

This repository is the allowed root for host bind mounts. Keep Compose bind sources and build contexts inside this checkout. File-only challenges need no Compose file.

| Challenge | Category | Runtime |
| --- | --- | --- |
| [Rotor Lock](challenges/rotor-lock/README.md) | rev | File only |
| [Note Vault](challenges/note-vault/README.md) | web | One service, solution and patch checks |

Each challenge README includes its distribution files and execution instructions. Solutions and patch sources are stored alongside the challenge for authors and reviewers.

Run `python3 tools/validate.py` to check the contract definition and every manifest using Python 3.11 or newer. See [format validation and CI](docs/verification.md) for details. A compatible runner owns execution and solution verification; the [platform repository](https://github.com/pwnden/platform) provides that runner.
