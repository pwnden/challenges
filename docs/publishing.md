# Publishing a catalog

Challenges owns problem creation, review, execution verification and publication.
The publication unit is a committed catalog on this repository's `main` branch.
Platform selects an already published commit and consumes its versioned contract.

## Author workflow

Run these commands from the challenges repository:

```sh
python3 tools/create.py example --kind service --category web --patched
# Complete the exercise, solution, hints, walkthrough and AUTHORING.md.
# Add or reassess quality/reviews/<slug>.json with source evidence.
python3 -B tools/quality.py
python3 tools/verify.py example
# Review and commit the completed changes on main.
python3 tools/publish.py --check
python3 tools/publish.py
```

Use the [authoring standard](authoring-standard.md#review-before-publication) for
the learning and content review. Execution tests provide technical evidence;
the author records learner-review and difficulty evidence in `AUTHORING.md`.
Python 3.11+, Docker Engine 28+ with Compose run the checks. Git is additionally
required for publication. The workflow uses this repository alone.

## Verified commit publication

`tools/publish.py` requires a clean worktree, including untracked files, on
`main`. It records `HEAD` and exports that commit with `git archive` to a
temporary catalog under ignored `.authoring/`. Only committed catalog files are
included. The temporary checkout contains its own contract and author tools.

The snapshot must pass:

1. Complete, evidence-backed and current [quality reviews](quality-review.md).
2. Author-tool regression tests.
3. Vue screen types and rendered behavior through the pinned Docker toolchain.
4. Actual network isolation with reachable host and separate-network controls.
5. Format checks and every declared solution, patch and resource-cleanup check.

The [verification guide](verification.md) defines those checks and their
coverage. The host control currently requires a locally accessible Linux/WSL
Docker bridge. Publication fails explicitly if a required gate is unavailable.

After verification, the command checks that the source worktree is still clean
and `HEAD` still names the recorded commit. It pushes that exact commit to
`origin/main` using an ordinary fast-forward Git push. A concurrent remote
update that cannot be fast-forwarded fails publication. Snapshot directories
are removed after success or failure. Docker image/build caches remain.

`--check` runs the same gates and leaves the remote unchanged. `--remote <name>`
selects another configured Git remote; `--repo <path>` selects a checkout.
`--prepare-timeout <seconds>` changes image preparation and service startup
limits. Failed or interrupted checks prevent the push. Child execution checks
receive an orderly termination signal and a bounded cleanup period when the
publication gate reaches its own time limit.

Use this command for the verified publication path. GitHub Actions independently
repeats the checks on pushes and pull requests; branch protection is a separate
repository setting. The tool does not configure it.

## Platform consumption

After publication, a platform maintainer selects the published revision using
`./pwnden catalog update --revision <full-commit>` in the platform repository and
commits its `catalog.lock` change. End users use the platform's normal setup.
Author tooling does not modify the platform repository or its lock file.

The existing Git catalog distribution remains the publication format. Separate
release archives are unnecessary for this workflow. Platform's own CI verifies
its runtime and player integration against published problems, independently
of these author gates.
