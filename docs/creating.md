# Creating a scenario

A scenario is a hacking request that the player investigates in the prepared
workspace. Use the [scenario writing framework](scenario-authoring.md) for its
briefing, additional information and investigation report. The existing
challenge contract supplies its declarations and execution profile.

Start with the [authoring standard](authoring-standard.md): define the security
learning objective, intended learner and prerequisite abilities before choosing
resources and execution kind. Record the intended solution and difficulty
assessment in the generated `AUTHORING.md` as the exercise takes shape.
Use the [learning map](learning-map.md) to select the primary area and topic,
the security experiment and required tool capabilities.
Check the [execution feasibility map](execution-feasibility.md) for its actual
runtime requirements. `--category` selects an existing contract classification;
record the independent learning area and topic in `AUTHORING.md`.

From the challenges repository, use Python 3.11 or newer:

```sh
python3 tools/create.py rotor-example --kind file --category rev --difficulty 2 --title "입력 검사 분석"
python3 tools/create.py vault-example --kind service --category web --difficulty 1 --title "개인 메모의 접근 권한" --patched
python3 tools/create.py session-example --kind service --category web --title "접속 상태 확인" --patched --concept http-messages --concept http-cookies
```

The generator owns the repeated directory layout, manifest declarations,
learning-content paths and initial runtime configuration. The author supplies
the actual exercise, resources, intended vulnerability, solution and explanation.
Templates live under `tools/templates`; update them centrally when authoring
conventions change. CI discovers their regression tests with the existing tools
test command. The generator supports contract version 5 and uses its existing
validator before reporting success. Update the templates explicitly for another
contract version.

## Options

| Option | Behavior |
| --- | --- |
| `<slug>` | Creates `challenges/<slug>`; follows the contract's 1–40 character slug syntax and excludes Windows device names. |
| `--kind file` | Creates distribution material, a fixed-flag declaration and solution scaffold. |
| `--kind service` | Creates Python target logic, a Vue screen, Dockerfile and Compose configuration. |
| `--category` | Required: `web`, `pwn`, `rev`, `crypto`, `forensics` or `misc`. Category and execution kind are independent. |
| `--title` | Korean display title; defaults to the authoring placeholder `새 시나리오`. Set the final title before publication. |
| `--difficulty` | 1 Intro, 2 Easy, 3 Medium, 4 Hard, 5 Expert; defaults to 1. Review the intended solution against the contract criteria before publication. |
| `--hints` | Generates 0–10 optional declared hints; defaults to 0. Choose the count for distinct points where a learner may get stuck. |
| `--concept` | Connects a shared prerequisite from `knowledge/<id>.md`; repeat for additional concepts. Creates `BRIEFING.md` and compiles the player brief. |
| `--patched` | Adds a service Compose override, patch source and functional-check scaffold. |
| `--image` | Python 3 image used by the toolbox and starter service; defaults to the repository's current pinned Python image and digest. |
| `--dry-run` | Lists the files that would be created and writes nothing. |
| `--repo` | Selects a challenges checkout; defaults to the checkout containing the script, independently of the current directory. |

Preview a service layout first:

```sh
python3 tools/create.py vault-example --kind service --category web --patched --dry-run
```

Existing directories, files and links are preserved. Creation is exclusive, and
a failed write or validation cleans up the newly created directory. Generated
files use UTF-8, LF line endings and portable relative paths. This is an author
tool; players receive completed problems through the platform's existing setup.

## Generated layouts

Every problem gets `challenge.toml`, `README.md`, `AUTHORING.md`, `solve/solve.py`,
`solve/README.md` and the chosen number of hint files under `hints/`.

File problems also get `files/data.txt`. Service problems get `compose.yaml`,
`.dockerignore`, `vulnerable/Dockerfile`, `vulnerable/app.py` and
`vulnerable/web/App.vue`. The optional
patch adds `compose.patched.yaml`, `patched/app.py` and `patched/test.py`.

The HTTP starter binds container port 8000, exposes `/healthz`, receives the
runner's generated `FLAG` and uses the declared solution network. The manifest
declares its HTTP endpoint; the platform supplies isolated networking and local
browser ingress as common capabilities. It runs as a non-root user with a read-only container
filesystem, dropped capabilities and `no-new-privileges`. The generated network
is internal. The toolbox timeout, network and write permissions follow contract
defaults; the manifest writes only explicit exercise requirements.

Python is the starter implementation. Authors can replace target source and
runtime requirements as the exercise requires. TCP and multi-service exercises
use the same contract; their services and endpoint declarations are authored to
match their requirements. The platform derives its tools from those declarations.

Service screens use the repository's [shared Vue presentation](target-web.md).
Python owns HTTP behavior, data, permissions and the intended vulnerability;
the problem's Vue component owns its screen. The repository owns asset serving,
offline font delivery and the pinned build toolchain.

## Complete before publication

### Shared starting knowledge

Use [shared starting notes](../knowledge/README.md) for reusable prerequisite
explanations. With `--concept`, edit `BRIEFING.md` for the scenario context and
keep the empty `::knowledge{concepts="id,other-id"}` block. Edit the referenced
concept Markdown to improve a shared explanation. Then run:

```sh
python3 tools/content.py
python3 tools/content.py --check
```

The first command refreshes all compiled briefs. The second checks equality
without writing; ordinary format and execution verification also reject stale
compiled prerequisites. The generated `README.md` remains the contract v5 player
document and displays the notes within the existing website reading pane.
Author records receive the concept reference links. Scenarios authored directly
in `README.md` retain their existing workflow.

### Scenario completion

1. Complete `AUTHORING.md` using the [authoring standard](authoring-standard.md).
   Define the request, player role and actual evidence behind its clues.
   Trace the intended solution, classify prerequisite and learning concepts,
   and explain the declared difficulty against the full player journey.
2. Complete the request briefing, objective and supplied information using the
   [scenario framework](scenario-authoring.md) and
   [player content standard](player-content.md). Titles
   and categories are displayed by the platform; the brief starts with context.
3. Replace sample distribution material or implement target behavior. The starter
   HTTP service reports preparation in progress outside its health route.
4. Implement `solve/solve.py` to recover and print the flag. For file problems,
   replace the marked zero digest with the SHA-256 of the solution's trimmed flag.
5. Write progressive additional information and an investigation report that
   explains and reproduces the reasoning and security principle.
   For patch verification, implement the patch and functional check.
6. Complete the [publication review](authoring-standard.md#review-before-publication),
   including an independent learner review. Record the actual evidence and
   revision in `AUTHORING.md`. Run `python3 tools/validate.py` and this repository's
   [execution checks](verification.md#author-execution-checks):
   `python3 tools/verify.py <slug>`. Author verification uses Python and Docker.
7. Commit the reviewed catalog on `main` and run `python3 tools/publish.py`.
   The [publication command](publishing.md) rechecks the committed snapshot's
   author tools, isolation, solutions, patches and cleanup before pushing it.

The generated manifest passes format validation. Solution and functional-check
stubs exit with an explicit authoring error, so scaffolding does not pass
execution verification until the exercise is complete. The optional patched
source starts from the same HTTP skeleton for the author to implement.

Problem discovery, terminal preparation, web navigation, file display, hints,
walkthroughs and submissions follow the declarations through common platform
features. Problem authors maintain the exercise-specific content and execution
requirements.
