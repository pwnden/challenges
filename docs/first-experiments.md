# First security experiments

This batch uses the current contract and existing player tools. Each scenario
includes a request briefing, scoped starting knowledge, three progressive hints,
a reproducible investigation report and a problem-specific author record.
The usual player path requires text reading and supplied tool operations.

| Scenario | Topic | Level | Player tools | Observation |
| --- | --- | --- | --- | --- |
| [Forgotten Shelf](../challenges/forgotten-shelf/README.md) | `web-information-disclosure` | Intro | Web | A removed link and a public collection rule leave a backup readable. |
| [Query Desk](../challenges/query-desk/README.md) | `web-injection` | Easy | Web | Search input changes an actual SQLite condition and exposes a private row. |
| [Wrapped Secret](../challenges/wrapped-secret/README.md) | `crypto-representation-protection` | Intro | Files, terminal | A public Base64 operation recovers an exposed key. |
| [Midnight Trace](../challenges/midnight-trace/README.md) | `forensics-event-reconstruction` | Intro | Files | Matching request IDs connect a guest's successful request to another owner's export. |

Forgotten Shelf, Wrapped Secret and Midnight Trace are independent starting
experiments. Query Desk adds condition syntax and inference; its brief explains
the query vocabulary before the player changes input. Note Vault remains an
access-control experiment. Rotor Lock keeps its existing implementation and
code-analysis workload.

The briefs contain the required background directly. Shared concept declarations
and a graph UI remain separate work; this batch uses the existing learning map
and version 5 content contract.

## Verification and review

The service scenarios include a patch and a functional check. Verification runs
actual target and solution containers, then checks attack denial, normal behavior
and resource cleanup. Wrapped Secret's solution executes the same `base64`
command supplied to the player. Midnight Trace distributes records captured from
six real HTTP exchanges with a local teaching fixture; its author capture script
regenerates the files. These records model an incident in that fixture.

Run from the challenges checkout:

```sh
python3 -B tools/validate.py
python3 -B tools/verify.py forgotten-shelf query-desk wrapped-secret midnight-trace
python3 -B -m unittest discover -s tools -p 'test_*.py'
python3 -B tools/check_isolation.py
```

Author records distinguish technical checks from learning review. The four new
scenarios require independent target-learner feedback before publication and
final difficulty assessment. Local commits and passing execution checks record
implementation progress; publication follows the authoring standard's review gate.
