# First security experiments

This batch uses the current contract and existing player tools. Each scenario
includes a request briefing, scoped starting knowledge, optional focused hints,
a reproducible investigation report and a problem-specific author record.
The usual player path requires text reading and supplied tool operations.

| Scenario | Topic | Level | Player tools | Observation |
| --- | --- | --- | --- | --- |
| [남겨진 백업 파일](../challenges/forgotten-shelf/README.md) | `web-information-disclosure` | 입문 | Web | A removed link and a public collection rule leave a backup readable. |
| [비공개 회원 검색](../challenges/query-desk/README.md) | `web-injection` | 초급 | Web | Search input changes an actual SQLite condition and exposes a private row. |
| [문자로 바꾼 복구 키](../challenges/wrapped-secret/README.md) | `crypto-representation-protection` | 입문 | Files, terminal | A public Base64 operation recovers an exposed key. |
| [자료 유출 기록](../challenges/midnight-trace/README.md) | `forensics-event-reconstruction` | 입문 | Files | Matching request IDs connect a guest's successful request to another owner's export. |

The [complete learning order](learning-order.md) places this batch within the
current catalog. `forgotten-shelf` prepares later history exercises;
`midnight-trace` follows identity and object-ownership preparation. `query-desk`
needs scoped database vocabulary, while `rotor-lock` remains a separate code-analysis branch.

The briefs provide the situation, goal and supplied access. Contract v7 connects
optional concept reading, predecessors, successors and related practice through
shared declarations. Hints help blocked decisions; walkthroughs contain the
reproducible commands and criteria.

## Verification and review

The service scenarios include a patch and a functional check. Verification runs
actual target and solution containers, then checks attack denial, normal behavior
and resource cleanup. The `wrapped-secret` solution executes the same `base64`
command available in the toolbox. The `midnight-trace` scenario distributes records captured from
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
