::message{from="노을책갈피"}
문서 화면에서는 다른 사람의 내용을 막는데, 사본을 내려받는 기능도 같은지 모르겠어요. 손님 계정으로 두 기능을 비교해 주세요.
::

:person[노을책갈피]는 작은 문서 서비스의 운영 담당자다. 손님은 자신의 회의 메모를 읽고
JSON 사본으로 내려받을 수 있다. 손님은 운영 담당자의 복구 절차 문서를 읽어서는
안 된다. 그 문서에는 서비스를 복구할 때 쓰는 비밀 코드가 들어 있다.

서비스에 문서 내보내기 기능을 새로 추가했다. 문서를 일반 조회로 요청하면 서버가
다른 사람의 문서를 읽지 못하게 막는다. 하지만 내보내기 기능에서도 같은 권한을
검사하는지는 아직 확인하지 않았다.
운영자는 길드에 실습용 손님 계정과 문서 목록을 제공하고 두 작업의 차이를
확인해 달라고 요청했다. 서버와 계정은 이 문제의 격리 환경 안에서만 사용한다.

::objective
같은 문서를 일반 조회와 내보내기로 요청해 권한을 비교하고, 잘못 공개된 복구 코드를 찾자.
::

::resources{title="실습 계정과 API"}
- 터미널의 서비스 주소는 `http://app:8000`이다.
- 로그인은 `POST /api/login`, 계정은 `guest`, 비밀번호는 `lab-guest`다.
- `GET /api/catalog`는 문서의 ID·소유자·제목만 보여 준다.
- `GET /api/notes/문서ID`는 본문 조회다.
- `POST /api/exports`에 `{"note_id":문서ID}`를 보내면 기본 요약 사본을 요청한다.
- `GET /`에는 제공하는 작업과 내보내기 형식의 안내가 있다.

먼저 로그인 쿠키를 저장하고 목록과 자기 문서를 읽자.

```sh
curl -sS -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"username":"guest","password":"lab-guest"}' http://app:8000/api/login
curl -sS -b cookies.txt http://app:8000/api/catalog | jq .
curl -i -b cookies.txt http://app:8000/api/notes/7
```

자기 문서의 정상 동작을 확인한 뒤, 목록에서 다른 소유자의 문서를 골라 두 작업을
비교하자. 쿠키와 응답 파일은 문제를 종료하면 지워지는 임시 공간에 저장된다.
요약 사본은 제목·소유자만 담을 수 있다. 상태가 200이어도 실제 본문이 제공됐는지
확인하고, 형식에 따라 반환 내용과 권한 검사가 달라지는지 비교하자.
::

::knowledge{concepts="terminal-commands,http-messages,http-cookies,curl-json"}
::

::submission
잘못 허용된 내보내기의 본문에서 찾은 현재 환경의 `pwnden{...}` 복구 코드를 제출하자.
::
