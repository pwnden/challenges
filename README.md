# pwnden challenges

Scenario authoring, verification and catalog publication for pwnden. Add each scenario under `challenges/<slug>/` with a `challenge.toml`. This repository owns the [complete problem contract](docs/contract.md) and the machine-readable version, defaults, and result code in [`contract.toml`](contract.toml).

This repository is the allowed root for host bind mounts. Keep Compose bind sources and build contexts inside this checkout. File-only challenges need no Compose file.

Use the [authoring standard](docs/authoring-standard.md) to define a scenario's
security learning objective, intended learner, prerequisite abilities and
difficulty evidence. Keep the design and review evidence in its `AUTHORING.md`.
Use the [scenario writing framework](docs/scenario-authoring.md) for a request
briefing, progressive additional information and a complete investigation report.
The [learning map](docs/learning-map.md) defines areas, topics, observable
experiments, scoped prerequisites and required tool capabilities.
Learning areas are independent of contract categories; the
[execution feasibility map](docs/execution-feasibility.md) distinguishes current
execution shapes, artifact-only scope and unverified runtime profiles.

Create the directory, manifest, author record, learning content and execution scaffold with
`python3 tools/create.py <slug> --kind file --category rev` or
`python3 tools/create.py <slug> --kind service --category web`.
See [creating scenarios](docs/creating.md) for options and the authoring workflow.

| Scenario | Category | Runtime |
| --- | --- | --- |
| [Rotor Lock](challenges/rotor-lock/README.md) | rev | File only |
| [Note Vault](challenges/note-vault/README.md) | web | One service, solution and patch checks |
| [Forgotten Shelf](challenges/forgotten-shelf/README.md) | web | Exposed backup, solution and patch checks |
| [Query Desk](challenges/query-desk/README.md) | web | Real SQL search, solution and patch checks |
| [Wrapped Secret](challenges/wrapped-secret/README.md) | crypto | File and prepared decoding command |
| [Midnight Trace](challenges/midnight-trace/README.md) | forensics | Correlate captured HTTP and audit records |
| [Paper Session](challenges/paper-session/README.md) | web | Browser cookie claims, solution and patch checks |
| [Path Parcel](challenges/path-parcel/README.md) | web | Actual relative file reads, solution and patch checks |
| [Hash Lantern](challenges/hash-lantern/README.md) | crypto | Compare six password candidates using the prepared hash command |
| [False Label](challenges/false-label/README.md) | forensics | Identify a mislabeled archive by bytes and parse its contents |
| [DNS Detour](challenges/dns-detour/README.md) | forensics | Reassemble data from captured local DNS query labels |
| [Borrowed Badge](challenges/borrowed-badge/README.md) | misc | Scoped local resource policy, solution and patch checks |

The [first experiment guide](docs/first-experiments.md) maps the new scenarios to
their learning topics, tools and review status. Each brief supplies the scoped
background needed to begin without writing Python.

The [second experiment guide](docs/second-experiments.md) covers six additional
scenarios and their scoped learning evidence. Reusable [starting knowledge](knowledge/README.md)
is maintained once and compiled into the new player briefs by the author tools.

Each challenge declares its player brief, ordered hints and complete walkthrough in `[content]`. Players read these in the website, open analysis materials there, use its prepared terminal and submit flags. Follow the [player content standard](docs/player-content.md). Executable solutions and patch sources support author verification; maintainer commands belong in [verification](docs/verification.md).

Run `python3 tools/validate.py` for format checks and `python3 tools/verify.py`
for complete target, solution, patch and cleanup verification. These author tools
use Python 3.11 or newer and Docker Engine 28 or newer with Compose, independently
of platform, Go or frontend tools. See [author verification](docs/verification.md).
After reviewing and committing the completed catalog, run
`python3 tools/publish.py --check` to check that exact commit and
`python3 tools/publish.py` to publish it to `origin/main`.
See [catalog publication](docs/publishing.md) for gates and prerequisites.
The [platform repository](https://github.com/pwnden/platform) independently consumes
published catalogs and checks their integration with the player.
