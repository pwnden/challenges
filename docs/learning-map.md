# Security learning map

## Use this map when designing a problem

This map organizes 12 learning areas and 50 topics by the security behavior a player
will observe. Choose a primary area and topic, identify the concepts taught and
required, then design the exercise using the [authoring standard](authoring-standard.md).
Record the choices and evidence in the problem's `AUTHORING.md`.

Each topic below specifies a learning principle, a concrete experiment, scoped
prerequisites, an entry exercise and progression, and the tools it needs.
Entry exercises are design patterns, not published problems or promises of
Intro difficulty. Advanced topics have advanced prerequisites. Assess the
actual workload and learner evidence for each authored problem.

Learning area IDs and topic keys identify authoring choices independently of
the manifest's `category`. Contract v5 accepts six `category` values and has no
learning-area, topic or concept-reference field. Record the learning area and
topic in `AUTHORING.md` today. Structured catalog declarations and graph
presentation require their own contract and platform work.

## Learning areas

This is the current authoring coverage, which can grow as learning objectives
are added. It is not a claim to enumerate all of security. Choose a learning
area by the primary objective, independently of the target's implementation
language, artifact format or execution form.

| Learning area | Area ID | Topics |
| --- | --- | --- |
| [Web security](#web-security) | `web-security` | Information disclosure; authentication and sessions; access control; injection; browser security; business logic; servers and proxies. |
| [System security](#system-security) | `system-security` | Memory boundaries; integers and sizes; control flow; heap and lifetime; mitigations; kernel boundaries; application sandboxes. |
| [Reverse engineering](#reverse-engineering) | `reverse-engineering` | Static analysis; dynamic analysis; input checks; data formats; obfuscation. |
| [Cryptographic security](#cryptographic-security) | `cryptographic-security` | Representation and protection; key management; modes and nonces; hashes and message authentication; public keys and signatures. |
| [Digital forensics](#digital-forensics) | `digital-forensics` | Files and metadata; network evidence; event reconstruction; memory evidence; storage recovery. |
| [Network security](#network-security) | `network-security` | Protocol state; service trust; wireless evidence. |
| [Cloud and infrastructure security](#cloud-and-infrastructure-security) | `cloud-infrastructure-security` | Identity policies; storage exposure; orchestration boundaries. |
| [Mobile security](#mobile-security) | `mobile-security` | Local data; backend trust; runtime integrity. |
| [Hardware and embedded security](#hardware-and-embedded-security) | `hardware-embedded-security` | Firmware artifacts; device protocols; physical measurement evidence. |
| [Software supply-chain security](#software-supply-chain-security) | `software-supply-chain-security` | Repository history; dependencies and builds; artifact provenance. |
| [AI security](#ai-security) | `ai-security` | Instruction boundaries; retrieval access; model artifacts. |
| [Blockchain security](#blockchain-security) | `blockchain-security` | Caller authority; state and reentrancy; transaction ordering. |

Areas and topics support navigation. Concepts can be shared across topics;
prerequisite relationships establish learning order, and difficulty describes
the complete solving workload. Supporting concepts may come from other areas.
For example, inspecting an APK can teach mobile local-data protection, reverse
engineering or forensics. Choose the primary objective and record the supporting
concepts rather than assigning the learning area solely from the file extension.

### Mapping to the current contract

`category` is a compatibility classification consumed by the current catalog;
it does not select file/service execution or change isolation. Keep the learning
area and topic explicit in the author record. Select one supported category for
the actual exercise using the following guidance; new learning areas do not add
manifest enum values.

| Primary exercise objective | Current category |
| --- | --- |
| Web behavior and web/API authorization | `web` |
| User-space memory exploitation | `pwn` |
| Reconstructing program or firmware behavior | `rev` |
| Cryptographic construction or key handling | `crypto` |
| Reconstructing evidence from supplied artifacts | `forensics` |
| Other objectives, including application sandbox, build provenance or chain state rules | `misc` |

A mobile backend authorization exercise can therefore use learning area
`mobile-security`, topic `mobile-backend-trust`, and category `web`. An AI
retrieval-permission exercise uses `ai-security` and `ai-retrieval-access` with
`web` when the primary exercise is API authorization, or `misc` for an agent
workflow. Record the choice's reason. Learning-area presentation is future
platform work; current catalog filters still use `category`.

Check the [execution feasibility map](execution-feasibility.md) before selecting
an experiment. Inclusion in a learning area does not establish that its real
target, tools or privileged variants can run on the current platform.

## Shared foundations

The keys below refer to prerequisite abilities, not existing concept pages.
Supply the needed explanation or prepared practice before the problem step
that uses it. Each topic lists the abilities required for its entry exercise;
extend that list when authoring a more demanding variant.

| Key | Required ability | Prepared practice |
| --- | --- | --- |
| `web-addresses` | Identify the path, resource identifier and query in a URL. | Change one path or query value and compare the resulting page. |
| `http-messages` | Distinguish method, path, headers, body, response status and response content. | Inspect an annotated normal exchange and change one request value. |
| `sessions` | Recognize the identity carried between requests and the effect of login and logout. | Compare requests in logged-in and logged-out states. |
| `browser-origins` | Distinguish document origins and understand which browser context performs an action. | Compare same-origin and cross-origin reads and record allowed behavior. |
| `data-representation` | Read bytes in text, hex and bits; follow the specific encoding or bit operation being used. | Compare the same small value in different representations using prepared controls. |
| `files-processes` | Distinguish files, executable programs, running processes and their inputs and outputs. | Inspect a supplied file and run a supplied program with one input. |
| `memory-layout` | Interpret a small address range, buffer length and adjacent storage. | Follow a labelled memory view while changing input length. |
| `integer-representation` | Understand the stated integer width, signedness and representable range. | Compare ordinary and boundary values in a prepared range example. |
| `execution-tracing` | Follow a condition, branch, call and the state before and after one step. | Trace a short annotated sequence with supplied breakpoint or stepping commands. |
| `data-querying` | Understand the records, filter and literal values used by a small query. | Compare an annotated intended query with its evaluated result. |
| `state-ordering` | Follow state changes, invariants and the order of dependent actions. | Repeat or reorder two actions and compare their state changes. |
| `crypto-primitives` | Distinguish encoding, encryption, keys, hashes, message authentication and signatures at the scope used by the exercise. | Compare confidentiality and tamper detection using prepared inputs and operations. |

A shared ability is introduced where needed. It does not create a requirement
to finish an entire programming, networking or mathematics course. Python is
primarily used by authors and verification scripts. Prepared tools let players
concentrate on the security observation. Where code or assembly comprehension
is essential, record the exact required ability and supporting explanation.

## Tools and delivery status

Use these names below to identify a capability, independently of its final UI
implementation. Every future capability is a publication prerequisite for
exercises that need it. Tool versions and integration are selected and verified
when that capability is implemented.

| Capability | Current state and author responsibility |
| --- | --- |
| Browser | Available: local target browsing, navigation and address editing. Browser history belongs to the common platform tool. |
| Text/source preview | Available: declared text files and syntax highlighting. Binary inspection needs another capability. |
| Terminal | Available: Bash over a PTY. Declare terminal only when needed. Package specific commands in the toolbox image before publication; players use the prepared environment. |
| Request inspector/editor | Planned common capability: inspect, edit and repeat HTTP exchanges, including headers, cookies and bodies. Ordinary address editing does not cover all of these operations. |
| Hex/metadata view | Planned common capability: display offsets and bytes or structured metadata for declared files. Prepared container commands can provide these observations when documented and installed. |
| Transform workbench | Planned common capability or prepared command set: convert representations, apply scoped byte operations and compare cryptographic outputs. It supplies operations while the player chooses an approach. |
| Debugger/disassembler | Requires a prepared and verified toolbox profile or common analysis view. Annotate the commands and instruction set needed; verify the actual process under the execution policy. |
| Evidence viewers | Require prepared tooling for packet captures, timelines, memory dumps or disk images. Deliver only the capabilities needed by the particular artifact. |
| Specialized runtimes | Require authored, verified local bot, proxy, kernel guest, agent or chain services. The common platform supplies lifecycle and declared endpoint access. |

Provide a common platform capability once and consume it through problem
declarations. Exercise-specific target interfaces may expose the target's own
behavior. Visual examples should identify their model, and views claiming to
show actual execution must derive their observations from that execution.

All authored experiments keep targets and dependencies inside the isolated
problem environment, with host paths inside the allowed repository root.
Services that model another machine, account or origin are local lab components.
They use the current [execution and network contract](contract.md).

## Web security

### web-information-disclosure

- **Principle:** Public resources can disclose information intended to be private.
- **Experiment:** Inspect an ordinary page and a supplied deployment artifact; identify the exposed secret and explain why it is accessible.
- **Prerequisites:** `web-addresses`, the relevant file role from `files-processes`.
- **Entry and progression:** A forgotten backup or debug resource; then response metadata, repository history or inconsistent deployment exposure.
- **Tools:** Browser and text/source preview. A request inspector supports later response-header variants.

### web-authentication-sessions

- **Principle:** Authentication establishes identity, and session handling must maintain that identity correctly through its lifecycle.
- **Experiment:** Compare protected requests before login, after login and after logout; test whether a previously issued credential still grants access.
- **Prerequisites:** `http-messages`, `sessions`.
- **Entry and progression:** Logout leaves a session usable; then session fixation, recovery flows and token validation.
- **Tools:** Browser and request inspector/editor with controlled session selection. Cookies belonging to the lab target remain separate from the player platform session.

### web-access-control

- **Principle:** Each resource or action must enforce the current identity's permitted access.
- **Experiment:** Compare access to an owned object and another object's identifier; observe whether individual requests enforce the stated permission.
- **Prerequisites:** `web-addresses`, `sessions`; the distinction between identity and permission is introduced with the exercise.
- **Entry and progression:** Note Vault's object ownership check; then role-restricted actions, nested resources and multiple access paths.
- **Tools:** Browser for path-based exercises; request inspector/editor for API, method or body variants.

### web-injection

- **Principle:** Untrusted input can change instructions when a downstream interpreter treats it as executable structure.
- **Experiment:** Compare the intended query and evaluated behavior when changing one input; connect the resulting access change to the interpreter boundary.
- **Prerequisites:** `http-messages`, `data-querying` for the first SQL exercise. Introduce the particular interpreter before each later variant.
- **Entry and progression:** A small login query with visible record filtering; then extraction, shell or template interpretation, and XML entities as separately taught branches.
- **Tools:** Browser and request inspector/editor; prepared query inspection for the entry exercise. Each interpreter runs in the authored local target.

### web-browser-security

- **Principle:** Browser execution, document origins and request authority determine which content can act with a user's privileges.
- **Experiment:** Submit marked untrusted content and observe it acting in a document; compare the result against an escaped version and identify the acting origin.
- **Prerequisites:** `http-messages`, `browser-origins`, `sessions`; supply the small markup or script example used by the first experiment.
- **Entry and progression:** Reflected content executes a harmless visible action; then DOM behavior, stored content with a local viewer account, CSRF, CORS and framing as separate branches.
- **Tools:** Browser and request inspector/editor. Multi-origin and viewer-account exercises require real local origins or a prepared browser bot.

### web-business-logic

- **Principle:** A server must preserve the application's stated rules across inputs, steps and repeated actions.
- **Experiment:** Record a normal purchase or coupon flow, vary one quantity or repeat an action, and compare balances and allowed state transitions.
- **Prerequisites:** `state-ordering`, form input and ordinary arithmetic explained in the brief; `http-messages` when requests are edited.
- **Entry and progression:** A quantity violates the documented pricing rule; then reused discounts, skipped workflow steps and controlled concurrent actions.
- **Tools:** Browser; request inspector/editor for replay and ordering. Race variants need reproducible target coordination.

### web-servers-proxies

- **Principle:** Components can interpret addresses, request boundaries or cache identity differently across a trust boundary.
- **Experiment:** Compare the request each local component receives and the response it selects; identify a mismatch that exposes a lab resource.
- **Prerequisites:** `http-messages`, `web-addresses`, `state-ordering`; introduce the specific proxy, cache or server-fetch behavior.
- **Entry and progression:** Server-side fetching reaches a local private service; then host handling, cache identity and request-boundary disagreement as separate branches.
- **Tools:** Request inspector/editor and declared local proxy, cache or private-service components. Raw protocol variants require a prepared raw-request capability.

## System security

### pwn-memory-boundaries

- **Principle:** A write beyond a buffer's bounds can affect neighboring state.
- **Experiment:** Vary input length, inspect the actual target's adjacent storage and explain which value changed beyond the intended buffer.
- **Prerequisites:** `data-representation`, `memory-layout`, `files-processes`.
- **Entry and progression:** An adjacent permission value changes; then stack and heap layouts, out-of-bounds reads and pointer targets.
- **Tools:** Prepared native target and terminal, debugger or target observation view. The author builds the target; the player needs only the scoped memory operations.

### pwn-integers-sizes

- **Principle:** Integer conversion and arithmetic can disagree with the intended range or size check.
- **Experiment:** Compare values around an annotated numeric boundary and observe the real target's resulting length, allocation or access decision.
- **Prerequisites:** `integer-representation`, `data-representation`; `memory-layout` for memory consequences.
- **Entry and progression:** A size calculation wraps across a boundary; then signedness conversions, truncation and allocation/write mismatches.
- **Tools:** Prepared native target, terminal and a value/state view or debugger. Use explicit widths and reproducible target behavior.

### pwn-control-flow

- **Principle:** Corrupting a control-flow value can redirect execution to an unintended operation.
- **Experiment:** Compare the normal call path and a changed target address; confirm the executed lab function through an observable result.
- **Prerequisites:** `memory-layout`, `execution-tracing`, `data-representation`, and the relevant memory-write mechanism.
- **Entry and progression:** Redirect a writable callback to a supplied target function; then saved return addresses and constructed call sequences.
- **Tools:** Prepared native target, terminal and debugger/disassembler. Supply the relevant calling and address representation, including the target architecture.

### pwn-heap-lifetime

- **Principle:** Access through an expired or incorrectly bounded heap object can affect another object's data or behavior.
- **Experiment:** Allocate, release and reuse small objects in the target; compare object identity and the data reached through a retained reference.
- **Prerequisites:** `memory-layout`, `state-ordering`, `files-processes`; introduce allocation, ownership and release.
- **Entry and progression:** A stale handle accesses a reused object; then neighboring allocations and allocator-specific mechanisms.
- **Tools:** Prepared native target and heap observation commands or debugger. Verify layout and reuse on the exact runtime profile.

### pwn-mitigations

- **Principle:** Exploit mitigations constrain particular attack mechanisms, and their scope differs from fixing the underlying defect.
- **Experiment:** Run the same reproducible defect under paired build profiles; compare address changes, detected corruption or blocked execution.
- **Prerequisites:** `memory-layout`, `execution-tracing`, and a previously understood memory/control-flow exercise.
- **Entry and progression:** Compare one mitigation enabled and disabled; then interacting protections and information disclosure that weakens a particular protection.
- **Tools:** Verified paired target builds and debugger/disassembler. The author documents each profile and the actual evidence for its behavior.

### pwn-kernel-boundaries

- **Principle:** Kernel-facing operations must enforce the privilege and memory boundaries of their callers.
- **Experiment:** In a dedicated lab guest, compare an allowed device operation with one that reaches data outside the caller's permitted range.
- **Prerequisites:** `files-processes`, `memory-layout`, `execution-tracing`, the relevant prior memory topic; introduce guest privilege levels and the device interface.
- **Entry and progression:** One faulty range or permission check in a lab driver; then guest-only memory corruption and privilege-boundary consequences.
- **Tools:** Prepared guest/emulator, target driver and debugger or guest observation tools. All target effects remain in the authored guest; verify real execution and resource cost before publishing.

### system-application-sandboxes

- **Principle:** An application's restrictions must account for the actual interpreter or capability boundary it exposes.
- **Experiment:** Compare an allowed action with another path to the same capability; demonstrate the lab restriction's gap and its scope.
- **Prerequisites:** `files-processes`, `state-ordering`; introduce the precise interpreter behavior or capability used.
- **Entry and progression:** An application command filter overlooks an equivalent lab operation; then parser behavior and language sandboxes as separately scoped branches.
- **Tools:** Prepared restricted target and terminal or target interface. State the application boundary being tested and retain the enclosing problem isolation. Host kernel and Docker escape targets are outside the current execution policy.

## Reverse engineering

### rev-static-analysis

- **Principle:** Distributed program material can expose security decisions, constants or secrets without executing it.
- **Experiment:** Inspect supplied strings, constants and an annotated decision; identify which material reveals the accepted input or protected data.
- **Prerequisites:** `files-processes`, `data-representation`; introduce the specific condition or instruction being examined.
- **Entry and progression:** An embedded constant used by a small check; then references, branching structure and larger compiled programs.
- **Tools:** Text/source preview or prepared strings/disassembly output; debugger/disassembler for later variants. Python syntax is not the default interface.

### rev-dynamic-analysis

- **Principle:** Runtime state can reveal how a security decision depends on supplied input.
- **Experiment:** Pause at a provided observation point, compare two inputs and inspect the value used by the decision.
- **Prerequisites:** `files-processes`, `execution-tracing`; `memory-layout` where addresses are inspected.
- **Entry and progression:** Observe a comparison operand; then calls, generated values and paths that static inspection leaves unresolved.
- **Tools:** Verified debugger profile with supplied stepping and observation commands, or a common view of actual debugger state.

### rev-input-checks

- **Principle:** An exposed input check may retain enough information to reconstruct an accepted input.
- **Experiment:** Compare chosen input/output pairs, identify the sequence of transformations and test a reconstructed input against the actual checker.
- **Prerequisites:** `data-representation`, `execution-tracing`; explain each needed operation with a scoped example.
- **Entry and progression:** A single understandable transformation; then chained stateful checks. Reassess Rotor Lock's presentation and workload within this progression.
- **Tools:** Prepared checker and transform workbench or annotated operation commands. The player selects operations and reasons about the sequence rather than implementing the author's Python routine.

### rev-data-formats

- **Principle:** A program's structured data can disclose relationships and values that are obscured by its binary representation.
- **Experiment:** Match known field values to offsets in a small real artifact; change a copy and observe which target behavior changes.
- **Prerequisites:** `data-representation`, `files-processes`; introduce record length, ordering and the specific fields used.
- **Entry and progression:** A short configuration format with a security-relevant field; then length tables, checksums and multiple record types.
- **Tools:** Hex/metadata view and prepared comparison or editing commands. Declare writable copies when the experiment requires modifications.

### rev-obfuscation

- **Principle:** Obfuscation changes how a security decision is represented while preserving behavior that can be analyzed.
- **Experiment:** Trace annotated transitions or decoded values and connect them to the target's input decision; confirm equivalent behavior.
- **Prerequisites:** `execution-tracing`, `data-representation`, relevant static or dynamic analysis experience.
- **Entry and progression:** Recover one transformed constant or short flattened decision; then protected strings, anti-debugging and custom bytecode as separate branches.
- **Tools:** Prepared static/dynamic analysis and transformation tools. Teach the narrow instruction or operation vocabulary needed for each target.

## Cryptographic security

### crypto-representation-protection

- **Principle:** A publicly reversible representation does not provide secret-key confidentiality.
- **Experiment:** Transform a supplied protected-looking value using the documented representation and explain what allows its contents to be recovered.
- **Prerequisites:** `data-representation`; introduce the difference between representation and protection.
- **Entry and progression:** Encoding used to conceal a credential; then combinations of representations and an explicit comparison with keyed encryption.
- **Tools:** Transform workbench or prepared decoding commands and text preview. The learning objective includes the security consequence of the exposed information.

### crypto-key-management

- **Principle:** A cryptographic operation's security depends on appropriate generation, separation and protection of its keys.
- **Experiment:** Identify a distributed or predictably reused lab key, use a prepared operation to recover protected content and explain the key exposure.
- **Prerequisites:** `crypto-primitives`, `data-representation`, the relevant artifact or session observation.
- **Entry and progression:** A key included in a distributed configuration; then weak generation, key reuse and separation of uses.
- **Tools:** Text/metadata observation and prepared cryptographic operations. Supply the operation so the exercise evaluates key handling.

### crypto-modes-nonces

- **Principle:** Cipher modes and nonce/IV handling impose particular requirements and can expose structure or permit unintended relationships between messages.
- **Experiment:** Compare selected plaintext/ciphertext pairs and observe repeated structure or shared output relationships in the chosen mode.
- **Prerequisites:** `crypto-primitives`, `data-representation`; explain the selected mode and its IV/nonce requirements.
- **Entry and progression:** Repeated blocks under ECB; then stream/CTR nonce reuse, CBC manipulation and oracle behavior as separately explained branches.
- **Tools:** Transform workbench and a real local cryptographic target or supplied artifacts. Provide comparison and scoped byte operations without requiring Python implementation.

### crypto-hashes-authentication

- **Principle:** A digest, a keyed authentication tag and encryption establish different security properties.
- **Experiment:** Modify a message and test which supplied verifier accepts it; identify the authority or secret absent from the vulnerable construction.
- **Prerequisites:** `crypto-primitives`, `data-representation`, and the verification workflow supplied by the exercise.
- **Entry and progression:** A public unkeyed digest is treated as proof of message authenticity; then MAC construction, verification behavior and algorithm-specific extension issues.
- **Tools:** Prepared hash/MAC operations and local verifier. The explanation distinguishes integrity checks from authentication in the actual scenario.

### crypto-public-keys-signatures

- **Principle:** Public-key use must preserve the distinction between public verification/encryption information and secret authority.
- **Experiment:** Compare accepted and modified signed messages against an annotated verifier; identify whether the signer or algorithm is actually enforced.
- **Prerequisites:** `crypto-primitives`, `data-representation`; introduce the exact signature fields and verification flow.
- **Entry and progression:** A lab verifier accepts a declared signature without verifying it; then algorithm/key confusion, weak parameters and nonce failures with their additional mathematics taught first.
- **Tools:** Prepared verification and signing operations, plus request or artifact inspection. Advanced numeric analysis needs its own prerequisite material and prepared calculator.

## Digital forensics

### forensics-files-metadata

- **Principle:** File contents, format signatures and metadata can reveal evidence that a filename or visible document does not describe.
- **Experiment:** Compare an artifact's extension, leading bytes and metadata; substantiate what it contains or exposes from those observations.
- **Prerequisites:** `files-processes`, `data-representation` for byte inspection; introduce the format fields used.
- **Entry and progression:** A misleading extension or exposed document property; then embedded artifacts, carving and reconstruction.
- **Tools:** Hex/metadata view, prepared file identification and extraction tools. Preserve the original artifact when experimenting on a copy.

### forensics-network-evidence

- **Principle:** Captured network exchanges can establish what data and actions crossed a network boundary.
- **Experiment:** Select a small relevant conversation, reconstruct its request/response or transferred object, and cite the records supporting the finding.
- **Prerequisites:** `http-messages`, `data-representation`; introduce connection identifiers, packet order and the selected protocol.
- **Entry and progression:** Recover a disclosed credential or artifact from a local capture; then multiple conversations, fragmented data and protocol-specific evidence.
- **Tools:** Prepared capture viewer or annotated command output with stream reconstruction. Captures come from the authored local lab.

### forensics-event-reconstruction

- **Principle:** Correlating events supports an evidence-based account of access or compromise, within the limits of the recorded observations.
- **Experiment:** Order supplied events, connect account/resource identifiers and explain the observed route to a protected resource.
- **Prerequisites:** `state-ordering`, `http-messages` for the first web-log exercise; introduce timestamps, time zones and log fields.
- **Entry and progression:** Trace a single suspicious resource access; then multiple sources, conflicting clocks and incomplete evidence.
- **Tools:** Text preview and prepared search/timeline operations. The answer and walkthrough cite evidence rather than inventing unrecorded events.

### forensics-memory-evidence

- **Principle:** A memory snapshot may retain processes, connections or sensitive material that is absent from visible files.
- **Experiment:** Inspect one identified process in a supplied dump and substantiate an observable secret or activity using actual snapshot data.
- **Prerequisites:** `files-processes`, `memory-layout`, `data-representation`; introduce snapshot provenance and the specific process fields.
- **Entry and progression:** Recover evidence from a known lab process; then cross-process activity, hidden state and correlated artifacts.
- **Tools:** Prepared dump-analysis tools and compatible profiles. Record tool limitations, snapshot coverage and resource requirements.

### forensics-storage-recovery

- **Principle:** File deletion and storage allocation affect recoverable evidence differently from the visible directory listing.
- **Experiment:** Compare the visible files with recoverable records or bytes in a supplied image; recover and identify one supported artifact.
- **Prerequisites:** `files-processes`, `data-representation`; introduce the selected filesystem's metadata and allocation model.
- **Entry and progression:** Recover an unoverwritten deleted lab file; then fragmented artifacts, filesystem metadata and multiple partitions.
- **Tools:** Prepared image/filesystem analysis and extraction tools. Work on repository-contained copies and record image size and resource cost.

## Network security

### network-protocol-state

- **Principle:** A protocol implementation must preserve message boundaries and validate the state in which each operation is allowed.
- **Experiment:** Compare an ordinary local exchange with a changed length or reordered message and observe the server's actual state transition.
- **Prerequisites:** `data-representation`, `state-ordering`, `files-processes`; introduce the small protocol's fields and normal exchange.
- **Entry and progression:** A TCP service accepts an operation before its required step; then framing, parser disagreement and replay as separate branches.
- **Tools:** Local TCP target and prepared message sender in the terminal. Internal UDP exchanges can use ordinary sockets; browser/host UDP endpoints and raw packet operations are separate unsupported capabilities.

### network-service-trust

- **Principle:** Reachability or a caller-supplied identity is insufficient evidence of a service's authority.
- **Experiment:** Compare a local service's response to an ordinary request and a request with a changed claimed identity or destination; identify the trust assumption.
- **Prerequisites:** `http-messages` or the supplied protocol vocabulary, `sessions`, `web-addresses` where names are used.
- **Entry and progression:** A service trusts a supplied peer identity field; then local name-resolution, certificate and service-discovery checks.
- **Tools:** Authored internal services and prepared client commands. Real transport evidence must come from the actual transport; routing, packet interception and host network changes need a separate feasibility decision.

### network-wireless-evidence

- **Principle:** Wireless authentication and protection can be assessed from the specific exchanges and parameters visible in recorded evidence.
- **Experiment:** Inspect a supplied wireless capture, locate the relevant exchange and substantiate the stated protection or exposed information.
- **Prerequisites:** `data-representation`, `state-ordering`; introduce frame fields and the particular authentication/protection scheme.
- **Entry and progression:** Identify exposed information in a supplied capture; then recorded authentication exchanges and protocol-specific analysis.
- **Tools:** Prepared offline capture viewer and real authored evidence. Live radio transmission, monitor mode and physical adapters are outside the current platform policy; a capture exercise teaches evidence analysis.

## Cloud and infrastructure security

### cloud-identity-policies

- **Principle:** Effective authorization depends on the combined identity, resource, action and policy conditions.
- **Experiment:** Compare supplied policy decisions for two lab identities, vary one action or resource and identify the rule that grants unintended access.
- **Prerequisites:** `sessions`, `state-ordering`; introduce policy syntax, rule precedence and scope.
- **Entry and progression:** A broad resource/action grant; then policy composition, delegation and short-lived credentials.
- **Tools:** Policy artifacts and a labelled local evaluator with explicit semantics. Validate any provider-specific claim against that provider's rules; access to a real external cloud account is outside runtime isolation.

### cloud-storage-exposure

- **Principle:** Object storage permissions and access tokens must preserve the intended object and identity boundaries.
- **Experiment:** Compare access to private and shared objects on an authored local object-storage target; change the object or permission and inspect the actual result.
- **Prerequisites:** `web-addresses`, `http-messages`, `sessions`; introduce the selected storage API and permission model.
- **Entry and progression:** An unintended public object or listing; then scoped access tokens and separation between object and bucket permissions.
- **Tools:** Prepared local storage service and browser/request client. A compatible API is identified by its actual implementation; it does not prove identical behavior on a public cloud provider.

### cloud-orchestration-boundaries

- **Principle:** Workload declarations, service identities and orchestration permissions determine which infrastructure actions an application can perform.
- **Experiment:** Inspect supplied workload and policy artifacts, connect an overbroad permission to its documented consequence and compare a restricted configuration.
- **Prerequisites:** `files-processes`, `state-ordering`, identity/permission concepts; introduce only the selected orchestration fields.
- **Entry and progression:** An excessive service-account permission in supplied manifests; then an actual isolated control-plane exercise after its runtime is verified.
- **Tools:** Artifact viewer and scoped policy/configuration inspection. A real control plane is an unverified runtime; host Docker sockets, nested privileged Docker and host cluster access are outside policy.

## Mobile security

### mobile-local-data

- **Principle:** Bundled or persisted mobile application data can expose information beyond the intended user or protection boundary.
- **Experiment:** Inspect an authored package or data snapshot and recover the protected value from the actual supplied artifact.
- **Prerequisites:** `files-processes`, `data-representation`; introduce the selected package or storage format and its origin.
- **Entry and progression:** A credential in bundled configuration; then local databases, backups and native components.
- **Tools:** Prepared archive, database and package viewers. Static snapshots support artifact claims; actual mobile storage enforcement requires the corresponding runtime.

### mobile-backend-trust

- **Principle:** A mobile client does not provide a trusted authorization boundary for its backend.
- **Experiment:** Inspect a supplied ordinary client exchange, change a claimed account or operation and compare the local backend's access decision.
- **Prerequisites:** `http-messages`, `sessions`; explain the client/backend roles and the request field being tested.
- **Entry and progression:** A backend trusts a client-supplied account identifier; then client-only workflow controls and replay protection.
- **Tools:** Real local backend and request inspector or prepared client. An emulator is needed only when the learning objective depends on actual client execution.

### mobile-runtime-integrity

- **Principle:** Platform permissions and app integrity checks have specific enforcement points whose effects must be observed in the real runtime.
- **Experiment:** Compare a permitted and denied app action in a prepared mobile runtime and identify the enforcing component.
- **Prerequisites:** `files-processes`, `state-ordering`, `execution-tracing`; introduce the exact platform permission or integrity mechanism.
- **Entry and progression:** One app permission boundary; then inter-app access, instrumentation and integrity-check bypass.
- **Tools:** Unverified mobile runtime, app controls and instrumentation profile. Current tools have no emulator display or device integration. Artifact inspection is a distinct exercise; host devices and accelerated-device passthrough are outside policy.

## Hardware and embedded security

### hardware-firmware-artifacts

- **Principle:** Distributed firmware can reveal credentials, exposed services and security decisions through its contents.
- **Experiment:** Inspect a real authored firmware artifact, locate the relevant configuration or code and connect it to the documented device behavior.
- **Prerequisites:** `files-processes`, `data-representation`; introduce the selected container/filesystem format.
- **Entry and progression:** A credential in extracted configuration; then filesystem structure, update verification and compiled components.
- **Tools:** Prepared extraction and static analysis commands. Tools must read or extract repository-contained files without loop devices or privileged mounts; full device execution needs separate verification.

### hardware-device-protocols

- **Principle:** An embedded command interface must enforce operation authority and state constraints independently of transport access.
- **Experiment:** Send ordinary and modified messages to an authored local protocol target and compare the actual accepted commands and state changes.
- **Prerequisites:** `data-representation`, `state-ordering`; introduce command framing and device states.
- **Entry and progression:** An omitted command authorization check; then update commands and replay-sensitive control flows.
- **Tools:** Local protocol implementation and prepared sender. Identify any emulated device model; claims about physical hardware require hardware evidence. USB, serial and debug-adapter passthrough are outside policy.

### hardware-physical-evidence

- **Principle:** Physical measurements can reveal information about device operations within the limits of the measurement and experimental setup.
- **Experiment:** Compare supplied traces with labelled operations and recover the specific correlation supported by the actual measurements.
- **Prerequisites:** `data-representation`, `state-ordering`, the narrowly required statistics and timing concepts.
- **Entry and progression:** Correlate labelled timing/power traces; then larger datasets and recorded fault responses with additional prerequisites.
- **Tools:** Prepared trace viewer and scoped analysis operations. Mark synthetic traces as synthetic. Actual measurement and fault injection require external hardware and are outside the current platform policy.

## Software supply-chain security

### supply-chain-history

- **Principle:** Software provenance, build configuration and dependency authority can expose secrets or influence the delivered artifact.
- **Experiment:** Inspect a supplied history or build record, identify the change that carries sensitive data or unwanted authority, and verify its consequence in the local lab.
- **Prerequisites:** `files-processes`, `state-ordering`; introduce revisions, diffs and the relevant build step.
- **Entry and progression:** Recover a secret from a removed historical file; then dependency selection, artifact changes and local build-step permissions.
- **Tools:** Prepared history/diff or Git commands; authored local package/build fixtures for later variants. Required dependencies are supplied with the exercise.

### supply-chain-builds

- **Principle:** Dependency selection and build inputs can grant unintended influence over a delivered program.
- **Experiment:** Compare two fully local build inputs, identify the changed dependency or hook and observe its effect in the resulting artifact.
- **Prerequisites:** `files-processes`, `state-ordering`; introduce the dependency selection and build step used.
- **Entry and progression:** A local dependency substitution changes a security-relevant value; then install hooks and compromised build inputs.
- **Tools:** Prepared compiler/package commands and local dependency fixtures in an ordinary container. Keep runtime builds offline and unprivileged; real registries, Docker socket access and privileged nested builders are outside policy.

### supply-chain-provenance

- **Principle:** A provenance claim must establish who produced an artifact and which content and build inputs it covers.
- **Experiment:** Compare a supplied artifact with its signed or hashed record, modify one value and identify whether the actual verifier enforces the stated linkage.
- **Prerequisites:** `files-processes`, `data-representation`, `crypto-primitives` at the scope of the supplied verifier.
- **Entry and progression:** A manifest does not bind the claimed digest to the distributed file; then identity, signatures and build-input evidence.
- **Tools:** Prepared artifact and attestation verification commands with local trust material. The exercise names the chosen format and verifier; no live hosted signing service is required.

## AI security

### ai-instruction-boundaries

- **Principle:** Agent decisions must preserve the boundary between trusted authority, untrusted content and permitted tools or data.
- **Experiment:** Compare tool actions with ordinary and instruction-bearing retrieved material; show whether the target grants authority to that material.
- **Prerequisites:** `state-ordering`, `http-messages` for the target API; introduce model output, retrieved content and tool permissions.
- **Entry and progression:** One local document causes an agent to attempt a prohibited lab action; then retrieval provenance, tool authorization and model artifacts.
- **Tools:** Prepared local model/agent and action trace. Label a deterministic model fixture as a fixture; model-behavior claims require tests against the actual model and its resource profile.

### ai-retrieval-access

- **Principle:** Retrieval and tool data access must enforce the acting identity's permissions before supplying protected material.
- **Experiment:** Compare the actual local retrieval results for two lab identities and change a document reference to test the access check.
- **Prerequisites:** `http-messages`, `sessions`; introduce retrieval scope, document identity and the acting principal.
- **Entry and progression:** An unauthorized document returned by a retrieval API; then cross-user indexes and delegated tool identities.
- **Tools:** Real local retrieval service and prepared request client. A model is unnecessary for a retrieval authorization objective; claims about model decisions need actual model execution.

### ai-model-artifacts

- **Principle:** Model packaging and loading establish trust boundaries for metadata, executable content and dependencies.
- **Experiment:** Inspect an authored model package, identify a risky loading option or exposed metadata and verify the consequence in a prepared local loader.
- **Prerequisites:** `files-processes`, `data-representation`; introduce the chosen artifact format and loading behavior.
- **Entry and progression:** Exposed sensitive model metadata; then unsafe deserialization and dependency loading after loader verification.
- **Tools:** Artifact inspection and a pinned offline loader. Actual inference needs a verified CPU/resource profile; host GPU access is outside policy. Label model fixtures and preserve enclosing isolation.

## Blockchain security

### blockchain-caller-authority

- **Principle:** Contract state transitions must enforce caller authority and the intended asset or workflow rules.
- **Experiment:** Compare the same state-changing call from two supplied lab identities and inspect the resulting contract state and transaction evidence.
- **Prerequisites:** `state-ordering`, `crypto-primitives` for identity/signatures; introduce callers, transactions and the supplied contract interface.
- **Entry and progression:** A local contract action lacks the stated caller check; then balances, reentrant calls and transaction ordering with their added prerequisites.
- **Tools:** Authored local chain, prepared identities and call interface. Players invoke actual lab transactions through the provided controls without writing a client SDK.

### blockchain-state-reentrancy

- **Principle:** Contract state must preserve its invariants across external calls and repeated entry into a workflow.
- **Experiment:** Compare an ordinary transaction with a prepared callback sequence and trace the actual balance and state updates on the local chain.
- **Prerequisites:** `state-ordering`, `execution-tracing`, the caller and transaction concepts introduced by the preceding exercise.
- **Entry and progression:** A balance update occurs after a callback; then cross-function invariants and token-specific behavior.
- **Tools:** Verified local chain, supplied actor contracts and a prepared transaction/trace interface. The player chooses the sequence; actual VM execution supports the observed result.

### blockchain-transaction-ordering

- **Principle:** A contract's assumptions about transaction order and external values can affect the authority and fairness of its state changes.
- **Experiment:** Compare the same prepared transactions in two controlled orders and inspect the actual local-chain result.
- **Prerequisites:** `state-ordering`, transaction and block concepts; introduce the selected pricing or settlement rule.
- **Entry and progression:** A state-dependent action accepts a changed ordering; then local price-oracle and settlement assumptions.
- **Tools:** Verified local chain with deterministic block/transaction controls and declared internal data sources. Public networks, real funds and external oracle access are outside runtime policy.

## Turn a topic into a publishable exercise

For each chosen topic, name the exact concepts taught and required, the first
observation and the normal operation used as a comparison. Keep the entry
exercise focused on one security principle, then establish its actual difficulty
through the [authoring review](authoring-standard.md#review-before-publication).

The topic map provides authoring coverage; it does not prove runtime readiness,
pedagogical suitability or a finished exercise. Add the player explanations,
real target/artifact, prepared tools, intended solution, progressive hints and
walkthrough, then record their execution and learner review evidence.

Note Vault currently maps to `web-access-control`. Rotor Lock maps to
`rev-input-checks` and needs its player path and workload reassessed against the
direct-experiment standard. Their published manifest difficulty values remain
separate from this topic assignment.

## Technical references

The taxonomy and entry exercises above are pwnden authoring choices. Use primary
references to check a particular mechanism and its defensive explanation; give
players sufficient local material for the exercise itself.

- Web testing areas: [OWASP WSTG v4.2](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/).
- Memory boundary, numeric and lifetime defects: [CWE-120](https://cwe.mitre.org/data/definitions/120.html), [CWE-190](https://cwe.mitre.org/data/definitions/190.html), [CWE-416](https://cwe.mitre.org/data/definitions/416.html).
- Running targets under a debugger: [GDB documentation](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Running.html).
- Block-cipher modes: [NIST SP 800-38A](https://csrc.nist.gov/pubs/sp/800/38/a/final). Use the specification for the particular selected mode or algorithm for additional requirements.
- Forensic data sources and analysis: [NIST SP 800-86](https://csrc.nist.gov/pubs/sp/800/86/final).
- Untrusted instructions in model inputs: [OWASP prompt-injection guidance](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).
