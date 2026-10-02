## 조사 결과와 재현

없는 두 주소는 200과 동일한 공통 안내를 반환한다. 상태 코드로 찾은 후보에는
없는 경로가 섞인다. 안내 크기를 제외하면 help·healthz·ops-check가 남는다.

```sh
curl -sS http://app:8000/does-not-exist -o baseline.json
size=$(wc -c < baseline.json)
ffuf -w files/paths.txt -u http://app:8000/FUZZ -fs "$size" -t 2 -rate 10 -maxtime 15
curl -sS http://app:8000/help | jq .
curl -sS http://app:8000/ops-check | jq .
```

help는 공개 도움말이다. ops-check는 staff를 대상으로 하는 복구 기능이며
`recovery_code`를 포함한다. 그 현재 값이 제출할 `pwnden{...}`이다.
크기 차이를 관찰한 뒤 실제 내용까지 확인했으므로 안내 페이지의 오탐과
비공개 자료의 공개를 구분할 수 있다.

## 보안 원리와 수정

응답 코드는 서버가 선택한 결과다. 본문 내용이나 권한 보장을 대신하지 않는다.
운영 점검 자료는 서버에서 공개 범위를 제한해야 한다. 수정한 서버는 해당
경로를 403으로 거부하고 도움말·건강 검사·없는 주소의 안내는 유지한다.
