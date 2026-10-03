# Author verification

The challenges repository owns the complete author workflow: problem design,
declarations, target and solution verification, patch checks and catalog
publication. Python 3.11 or newer, Docker Engine 28 or newer with Linux containers,
and Docker Compose are the execution prerequisites. These tools run with this
checkout alone. Go, a platform checkout and frontend assets are unnecessary.

Compose must support `start --wait` and `--wait-timeout`: services are created and
their mounts checked before they start. CI installs Compose 5.1.3 from the official
release with its SHA-256 checked. It builds the basic and pcap
[CLI images](../images/cli/README.md) before verifying the catalog. Prepare those
images locally as well; their exercise tags are built from this repository.

## Format checks

From the repository root:

```sh
python3 tools/validate.py
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

The validator discovers `challenges/*/challenge.toml`, reads `contract.toml`, and
checks version, fields, values, file/service rules, endpoints, patches, player
tools, primary CLI names, difficulty and declared player documents. Paths and symlink targets stay
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
Before running a solution, verification checks every declared `player.cli` command in its toolbox image with network access disabled. Missing commands fail publication.

This author verifier explicitly supports contract version 6; update its
implementation when the authoring contract changes.

For each selected problem, the verifier:

1. Resolves both vulnerable and optional patched Compose models and checks
   repository-contained inputs and project-scoped resources before starting
   services. Environment-file paths are checked before resolving their contents.
2. Preserves the exercise configuration while removing published ports,
   isolating every bridge network, dropping all capabilities and enabling
   `no-new-privileges`, enforcing the [author runtime limits](#runtime-limits).
   It inspects live network ownership and configuration
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
remain. Writable copies are removed after author verification; generated files
never change the author's repository.

Missing toolbox images are prepared before the command's declared runtime limit.
`--prepare-timeout 300` controls image preparation and service startup separately;
change it when the authored profile needs a longer preparation period. A
timeout still requires cleanup. Generated flags are passed through the child
environment and configuration stdin, with no flag-bearing configuration file,
and redacted from verifier diagnostics.

The generator deliberately creates incomplete solution stubs. A newly generated
manifest can pass format checks while execution checks fail until the author
implements the actual exercise.

## Runtime limits

The author runner rejects GPU/device access, privileged hooks, host namespaces,
extra capabilities and custom security profiles before startup. Services retain
their declared image and user, but receive a read-only root and an executable,
writable 128 MiB `/tmp` tmpfs. Declare separate temporary data mounts for writes
and use a non-root user in service images.

Services and toolboxes have per-container ceilings of 2 CPUs, 2 GiB memory,
no additional swap and 256 processes. Author resource declarations cannot
increase these limits. Memory is not reserved in advance. Toolboxes run as
`10001:10001` in both read-only and writable modes. A separate 64 MiB tmpfs at `/home/pwnden`
provides a writable home; caches and compiled exercises use `/tmp`.

`PWNDEN_CONTAINER_CPUS=1` tightens the service and toolbox CPU ceiling to one
CPU; the default is 2, and only 1 or 2 are accepted. Aggregate limits still apply
and remain clipped to daemon capacity. CI uses 1 so vulnerable and patched
targets, the active toolbox and their temporary workspace keepers fit its
four-core runner. Default-policy regressions run with 2.

Logs rotate through the `local` driver with 10 MiB per file and 3 files.
Command stdout and stderr each have an 8 MiB capture limit; exceeding either
fails verification and still performs cleanup. All solution and patch commands
use this policy. Writable repository binds are rejected. Named service volumes
use 256 MiB local-driver tmpfs with 32768 inodes and no automatic image copy.
Other declared tmpfs mounts are capped at 256 MiB and shared memory at 64 MiB.
Toolbox image `VOLUME` declarations are rejected; service image volumes require
explicit mounted paths. Volumes disappear on stop/unmount and are unsuitable for
durable data. Builds, downloads and image caches remain preparation operations.

Writable toolboxes share a 256 MiB problem-specific copy, retained by a small
networkless keeper until environment cleanup. Its ceilings are 0.25 CPU,
512 MiB memory and 32 processes; the memory allowance also accounts for the
workspace contents retained after a command exits. Commands and PTYs see the
same copy, while patched projects receive a separate copy. Originals never change.

On Linux/WSL, the Go consumer and Python author runner share a per-user, per-daemon
lock in `/tmp`. Creation reserves actual container ceilings before processes
start. The default aggregate budget is 8 CPUs, 8 GiB RAM, 1024 processes and
12 containers, clipped to the daemon's CPU/RAM capacity. Connectors and keepers
also count. Exceeding any dimension rejects creation, without interrupting
existing environments. Created and stopped managed containers count until removed;
unrelated applications do not count. Operator settings are positive integers:
`PWNDEN_RUNTIME_CPUS`, `PWNDEN_RUNTIME_MEMORY_MIB`, `PWNDEN_RUNTIME_PIDS`,
`PWNDEN_RUNTIME_CONTAINERS`. This admission policy assumes the controllers run
as the same local OS user; it is not a daemon-wide quota for other users or hosts.

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
