::message{from="흐린응답"}
없는 주소도 전부 정상이라고 나와요. 상태 코드만 보면 구분이 안 됩니다. 운영 자료가 공개돼 있다는 제보를 실제 본문으로 확인해 주세요.
::

흐린응답은 납품 보드의 운영 담당자다. 보드는 공개 도움말과 서비스 상태를
누구나 읽게 한다. 운영 점검 자료와 장애 복구 코드는 담당자만 읽어야 한다.

서버는 없는 경로에도 공통 안내 페이지를 200으로 반환한다. 운영 자료가 보인다는
제보가 왔지만, 상태 코드만 수집한 목록으로는 실제 자료와 안내 응답을 구분하지
못했다. 흐린응답은 실습 서버·작은 후보 목록·공개 정책을 길드에 제공하고,
어떤 응답이 비공개 내용을 담는지 재검증을 맡겼다.

::objective
공통 안내와 다른 응답을 찾고, 실제 본문을 공개 정책과 비교해 잘못 공개된 복구 코드를 확인하자.
::

::resources{title="서버와 후보 자료"}
- 서버 주소는 문제 네트워크의 `http://app:8000`이다.
- `files/paths.txt`에는 조사할 후보 경로 12개가 있다.
- `files/public-policy.txt`는 공개 가능한 자료의 범위를 정한다.
- `/help`와 `/healthz`는 공개 기능이다.

먼저 서로 다른 없는 주소의 본문을 저장하고 비교하자.

```sh
curl -sS http://app:8000/does-not-exist -o first.json -w '%{http_code}\n'
curl -sS http://app:8000/another-missing -o second.json -w '%{http_code}\n'
wc -c first.json second.json
cmp first.json second.json
```

후보 탐색에는 아래 `크기`를 공통 안내의 바이트 수로 바꾼다. 결과에 남은 주소를
`curl -sS 주소 | jq .`로 열어 실제 내용과 공개 정책을 비교하자.

```sh
ffuf -w files/paths.txt -u http://app:8000/FUZZ -fs 크기 -t 2 -rate 10 -maxtime 15
```
::

::knowledge{concepts="terminal-commands,http-messages,response-comparison"}
::

::submission
비공개 점검 응답에서 확인한 현재 환경의 `pwnden{...}` 복구 코드를 제출하자.
::
