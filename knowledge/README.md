# 공통 학습 개념

문제의 첫 행동에 필요한 배경을 설명하는 공통 문서다. 각 문서는 하나의
좁은 능력을 다루며, 실제 정답·공격 입력은 문제의 힌트와 해설에서 설명한다.

| 개념 ID | 읽을 내용 |
| --- | --- |
| `http-messages` | [요청·응답과 상태](http-messages.md) |
| `http-cookies` | [쿠키와 신원](http-cookies.md) |
| `web-addresses` | [주소와 입력값](web-addresses.md) |
| `file-paths` | [폴더와 상대 경로](file-paths.md) |
| `terminal-commands` | [준비된 터미널 명령](terminal-commands.md) |
| `hashing` | [해시와 후보 대입](hashing.md) |
| `file-signatures` | [확장자와 식별 바이트](file-signatures.md) |
| `dns-records` | [DNS 기록 읽기](dns-records.md) |
| `base32` | [Base32 복원](base32.md) |
| `resource-policies` | [누가 어떤 문서를 읽을 수 있나](resource-policies.md) |
| `image-metadata` | [이미지와 메타데이터](image-metadata.md) |
| `git-history` | [현재 파일과 Git 이력](git-history.md) |
| `sqlite-records` | [SQLite의 목록과 본문](sqlite-records.md) |
| `curl-json` | [curl로 JSON API 읽기](curl-json.md) |
| `tcp-services` | [포트와 TCP 연결](tcp-services.md) |
| `response-comparison` | [응답을 비교해 후보 줄이기](response-comparison.md) |
| `packet-streams` | [패킷에서 전송 자료 읽기](packet-streams.md) |
| `detached-signatures` | [문서와 분리된 서명 확인하기](detached-signatures.md) |

기본 브리핑은 문제의 상황과 자료를 소개한다. 공통 개념은 `[learning]` 관계를
통해 학습 연결에서 선택해 읽는다. 개념 문서는 문제와 독립된 원리와 예시를 다룬다.

필수 배경을 본문에 포함할 때는 `BRIEFING.md`의 아래 블록을 사용할 수 있다.
`python3 tools/content.py`가 배포용 `README.md`로 컴파일한다.

```md
::knowledge{concepts="http-messages,http-cookies"}
::
```

`--concept` 옵션을 반복해서 생성기에 전달하면 본문 연결과 `[learning].requires`가
함께 생성된다. `--requires`와 `--teaches`는 관계 선언만 추가한다.
원문과 생성 결과의 일치는 validator와 verifier가 검사한다.

계약 v7의 [catalog.toml](catalog.toml)이 37개 개념의 ID, 제목, 선수 개념과 관련
개념을 관리한다. 위 표는 시작 지식 문서이며, 같은 폴더의 학습 목표 문서도
등록부에 포함된다. 각 문서의 경로는 `knowledge/<id>.md`다. 문제는
`[learning].requires`와 `teaches`로 개념을 참조한다. 플랫폼에서 선수 문서를
현재 풀이 화면에서 펼쳐 읽고 연결된 선행·후속·관련 문제로 이동할 수 있다.
학습 목표는 풀이 원리가 드러날 수 있어 처음에는 접혀 있다.
