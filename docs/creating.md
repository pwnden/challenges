# Creating a problem

From the challenges repository, use Python 3.11 or newer:

```sh
python3 tools/create.py rotor-example --kind file --category rev --difficulty 2 --title "Rotor Example"
python3 tools/create.py vault-example --kind service --category web --difficulty 1 --title "Vault Example" --patched
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
| `--kind service` | Creates a Python HTTP starter, Dockerfile, Compose configuration and a generated-flag HTTP endpoint. |
| `--category` | Required: `web`, `pwn`, `rev`, `crypto`, `forensics` or `misc`. Category and execution kind are independent. |
| `--title` | Display title; defaults to title-cased slug words. |
| `--difficulty` | 1 Intro, 2 Easy, 3 Medium, 4 Hard, 5 Expert; defaults to 1. Review the intended solution against the contract criteria before publication. |
| `--hints` | Generates 0–10 declared hints; defaults to 3. |
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

Every problem gets `challenge.toml`, `README.md`, `solve/solve.py`,
`solve/README.md` and the chosen number of hint files under `hints/`.

File problems also get `files/data.txt`. Service problems get `compose.yaml`,
`.dockerignore`, `vulnerable/Dockerfile` and `vulnerable/app.py`. The optional
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

## Complete before publication

1. Replace bracketed authoring prompts with the scenario, objective and supplied
   information. Follow the [player content standard](player-content.md). Titles
   and categories are displayed by the platform; the brief starts with context.
2. Replace sample distribution material or implement target behavior. The starter
   HTTP service reports preparation in progress outside its health route.
3. Implement `solve/solve.py` to recover and print the flag. For file problems,
   replace the marked zero digest with the SHA-256 of the solution's trimmed flag.
4. Write progressive hints and a walkthrough that explains and reproduces the
   reasoning. For patch verification, implement the patch and functional check.
5. Review the declared difficulty against the intended solution without hints. Run `python3 tools/validate.py` and the platform's [execution checks](verification.md#maintainer-execution-checks).

The generated manifest passes format validation. Solution and functional-check
stubs exit with an explicit authoring error, so scaffolding does not pass
execution verification until the exercise is complete. The optional patched
source starts from the same HTTP skeleton for the author to implement.

Problem discovery, terminal preparation, web navigation, file display, hints,
walkthroughs and submissions follow the declarations through common platform
features. Problem authors maintain the exercise-specific content and execution
requirements.
