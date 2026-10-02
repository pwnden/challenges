# Author verification

The challenges repository owns the complete author workflow: problem design,
declarations, target and solution verification, patch checks and catalog
publication. Python 3.11 or newer, Docker Engine 28 or newer with Linux containers,
and Docker Compose are the execution prerequisites. These tools run with this
checkout alone. Go, a platform checkout and frontend assets are unnecessary.

## Format checks

From the repository root:

```sh
python3 tools/validate.py
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

The validator discovers `challenges/*/challenge.toml`, reads `contract.toml`, and
checks version, fields, values, file/service rules, endpoints, patches, player
tools, difficulty and declared player documents. Paths and symlink targets stay
inside the repository. Declared Markdown files are distinct, nonempty UTF-8,
at most 1 MiB, with up to 10 ordered hints.

Scenarios with a `BRIEFING.md` source compile shared prerequisite notes using
`python3 tools/content.py`. Format validation also checks that their player
`README.md` matches that source and the referenced notes. A changed concept
requires refreshing the consuming briefs before verification or publication.

The regression suite covers format rules, generation, execution boundaries,
result semantics, timeout/interruption and resource cleanup. Format validation
does not establish target execution, author-record completeness or learning
suitability. Follow the [authoring standard](authoring-standard.md) and
[player-content review](player-content.md#author-review).

## Author execution checks

Verify one problem or the whole catalog:

```sh
python3 tools/verify.py note-vault
python3 tools/verify.py
```

Multiple slugs can be supplied. `--repo <path>` selects another challenges
checkout. All manifests are format-checked before the selected problems run.
This author verifier explicitly supports contract version 5; update its
implementation when the authoring contract changes.

For each selected problem, the verifier:

1. Resolves both vulnerable and optional patched Compose models and checks
   repository-contained inputs and project-scoped resources before starting
   services. Environment-file paths are checked before resolving their contents.
2. Preserves the exercise configuration while removing published ports,
   isolating every bridge network, dropping all capabilities and enabling
   `no-new-privileges`. It inspects live network ownership and configuration
   before attaching a toolbox.
3. Runs the declared solution in its image. File toolboxes use network `none`
   and SHA-256 comparison; services receive a fresh generated flag and the
   toolbox joins only the declared problem network.
4. For a declared patch, starts a separate project, rejects continued flag
   recovery, accepts only normal completion or the contract's attack-denial
   code, and requires the functional check to succeed. Connection/launch/signal
   errors and unexpected exit codes fail verification.
5. Removes toolboxes and both projects on success, failure, timeout or handled
   interruption. It checks that project containers, networks and volumes are
   absent; cleanup failure prevents a successful result.

Verification uses fresh invocation-specific project/container identities and
does not adopt or stop the player's existing environments. Images/build caches
remain. `solve.writable` follows the contract: permitted repository writes can
remain after verification, so authors must design those writes deliberately.

Missing toolbox images are prepared before the command's declared runtime limit.
`--prepare-timeout 300` controls image preparation and service startup separately;
change it when the authored profile needs a longer preparation period. A
timeout still requires cleanup. Generated flags are passed through the child
environment and configuration stdin, with no flag-bearing configuration file,
and redacted from verifier diagnostics.

The generator deliberately creates incomplete solution stubs. A newly generated
manifest can pass format checks while execution checks fail until the author
implements the actual exercise.

## Actual network isolation

On Linux/WSL with a locally accessible Docker bridge:

```sh
python3 -B tools/check_isolation.py
```

This standalone check uses the pinned Python toolbox image and fresh controls.
It first establishes that a synthetic host listener and a service on another
network are reachable from the control network. From the isolated toolbox it
requires Internet IPv4/IPv6/DNS, host and peer connections to fail while
same-problem HTTP succeeds. The target and controls are cleaned up afterward.
This check uses neither platform code nor a running player environment.

The host-listener check requires the Python host to reach the Docker bridge
address; it fails explicitly when that setup is unavailable. Windows/macOS
actual host checks remain later work. The shared runtime still uses portable
paths and the same Docker contract. Docker and its kernel remain trusted;
ordinary network and mount checks do not establish resistance to kernel or
daemon exploits.

## GitHub Actions

`.github/workflows/verify.yml` checks out only challenges with read-only
permissions and credentials not persisted. On main pushes, pull requests and
manual dispatch it runs author-tool regressions, format validation, actual
network isolation and every declared solution/patch/cleanup check. New manifests
join discovery automatically. No platform revision, Go setup, frontend build
or consumer artifact is used by these publication checks.

## Publication gate

`python3 tools/publish.py --check` runs regressions, actual network isolation and
the complete execution check on an immutable committed snapshot. After a pass,
`python3 tools/publish.py` publishes the checked commit. See
[catalog publication](publishing.md) for the author workflow and Git requirements.

## Consumer integration

A consumer independently implements the versioned contract and its runtime
policy, and tests its use of published problems. The platform's own tests cover
catalog acquisition, player tools, browser ingress, submissions and lifecycle.
They are consumer integration evidence; authoring verification finishes in
challenges before publication. See the
[platform integration guide](https://github.com/pwnden/platform/blob/main/docs/verification.md).
