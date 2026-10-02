# pwnden challenges

Problem definitions, contract ownership, and metadata validation for pwnden. Add each challenge under `challenges/<slug>/` with a `challenge.toml`. This repository owns the [complete problem contract](docs/contract.md) and the machine-readable version, defaults, and result code in [`contract.toml`](contract.toml).

This repository is the allowed root for host bind mounts. Keep Compose bind sources and build contexts inside this checkout. File-only challenges need no Compose file.

Use the [authoring standard](docs/authoring-standard.md) to define a problem's
security learning objective, intended learner, prerequisite abilities and
difficulty evidence. Keep the design and review evidence in its `AUTHORING.md`.
The [learning map](docs/learning-map.md) defines areas, topics, observable
experiments, scoped prerequisites and required tool capabilities.

Create the directory, manifest, author record, learning content and execution scaffold with
`python3 tools/create.py <slug> --kind file --category rev` or
`python3 tools/create.py <slug> --kind service --category web`.
See [creating problems](docs/creating.md) for options and the authoring workflow.

| Challenge | Category | Runtime |
| --- | --- | --- |
| [Rotor Lock](challenges/rotor-lock/README.md) | rev | File only |
| [Note Vault](challenges/note-vault/README.md) | web | One service, solution and patch checks |

Each challenge declares its player brief, ordered hints and complete walkthrough in `[content]`. Players read these in the website, open analysis materials there, use its prepared terminal and submit flags. Follow the [player content standard](docs/player-content.md). Executable solutions and patch sources support author verification; maintainer commands belong in [verification](docs/verification.md).

Run `python3 tools/validate.py` to check the contract definition and every manifest using Python 3.11 or newer. See [format validation and CI](docs/verification.md) for details. A compatible runner owns execution and solution verification; the [platform repository](https://github.com/pwnden/platform) provides that runner.
