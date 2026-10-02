# Problem format validation

This repository owns the [problem contract](contract.md) and checks its machine-readable values and manifests before publication. Run this command from the repository root with Python 3.11 or newer:

```sh
python3 tools/validate.py
```

The validator reads `contract.toml`, discovers `challenges/*/challenge.toml`, and checks the contract version, required fields, types, allowed values, file and service rules, endpoint declarations, patch declarations and `[content]`. Player documents must be distinct nonempty UTF-8 Markdown files, at most 1 MiB each, with up to 10 ordered hints. Declared distribution, content and Compose paths must exist inside this repository, including their symlink targets. Errors identify the manifest and offending field. Review the learning design against the [authoring standard](authoring-standard.md#review-before-publication) and the rendered content against the [player content checklist](player-content.md#author-review).

Run the format validator's regression checks with:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

Both commands use Python's standard library and run with this repository alone.

The regression suite also checks the [problem generator](creating.md), its file
and service templates, optional patches, contract defaults, safe creation and
incomplete-solution behavior. Generated manifests pass these format rules;
complete learning, content and execution review remain the author's publication gate.
The generated `AUTHORING.md` is a maintainer record. The format validator currently
checks the declared contract and resources; it does not enforce completion of that
record or determine prerequisite coverage and educational suitability.

## Maintainer execution checks

With sibling checkouts and the platform development prerequisites available, run from `platform`:

```sh
go run ./cmd/pwnden --repo ../challenges validate rotor-lock
go run ./cmd/pwnden --repo ../challenges verify rotor-lock
go run ./cmd/pwnden --repo ../challenges validate note-vault
go run ./cmd/pwnden --repo ../challenges run note-vault
go run ./cmd/pwnden --repo ../challenges verify note-vault
go run ./cmd/pwnden --repo ../challenges stop note-vault
```

Rotor Lock uses the pinned solution image without a service. Note Vault verification checks flag recovery, rejection by the patched service, its functional behavior and cleanup. Maintainer commands exercise authored declarations; player briefs describe the website workflow instead.

## GitHub Actions

`.github/workflows/verify.yml` runs the regression checks and validates all manifests on pushes to `main`, pull requests, and manual dispatches. Commit and push these files to activate the workflow. Its checkout uses read-only repository permissions and does not persist credentials.

Execution, flag recovery, patch behavior, and Docker cleanup are verified by the consuming runner. The [platform verification guide](https://github.com/pwnden/platform/blob/main/docs/verification.md) explains those checks. Format validation checks declarations; the execution check resolves Compose and observes the running problem.
