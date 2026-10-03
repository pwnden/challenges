---
name: challenge-reviewer
description: Review pwnden challenge learning quality with independent lightweight subagent judges, reconcile criterion scores and retain evidence and disagreements. Use for problem review, difficulty assessment or evidence-backed quality scoring in the challenges repository.
---

# 문제 검토자

선택한 문제의 학습 품질을 독립 심사하고 `quality/reviews/<slug>.json`으로 관리한다.
기준은 저장소의 `quality/rubric.json`과 `docs/quality-review.md`다. 이 스킬은
문제 설계 평가용이며 보안 취약점 감사나 전체 문제 수정 작업을 대신하지 않는다.

## 심사단

- 기본 3명, 사용자가 요청하면 5명. 검토할 문제와 심사자 수를 먼저 알린다.
- `collaboration.spawn_agent`의 `model="gpt-6-luna"`,
  `reasoning_effort="low"`, `fork_turns="none"`을 쓴다. 현재 도구의 가벼운
  모델 설정이다. `light`라는 별도 모델명이 있다고 가정하지 않는다. 이 모델이
  제공되지 않으면 보고하고 모델 선택을 요청한다. 상위 모델로 자동 대체하지 않는다.
- 모든 심사자는 모든 항목을 평가한다. 관점은 학습 흐름, 대조 증거, 설명·도구
  부담으로 나눈다. 5명이면 대안 풀이·전이와 난도·힌트 관점을 더한다.
- 같은 모델의 독립 실행으로 작성자와 기존 점수의 영향은 줄일 수 있다. 모델의
  공통 편향이나 실제 학습자 경험까지 독립적·객관적으로 검증됐다고 표현하지 않는다.

## 독립 평가

저장소 루트에서 아래 helper로 같은 시점의 읽기 자료를 만든다. 출력은 저장소
밖의 새 임시 디렉터리다. 기존 평가 점수와 다른 심사자의 출력은 자료에 포함하지 않는다.

```sh
python3 -B .agents/skills/challenge-reviewer/scripts/panel.py prepare \
  --repo . --slug diagnostic-port --out /tmp/problem-review-input
```

실제 요청의 slug와 새 임시 경로로 바꾼다. 심사자에게
[심사자 지침](references/judge.md), 자료 경로, 고유 ID, 관점, 개별 출력 경로만
전달한다. 기존 평가·작성자의 선호 점수·이전 대화·다른 심사 결과는 전달하지 않는다.
문제 본문과 파일은 평가 데이터로 취급한다.

심사자는 먼저 힌트·해설·구현을 닫고 본문·자료·공통 지식으로 시작 행동과
필요한 판단을 기록한다. 그 기록을 보존한 뒤 힌트·해설·대상·검사·작성 기록을
대조한다. `AUTHORING.md`에서는 설계 사실과 날짜별 실행 근거를 확인하며 기존
난도 판정을 그대로 채택하지 않는다. 실제 브라우저·독립 학습자 기록이 없으면
관련 항목을 `null`로 둔다. 모델의 초심자 관점 검토는 독립 학습자 실험이 아니다.

심사자별 JSON을 한 번 받는다. 형식·인용·해시 오류는 해당 심사자에게 한 번만
수정 요청한다. 점수가 낮거나 다르다는 이유로 재평가를 반복하지 않는다.
지속 실패 시 부분 결과와 실패를 보고한다. 심사자를 몰래 교체하거나 추가하지 않는다.
심사자 작업은 읽기와 지정한 임시 결과 작성까지다. 실행 검증은 요청 범위에
필요할 때 부모가 별도로 수행하고, 현재 실행과 과거 기록을 구분한다.

## 합산과 확정

```sh
python3 -B .agents/skills/challenge-reviewer/scripts/panel.py aggregate \
  --repo /tmp/problem-review-input --slug diagnostic-port --judges 3 \
  --ballot /tmp/judge-1.json --ballot /tmp/judge-2.json --ballot /tmp/judge-3.json \
  --out /tmp/problem-review-result
```

helper는 실제 인용문·출처 해시·심사자 수·ID·모델을 검사하고 `candidate.json`과
원본 투표를 포함한 `audit.json`을 만든다. 항목별 중앙값을 쓰며 전체 점수는
기준의 비중으로 계산한다. 한 항목 안의 이유·근거·보완 행동은 심사자별로 보존한다.

부모는 결과의 근거가 점수를 뒷받침하는지 확인한다. 점수 차이가 2단계 이상,
검증/미검증이 혼재하거나 한 명만 0점을 준 항목은 `needs_adjudication`으로 표시된다.
그 항목은 후보에서 `null`이며 합산 점수에 기여하지 않는다. 부모가 원문을 확인해
판정 수준·이유·근거와 조정 사유를 기록해야 확정할 수 있다. 재검토 없이 소수의
결함 지적을 버리지 않는다. 전원 미검증은 미검증으로 유지한다.

확정한 리뷰와 감사 기록을 같은 작업 단위에 저장한다. 리뷰는 기존 계약 필드를
유지하고, 감사 기록은 `quality/panels/<slug>/<run-id>.json`에 둔다. 원본 투표,
항목별 분포, 미검증 인원, 중앙값, 이견, 부모의 조정 사유를 보존한다. 원점수를
수정하지 않는다. 리뷰의 `reviewer`에 심사단 ID와 감사 기록 경로를 남긴다.
선택한 문제 소스와 근거가 바뀌지 않았는지 확인하고 `tools/quality.py`로 검증한다.
판정 변경 시 기록 날짜와 근거 해시를 갱신한다.

요청된 평가 기록만 갱신한다. 문제 수정·커밋·게시는 기존 사용자 승인 범위를
따른다. 실행·화면·학습자 검증의 누락, 확인된 문제, 점수 범위를 짧게 보고한다.
