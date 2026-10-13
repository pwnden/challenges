# Shared layout

Every problem under `challenges/<slug>/` follows one directory and document layout so
authors, reviewers and tools find the same things in the same places. `python3 tools/layout.py`
checks it, `python3 tools/validate.py` runs the same rules (without the review-file rule),
and CI runs both. [`tools/templates`](../tools/templates) holds the starting text for each
file, and `tools/create.py` output passes the check once the problem has its text review.

## Files

| Path | Rule |
| --- | --- |
| `README.md` | Player brief with the blocks `objective`, `resources`, `submission` in that order, optionally led by a requester `message`. `knowledge` may appear between them. |
| `challenge.toml`, `AUTHORING.md`, `solve/README.md` | Required. |
| `hints/<n>.md` | As many as the manifest declares. Plain text without headings; the hint list numbers them. |
| `solve/solve.py` or `solve/solve.sh`, `patched/test.py` or `patched/test.sh` | The runner commands declared in the manifest. |
| `BRIEFING.md` | Only for problems that compile shared prerequisite notes; see [creating](creating.md). |
| `compose.yaml`, `vulnerable/Dockerfile`, `vulnerable/app.py` | Service problems. The compose file declares an internal default network and publishes no ports; the platform provides ingress. |
| `.dockerignore` | Required when the service has `vulnerable/web/App.vue`. |
| `compose.patched.yaml`, `patched/` | Patch checks. A patch replaces either the whole app (`patched/app.py` with `APP_SOURCE`) or one policy module. |
| `vulnerable/policy.py`, `patched/policy.py` | The policy-swap module is always named `policy.py` (or `policy.json` for data). Do not prefix it with the topic. |
| `files/`, `authoring/`, `.gitattributes` | Distributed material, author build scripts and attribute rules. No other top-level entries. |
| `quality/text-reviews/<slug>/*.md` | At least one text review; `tools/quality.py` separately requires `quality/reviews/<slug>.json`. |

## Documents

`AUTHORING.md` starts with `# 시나리오 작성 기록` and has these sections in this order, from
the [template](../tools/templates/common/authoring.md):

1. 시나리오 설정
2. 학습 목표와 대상
3. 선수 지식과 학습 내용
4. 의도된 풀이
5. 개념 관계
6. 난도 근거
7. 다른 풀이와 정답 노출
8. 검증과 리뷰

Extra sections may follow, for example `연결된 공통 시작 지식` or earlier review notes. When
an older record held two topics in one section, the later section says where the content is.

`solve/README.md` uses only these level-2 headings, in this order: 조사 결과, 조사 과정,
의뢰 완료 확인, 드러난 보안 원리. 조사 과정 and 드러난 보안 원리 are required. A fix or
protection discussion goes in a level-3 subsection of 드러난 보안 원리.

## Known gaps

`layout.EXCEPTIONS` lists each gap in an older problem with its reason. A listed gap that is
fixed must be removed, so the list only shrinks. Do not add an entry for a new problem.
The list is empty today.
