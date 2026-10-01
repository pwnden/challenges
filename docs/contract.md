# Problem contract v3

This contract defines player learning content, problem metadata, execution environment, solution and patch results, and resource lifecycle shared by problem authors and consumers. The challenges repository owns this document and the machine-readable values in [`contract.toml`](../contract.toml). Together they define contract version **3**. The TOML file contains the version, execution defaults, and a result code; this document specifies the complete rules.

Each challenge lives at `challenges/<slug>/challenge.toml`. Authors describe the problem there and supply its files, Compose configuration, solution, and optional patch. A compatible consumer reads those declarations and implements this contract.

## Ownership and compatibility

The challenges repository maintains the contract and checks problem declarations in its own validator and CI. The platform consumes the contract: it confirms version support, parses execution fields, applies filesystem and Docker execution safety checks, and verifies running problems. See [format validation and CI](verification.md) for the author checks and the [platform verification guide](https://github.com/pwnden/platform/blob/main/docs/verification.md) for execution checks.

The repository declares one positive integer `version`. Every problem's `schema` equals that version. The platform explicitly supports version `3` and retains version `1` and `2` execution support for installed snapshots, with the current network isolation policy applied to all supported versions. It rejects an unsupported repository or problem version before decoding execution fields or starting resources. Version agreement selects the behavior the consumer implements. Authors remain responsible for publishing valid declarations.

Increment the contract version whenever consumed fields, types, requiredness, allowed values, defaults, or execution and result rules change. Update the document, TOML values, author validator, and problem declarations together. A consumer adds explicit support for the new version before it can execute those problems. Adding problems, changing their content within the same contract, and clarifying documentation without changing a rule keep the version.

### Machine-readable contract values

All four fields in `contract.toml` are required. The author validator rejects unknown fields. These values belong to the versioned contract; editing them is a contract change.

| Field | Type | Version 3 value | Rule |
| --- | --- | --- | --- |
| `version` | Integer | `3` | Positive contract version; matches every problem's `schema`. |
| `solve_network` | String | `"default"` | Nonempty default Compose network key for service solutions. |
| `solve_timeout_seconds` | Integer | `60` | Positive default runtime limit for each toolbox command, in seconds. |
| `attack_rejected_exit` | Integer | `3` | Expected attack denial code; in the range 1–124. |

## Problem metadata reference

The tables below list all supported metadata fields. The author validator rejects unknown fields at every listed level. An integer is a TOML integer, a boolean is a TOML boolean, and a nonempty string contains at least one non-whitespace character. Command arguments are strings that are not empty; whitespace within an argument is preserved.

Paths are relative to the problem directory and follow the [files and resource rules](#files-and-resource-boundaries). A service problem has a nonempty `compose`; a file problem omits `compose` or uses an empty string.

### Top-level fields

| Field | Type | Required or default | Rule |
| --- | --- | --- | --- |
| `schema` | Integer | Required | Equals `contract.toml`'s `version`. |
| `slug` | String | Required | Matches the directory name; 1–40 characters; lowercase letters and digits separated by single hyphens. |
| `title` | String | Required | Nonempty display title. |
| `category` | String | Required | One of `web`, `pwn`, `rev`, `crypto`, `forensics`, or `misc`. |
| `content` | Table | Required | Player description, ordered optional hints and complete walkthrough. |
| `files` | Array of strings | Defaults to `[]`; nonempty for file problems | Existing distribution files or directories inside this repository. Service problems may also distribute files. |
| `compose` | String | Defaults to `""` | Existing regular Compose file for a service problem. |
| `endpoints` | Array of tables | Defaults to `[]` | Service entry points; file problems use an empty array. |
| `flag` | Table | Required | Flag comparison strategy described below. |
| `solve` | Table | Required | Toolbox image, command, and execution options. |
| `patched` | Table | Optional for service problems | Compose override and functional check; file problems omit it. |

### `content`

| Field | Type | Required or default | Rule |
| --- | --- | --- | --- |
| `description` | String | Required | Path to the player brief. |
| `hints` | Array of strings | Defaults to `[]` | Up to 10 Markdown paths, ordered from general direction to concrete clues. |
| `walkthrough` | String | Required | Path to a complete player-facing explanation. |

Every document is a distinct existing regular `.md` file inside this repository, encoded as nonempty UTF-8 and at most 1 MiB. Paths follow the portable repository containment rules. These documents are content resources, independently declared from downloadable `files` and executable `solve.command`. Version 2 introduced the required content declarations. Version 3 retains their format and adds the common network isolation and ingress rules below.

The description provides the scenario, objective, supplied information, starting actions, expected result and submission format. It names the website's actual controls and gives enough context for a player to start without reading repository documentation. The authoring standard and review checklist are in [player content](player-content.md).

Consumers render the brief in the workspace, expose hints separately in declaration order and expose the walkthrough with an explicit answer-spoiler label. Hint and walkthrough bodies are requested after player activation; they are absent from the default detail payload. A walkthrough explains the reasoning, reproducible steps, result and takeaway. For generated flags it explains how to obtain the current instance's answer. Players read it in the website.

This presentation controls accidental spoilers. The local checkout and toolbox are available to the player, so it is not an answer confidentiality boundary. Author validation and automated verification commands belong in maintainer documentation. Commands in player content run in the website's prepared terminal and directly serve the exercise.

### `flag`

| Field | Type | Required or default | Rule |
| --- | --- | --- | --- |
| `mode` | String | Required | `"sha256"` for file problems; `"generated"` for service problems. |
| `sha256` | String | Required for file problems | Exactly 64 hexadecimal digits, case-insensitive. Service problems omit it or use `""`. |

### `solve`

| Field | Type | Required or default | Rule |
| --- | --- | --- | --- |
| `image` | String | Required | Nonempty Docker image reference, without leading/trailing whitespace or a leading `-`. |
| `command` | Array of strings | Required | At least one nonempty argument, executed directly in the image. |
| `network` | String | Defaults to `contract.toml`'s `solve_network` | Nonempty Compose network key. Service configurations must define it; file toolboxes use networking mode `none`. |
| `timeout_seconds` | Integer | Defaults to `contract.toml`'s `solve_timeout_seconds` | Positive runtime limit for each toolbox command, after image preparation. |
| `writable` | Boolean | Defaults to `false` | Gives the toolbox write access to its problem directory when `true`. |

### Each `endpoints` entry

| Field | Type | Required or default | Rule |
| --- | --- | --- | --- |
| `name` | String | Required | Nonempty and unique within this problem's endpoint list. |
| `service` | String | Required | Nonempty service name present in the resolved Compose configuration. |
| `port` | Integer | Required | Container port in the range 1–65535. |
| `protocol` | String | Required | `"http"` or `"tcp"`; describes a TCP entry point. |

### `patched`

| Field | Type | Required or default | Rule |
| --- | --- | --- | --- |
| `compose` | String | Required | Existing regular Compose override file, combined with the vulnerable Compose file. |
| `check` | Array of strings | Required | At least one nonempty argument for the patched functional check. |
| `image` | String | Defaults to `solve.image` | A nonempty value follows the same image rules as `solve.image`; an explicit `""` also inherits `solve.image`. |

The patch attack uses the original `solve.image` and `solve.command`. Both patched commands use the solution's network, timeout, and mount permissions.

## File problem execution

```toml
schema = 3
slug = "example-file"
title = "Example file"
category = "rev"
files = ["files/example.bin"]

[content]
description = "README.md"
hints = ["hints/1.md"]
walkthrough = "solve/README.md"

[flag]
mode = "sha256"
sha256 = "<64 hex digits: SHA-256 of the solution's trimmed stdout>"

[solve]
image = "python:3.13.15-slim"
command = ["python3", "solve/solve.py"]
timeout_seconds = 60
```

The runner mounts the challenge directory at `/challenge` and runs the solution there. The mount is read-only by default. `verify` hashes the trimmed solution output and compares it with `flag.sha256`. A file problem omits `compose` or uses `""`, has no endpoint entries, and omits `patched`. `run` reports the available files; `verify` can run without `run`.

`solve.timeout_seconds` uses the timeout declared in `contract.toml` when omitted and applies after the toolbox image is available. Downloading a missing image uses the consumer's overall deadline, so a cold image cache does not consume the solution's execution time. File toolboxes have networking mode `none`.

## Service problem execution

```toml
schema = 3
slug = "example-service"
title = "Example service"
category = "web"
compose = "compose.yaml"

[content]
description = "README.md"
walkthrough = "solve/README.md"

[flag]
mode = "generated"

[[endpoints]]
name = "web"
service = "app"
port = 8000
protocol = "http"

[solve]
image = "python:3.13.15-slim"
command = ["python3", "solve/solve.py"]
network = "default"
timeout_seconds = 60

[patched]
compose = "compose.patched.yaml"
check = ["python3", "patched/test.py"]
```

`compose` can define any positive number of services. `endpoints` documents entry points; each service must exist in the resolved Compose configuration. `protocol` is `http` or `tcp`. The solution runs on the named Compose network and can reach services by their Compose service names. `network` defaults to `default`; set it when the solution should join a custom network. Give target services health checks if the solution needs readiness: `run` uses `docker compose up --wait`.

Declare HTTP endpoints in the manifest. The platform provides browser access on a separate loopback origin through a fixed-destination Docker exec byte stream into the problem's isolated network. The platform removes service `ports` from the effective execution configuration; authors need no host port mapping or ingress implementation. The local server owns these origins for the running environment's lifetime. Standalone CLI `run` reports private service addresses; TCP endpoints are reached by service name from the problem terminal. Host port numbers are outside the challenge contract.

At each `run`, the runner generates a new `pwnden{...}` flag and passes it to Compose as the `FLAG` environment variable. The Compose file injects `${FLAG}` into the intended service. The solution prints exactly that flag to stdout. `verify` checks the vulnerable run first. When `[patched]` exists, the runner starts a separate Compose project with the override, checks that the same solution no longer returns the flag, runs `patched.check`, and removes the patched project. `patched.image` can override the toolbox image for the functional check. `stop` removes the running vulnerable project and its saved flag.

## Solution and patch results

Solutions print exactly one flag to stdout and send diagnostics to stderr. The consumer removes leading and trailing Unicode whitespace before comparing stdout. For file problems, it hashes the UTF-8 bytes of the remaining string with SHA-256. For service problems, it compares the entire remaining string with the current run's generated flag. A successful solution exits 0; a mismatched flag or nonzero exit fails verification.

The patched attack succeeds as a verification step only when trimmed stdout differs from the current flag and the command either exits 0 or completes with the expected denial code from `contract.toml` (version 3: **3**). Reserve that denial code for a confirmed denial, such as the expected access-control response. Connection errors, timeouts, parsing failures, and other unexpected errors fail verification. Returning the current flag as trimmed stdout always fails the patch check, regardless of exit code. Docker launch failures, cancellation, and signal exits are execution failures, even if no flag was printed. Codes 125 and above cannot express expected denial. The functional check must exit 0; its stdout does not participate in flag comparison.

| Verification step | Required result |
| --- | --- |
| File solution | Exit 0 and trimmed stdout matches the declared SHA-256 digest. |
| Vulnerable service solution | Exit 0 and trimmed stdout equals the current run flag. |
| Patched attack | Trimmed stdout differs from the current flag, and exit is 0 or the declared denial code. |
| Patched functional check | Exit 0. |

A patch is verified only when the vulnerable solution, patched attack, functional check, and patched resource cleanup all succeed. Problems without `patched` verify only their solution.

## Files and resource boundaries

- `files` lists distribution files or directories relative to the challenge directory. Paths may refer to shared content inside the challenges repository.
- `compose` and `patched.compose` are relative to the challenge directory and stay inside the repository.
- Paths use portable relative syntax with `/` separators; absolute paths, backslashes, and colons are invalid in declared problem paths. Resolved bind mount sources, build contexts, and Dockerfiles stay inside the challenges repository. The runner rejects outside paths, including paths reached through symlinks. A bind source must exist before `run`.
- Docker-managed named volumes and bridge networks are scoped to the challenge project. External or explicitly shared volumes and networks, custom volume `driver_opts`, extra build contexts, and host privilege settings are outside format v3.
- File-backed Compose configs and secrets must use files inside this repository. `volumes_from` is unsupported because it can inherit mounts from another container.
- Local build cache imports (`cache_from` with `type=local,src=...`) and exports (`cache_to` with `type=local,dest=...`) stay inside the repository. Relative cache paths resolve from the problem directory. Cache directories may be created during a build; their existing ancestors and symlinks must resolve inside the repository.
- The toolbox mounts the challenge directory read-only. Set `solve.writable = true` when the solution must write there. When the host supplies numeric effective user and group IDs, the writable toolbox uses those IDs so files follow the caller's permissions and ownership. Ordinary filesystem permissions still apply. Its container filesystem also provides temporary writable space.
- `solve.command` and `patched.check` are argument arrays executed directly in the toolbox image. Use `sh -c` explicitly if a shell is needed.

The consumer validates resolved Compose configuration before creating resources, for both the vulnerable and patched projects. Supported service mounts are repository-contained binds, Docker volumes, and `tmpfs`. Services use Compose networks or `network_mode: none`. Services cannot request `privileged`, automatic engine socket and credential access through `use_api_socket`, devices, added capabilities, host PID/IPC, host providers, credential specifications, or inherited volumes through `volumes_from`. Builds cannot request SSH access, extra build contexts, privilege, or entitlements. All services, toolboxes and ingress connectors drop all capabilities and enable `no-new-privileges`. The toolbox mounts the problem directory at `/challenge`, which is also its working directory.

Compose and toolbox containers receive repository files only through the permitted mounts. The generated flag and run state live in the consumer's local user cache, which is never mounted into a problem container. Repository containment checks prevent accidental access through host mounts outside the allowed checkout.

### Network isolation

Version 3 requires Docker Engine 28 or newer. The platform resolves the author's complete Compose configuration and starts it with every bridge network set to `internal: true` and both IPv4 and IPv6 gateway modes set to `isolated`. These are the only accepted network driver options. It checks the live Docker networks before exposing endpoints or attaching toolboxes. Existing environments with a different network policy require stop and restart.

Problem services and their tools can communicate inside their own declared networks. Outbound access to the Internet, host services and other problem networks is blocked. File toolboxes use network mode `none`. Browser ingress uses a platform-owned, non-root, read-only connector on the isolated problem network with no host mounts, Docker socket or published ports. The platform chooses a declared service and port for each connection; the problem cannot select a host destination through this stream. The connector is removed with its problem project.

Image downloads and builds are preparation operations performed by the consumer. Runtime containers retain the isolation policy after preparation. Docker remains the execution trust boundary; kernel or daemon exploits are outside the ordinary command and network isolation checks.

Package and image versions in a problem should be pinned by its author. Problem source and Compose configuration should use portable paths and container tools so consumers can use the same declarations across operating systems.

## Lifecycle and cleanup

`run` for a file problem reports its distribution files and creates no service project. `verify` can execute its solution without a prior `run`, and `stop` has no service resources to remove.

`run` for a service problem creates a project scoped to the repository and problem, generates a fresh flag, starts services, waits for Compose readiness, and saves the current run state. Starting an already recorded run fails and requires `stop` first. Service verification requires that saved state and leaves the vulnerable project running for further use. Patch verification creates a separate project using the same flag and attempts its cleanup on completion, failure, or cancellation.

Failed startup attempts clean up their project, and failed or interrupted toolbox execution attempts remove its toolbox container. A cleanup failure is reported with the resource identity and prevents the operation from reporting success. Cancellation does not cancel the cleanup attempt.

Problem metadata is read by `validate`, `run`, `verify`, and `stop`; editing metadata or moving the checkout while a problem runs is unsupported. Cleanup requires readable contract and Compose declarations.

`stop` checks project-scoped networks and volumes and rejects host providers before removal. Deleted distribution files, bind sources, or build inputs do not prevent cleanup. It attempts both patched and vulnerable project cleanup and retains the run state if either cleanup fails. Cleanup errors identify the project or toolbox that needs attention.

Successful `stop` removes the problem projects' containers, networks, and volumes and deletes the saved run state. Image caches and repository files, including files created by a writable solution, remain available.
