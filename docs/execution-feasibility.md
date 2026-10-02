# Learning topics and execution feasibility

## What this assessment establishes

The [learning map](learning-map.md) describes teaching scope. The current
[contract](contract.md) supplies file artifacts and ordinary container services,
with declared HTTP/TCP endpoints and web, files and terminal tools. These are
independent classifications: a learning area does not enable a runtime feature.

This assessment compares each topic's entry design with the current contract
and execution implementations. It is a design assessment, not an execution test
of 50 targets. The published examples use IDs `note-vault` and `rotor-lock`. Each new
problem still needs its own target/tool verification and learner review.

Use these statuses to decide what work must precede publication:

| Status | Meaning |
| --- | --- |
| `contract-fit` | The entry can be represented by the current file or user-space service contract. Package and verify its target and tools before publication; a browser tool mentioned in the learning map may still need implementation. |
| `artifact-scope` | The supported entry uses supplied evidence, configuration or packaged data. It teaches analysis of that evidence; live device/provider behavior needs separate support and proof. |
| `runtime-gate` | The intended entry depends on an unverified specialized execution or observation profile. Establish actual behavior under the existing policy before promising it as a playable problem. |

`outside-policy` applies to variants whose target requires prohibited access.
Keep those variants out of the current playable catalog. An evidence exercise
or labelled simulation has its own objective and cannot count as successful
verification of the unavailable original exercise.

## Current boundaries and evidence

The current runtime policy requires:

- All problem runtime services and tools communicate inside their own isolated
  networks. File toolboxes have networking mode `none`.
- Runtime containers have no Internet route, access to host services or access
  to another problem's network. Image/build preparation is a separate operation.
- Host bind mounts and build inputs resolve inside the challenges repository.
  The local user cache, host credentials and platform state are not mounted.
- Services, command toolboxes, terminal containers and ingress drop all
  capabilities and enable `no-new-privileges`.
- Added capabilities, devices, privileged services, host network/PID/IPC,
  inherited mounts, host providers and Docker socket integration through
  `use_api_socket` are rejected. Host Docker sockets outside the repository also
  fail mount containment. A problem's target is never the host Docker daemon.
- Services declare HTTP or TCP entry points. Internal ordinary UDP sockets
  are possible within the problem network; there is no declared host/browser
  UDP ingress. Raw packets and network administration require permissions the
  current policy does not grant.

Author verification applies these boundaries in
[`tools/runtime.py`](../tools/runtime.py) and checks live networks before each
solution. The standalone [isolation check](verification.md#actual-network-isolation)
uses reachable host/peer controls. Target, solution, patch and cleanup evidence
belongs to the challenges authoring workflow.

Consumer integration evidence additionally comes from the platform's
[network policy](https://github.com/pwnden/platform/blob/main/docs/network-isolation.md),
[`checkConfig` and command toolbox](https://github.com/pwnden/platform/blob/main/internal/runtime/runtime.go),
[`isolatedConfig`](https://github.com/pwnden/platform/blob/main/internal/runtime/isolation.go)
and [terminal configuration](https://github.com/pwnden/platform/blob/main/internal/runtime/terminal.go).
Existing boundary and isolation tests cover accepted/rejected configurations;
the [actual isolation check](https://github.com/pwnden/platform/blob/main/docs/verification.md#actual-network-isolation)
covers external, host and other-network denial against reachable controls,
same-problem communication, `note-vault` solving, patch checks and cleanup.

Those checks establish a shared boundary on the verified Linux/WSL execution
target. They do not establish every tool's compatibility or every target's
resource and architecture requirements. Windows/macOS execution remains a
later check; new authoring must avoid depending on host paths, host packages or
host devices. Native targets need declared architecture/tool profiles and
verification on the intended container architectures.

## Area coverage

| Learning area | Entry scope supported by the contract | Material limit |
| --- | --- | --- |
| Web security | Real local sites, API requests and internal service combinations. | Request editing and viewer bots need prepared tooling; real external services stay outside runtime scope. |
| System security | User-space target programs and application sandboxes. | Debuggers and kernel guests are unverified profiles. Host kernel or Docker escape targets are outside policy. |
| Reverse engineering | Real distributed files and prepared checkers. | Actual dynamic tracing and architecture-specific execution need profile verification. |
| Cryptographic security | Real local cryptographic operations, verifiers and supplied artifacts. | Prepare operations and local dependencies; scope mathematics to the objective. |
| Digital forensics | Authored captures, logs, memory snapshots and disk images. | Offline parsers/extractors need prepared tooling; live host acquisition and privileged mounts are outside policy. |
| Network security | Local TCP/protocol targets and recorded traffic. | Live wireless, raw packet injection, host routing and device access are outside policy. |
| Cloud and infrastructure security | Configuration evidence and real local storage implementations. | A local policy model is labelled by its semantics. Real cloud accounts are outside runtime scope; a control plane is unverified. |
| Mobile security | Package/data artifacts and real local mobile backends. | Emulator/app execution and instrumentation are unverified; physical device integration is outside policy. |
| Hardware and embedded security | Firmware artifacts, local protocol implementations and measured trace files. | Emulation needs an explicit model and verification. Physical measurement, fault injection and device access are outside policy. |
| Software supply-chain security | Local history, unprivileged builds and provenance verification. | Supply dependencies locally. Live registries, host CI credentials and privileged nested builders are outside scope. |
| AI security | Local retrieval authorization and model artifacts. | Actual model decisions and inference need an offline CPU/resource profile. GPU access and external model APIs are outside policy. |
| Blockchain security | Real local-chain targets can use the ordinary service shape. | Chain execution, prepared actors, traces and deterministic ordering need profile verification; public networks and funds are outside scope. |

## Topic assessment

Each row refers to the corresponding five-field entry in the learning map.
The status concerns that entry's stated objective. Later variants can have
different requirements and must be reassessed.

The current assessment has 30 `contract-fit` entries, 10 `artifact-scope`
entries and 10 `runtime-gate` entries. These counts describe designs and scope,
not 50 runnable implementations. Outside-policy variants are listed separately
within their topic and area boundaries.

| Topic | Status | Required preparation or boundary |
| --- | --- | --- |
| `web-information-disclosure` | `contract-fit` | Local site and actual deployment artifact; prepared header inspection for later variants. |
| `web-authentication-sessions` | `contract-fit` | Session-aware request replay; keep target cookies separate from platform authentication. |
| `web-access-control` | `contract-fit` | The `note-vault` scenario is the existing path-based example; method/body variants need prepared request editing. |
| `web-injection` | `contract-fit` | Real local interpreter and dependencies, annotated query observation and prepared request controls. |
| `web-browser-security` | `contract-fit` | Actual browser origin/execution; prepare local viewer-account bots for stored-content variants. |
| `web-business-logic` | `contract-fit` | Real local state and observable changes; coordinated race variants need deterministic tooling. |
| `web-servers-proxies` | `contract-fit` | Actual internal proxy/fetch/cache services; raw HTTP message controls need prepared tools. |
| `pwn-memory-boundaries` | `contract-fit` | Real native target and observable adjacent state. A debugger-based path needs the debugger gate below. |
| `pwn-integers-sizes` | `contract-fit` | Real fixed-width arithmetic and target effects; explicit architecture and boundary values. |
| `pwn-control-flow` | `runtime-gate` | Verify the target, debugger/disassembler and address behavior used by the intended path. |
| `pwn-heap-lifetime` | `runtime-gate` | Verify actual allocator reuse and heap observations on the exact runtime profile. |
| `pwn-mitigations` | `runtime-gate` | Verify paired builds and tracing; existing process restrictions can affect observations and address randomization controls. |
| `pwn-kernel-boundaries` | `runtime-gate` | No prepared guest execution profile exists. Host kernel testing and host device/KVM access are outside policy. |
| `system-application-sandboxes` | `contract-fit` | Actual restricted user-space application within the enclosing problem container. |
| `rev-static-analysis` | `contract-fit` | Actual artifact and prepared strings/disassembly tools; introduce the exact instruction vocabulary. |
| `rev-dynamic-analysis` | `runtime-gate` | Actual stepping, process tracing and required architecture must work under current process restrictions. |
| `rev-input-checks` | `contract-fit` | Actual checker plus prepared operations; the `rotor-lock` scenario exists but needs learner-path reassessment. |
| `rev-data-formats` | `contract-fit` | Real artifact and prepared hex/edit operations; declare writable copies when necessary. |
| `rev-obfuscation` | `contract-fit` | Static transformed-constant entry with real artifact. Dynamic and anti-debug variants require a tracing profile. |
| `crypto-representation-protection` | `contract-fit` | Prepared representation operations with actual exposed data. |
| `crypto-key-management` | `contract-fit` | Real artifacts and cryptographic operations; relevant local keys supplied by the lab. |
| `crypto-modes-nonces` | `contract-fit` | Actual selected cryptographic implementation and byte comparison tools. |
| `crypto-hashes-authentication` | `contract-fit` | Real local verifier, scoped digest/MAC operations and stated authority model. |
| `crypto-public-keys-signatures` | `contract-fit` | Real verification decision and local keys; advanced arithmetic requires separate preparation. |
| `forensics-files-metadata` | `contract-fit` | Prepared format identification and extraction that operates on files. |
| `forensics-network-evidence` | `artifact-scope` | Actual supplied capture and offline reconstruction tools. This does not provide live host packet acquisition. |
| `forensics-event-reconstruction` | `contract-fit` | Supplied logs with explicit timestamps and evidence-backed solution. |
| `forensics-memory-evidence` | `artifact-scope` | Real dump, compatible offline parser and measured memory/resource cost. |
| `forensics-storage-recovery` | `artifact-scope` | Actual image and userspace extraction; loop devices or privileged filesystem mounts are outside policy. |
| `network-protocol-state` | `contract-fit` | Actual TCP target and prepared sender; internal UDP can use ordinary sockets. |
| `network-service-trust` | `contract-fit` | Real local service and supplied identity-field experiment; packet interception/routing variants exceed this entry scope. |
| `network-wireless-evidence` | `artifact-scope` | Real recorded exchange and offline analysis. Live radio operations are outside policy. |
| `cloud-identity-policies` | `artifact-scope` | Supplied policies and explicitly scoped evaluator; provider behavior claims need independent semantic evidence. |
| `cloud-storage-exposure` | `contract-fit` | Real local storage service running without extra privilege; scope claims to that implementation. |
| `cloud-orchestration-boundaries` | `artifact-scope` | Configuration/policy analysis entry. Actual control-plane execution is `runtime-gate`; host cluster access is outside policy. |
| `mobile-local-data` | `artifact-scope` | Actual app/data artifact and offline archive/database tools. |
| `mobile-backend-trust` | `contract-fit` | Real local backend and prepared request client; actual app behavior is a separate runtime question. |
| `mobile-runtime-integrity` | `runtime-gate` | No prepared emulator display/app-control/instrumentation profile exists. Physical-device and accelerated-device access are outside policy. |
| `hardware-firmware-artifacts` | `artifact-scope` | Actual firmware and userspace extraction tools; static evidence supports only the stated artifact claims. |
| `hardware-device-protocols` | `contract-fit` | Actual local protocol implementation with a stated device model; physical device fidelity needs separate evidence. |
| `hardware-physical-evidence` | `artifact-scope` | Supplied measured traces and prepared analysis. Live measurement and physical fault injection are outside policy. |
| `supply-chain-history` | `contract-fit` | Prepared local repository/history; no host credentials or external repository runtime access. |
| `supply-chain-builds` | `contract-fit` | Offline dependency fixtures, ordinary unprivileged compiler/build commands and observable artifact changes. |
| `supply-chain-provenance` | `contract-fit` | Actual artifacts, attestation format, verifier and local trust material. |
| `ai-instruction-boundaries` | `runtime-gate` | Verify an actual offline model/agent and resource profile. A deterministic fixture cannot prove model behavior. |
| `ai-retrieval-access` | `contract-fit` | Real local retrieval permission checks and request tools; inference is unnecessary for this scoped objective. |
| `ai-model-artifacts` | `artifact-scope` | Actual model package inspection; unsafe-loading/inference variants require loader/runtime verification. |
| `blockchain-caller-authority` | `runtime-gate` | Prepare and verify real local chain execution, lab identities and call controls. |
| `blockchain-state-reentrancy` | `runtime-gate` | Actual local VM execution, prepared actors and state/call trace controls. |
| `blockchain-transaction-ordering` | `runtime-gate` | Actual local chain with deterministic transaction/block controls and internal data sources. |

## Verify a new execution profile before selecting it

1. State the exact objective and whether the experiment uses a real target,
   supplied evidence or an explicitly labelled model. Record learning area,
   topic, current category and evidence scope in `AUTHORING.md`.
2. Package dependencies and tools in the selected image or authored local
   services. Confirm the intended player actions are exposed by the site and
   prepared terminal; installation by the player is not a solving prerequisite.
3. Validate the resolved vulnerable and patched configurations with the existing
   policy. Specialized runtimes must work without widening host, device,
   capability or external-network access.
4. Execute the actual intended path and author solution. Check real observations,
   flag comparison, optional patch behavior, timeouts and cleanup. Measure cold
   preparation time, CPU, RAM and image/artifact storage. Record image versions,
   architecture, engine/runtime details and result.
5. For new runtimes, check same-problem communication and denied external/host/
   other-problem access using reachable positive controls. Verify repository
   containment and cleanup after failure. Linux/WSL results establish that
   target only; Windows/macOS checks remain a later publication compatibility gate.
6. Run a learner review for the intended audience. Execution evidence and
   learning/difficulty evidence answer separate questions.

If a required operation fails, identify that requirement and leave the profile
unverified or outside policy. Do not relax isolation or change the exercise into
a simulation while claiming the original target now works.

## External mechanism references

The support judgments above are inferred from pwnden's execution implementations, not from
general Docker feature availability. Check the exact host/runtime profile:

- Docker's [isolated gateway mode](https://docs.docker.com/engine/network/port-publishing/#gateway-modes)
  removes the internal bridge's gateway address; the platform applies and inspects it.
- Docker's [seccomp profile](https://docs.docker.com/engine/security/seccomp/)
  restricts process, mount and kernel operations. Debugger compatibility depends
  on the particular operation and security profile; it is not established merely
  by installing GDB.
- Android's [emulator acceleration documentation](https://developer.android.com/studio/run/emulator-acceleration)
  describes host-specific graphics/VM acceleration. No such device access is
  part of pwnden's current container contract, and no unaccelerated emulator
  profile has been verified here.
