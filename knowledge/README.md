# 공통 학습 개념

문제의 첫 행동에 필요한 배경을 설명하는 공통 문서다. 각 문서는 하나의
좁은 능력을 다루며, 실제 정답·공격 입력은 문제의 힌트와 해설에서 설명한다.

문제 20개의 [전체 학습 순서](../docs/learning-order.md)와 함께 사용한다.
아래 표는 개념 37개를 선수 개념이 먼저 나오도록 배열했다. 표 전체를 차례로
읽을 필요는 없고, 선택한 문제에서 필요한 개념과 그 선수 개념만 읽으면 된다.

| 개념 ID | 읽을 내용 | 먼저 읽을 개념 |
| --- | --- | --- |
| `terminal-commands` | [준비된 터미널 명령 사용하기](terminal-commands.md) | 없음 |
| `file-paths` | [폴더와 상대 경로](file-paths.md) | 없음 |
| `web-addresses` | [주소의 경로와 입력값](web-addresses.md) | 없음 |
| `base64` | [Base64 복원](base64.md) | 없음 |
| `hashing` | [해시와 비밀번호 후보](hashing.md) | 없음 |
| `candidate-cost` | [비밀번호 후보와 확인 비용](candidate-cost.md) | [해시와 비밀번호 후보](hashing.md) |
| `file-signatures` | [확장자와 파일의 실제 형식](file-signatures.md) | 없음 |
| `file-type-checks` | [파일 종류를 확인하는 근거](file-type-checks.md) | [확장자와 파일의 실제 형식](file-signatures.md) |
| `image-metadata` | [이미지와 메타데이터](image-metadata.md) | 없음 |
| `hidden-file-data` | [화면에 보이는 내용과 파일의 내용](hidden-file-data.md) | 없음 |
| `retained-data` | [공개 자료와 보관 자료의 범위](retained-data.md) | 없음 |
| `git-history` | [현재 파일과 Git 이력](git-history.md) | [준비된 터미널 명령 사용하기](terminal-commands.md), [폴더와 상대 경로](file-paths.md) |
| `sqlite-records` | [SQLite의 목록과 본문](sqlite-records.md) | 없음 |
| `historical-retention` | [과거 버전과 삭제의 의미](historical-retention.md) | [공개 자료와 보관 자료의 범위](retained-data.md) |
| `http-messages` | [Web 요청과 응답 읽기](http-messages.md) | [주소의 경로와 입력값](web-addresses.md) |
| `http-cookies` | [쿠키와 신원](http-cookies.md) | [Web 요청과 응답 읽기](http-messages.md) |
| `trusted-identity` | [서버가 확인하는 사용자 신원](trusted-identity.md) | [쿠키와 신원](http-cookies.md) |
| `object-ownership` | [자료의 소유권과 읽기 권한](object-ownership.md) | [서버가 확인하는 사용자 신원](trusted-identity.md) |
| `resource-policies` | [누가 어떤 문서를 읽을 수 있나](resource-policies.md) | [자료의 소유권과 읽기 권한](object-ownership.md) |
| `read-path-authorization` | [여러 읽기 기능의 권한 일관성](read-path-authorization.md) | [자료의 소유권과 읽기 권한](object-ownership.md) |
| `response-comparison` | [응답을 비교해 후보 줄이기](response-comparison.md) | [Web 요청과 응답 읽기](http-messages.md) |
| `response-evidence` | [응답 차이와 내용의 판단](response-evidence.md) | [응답을 비교해 후보 줄이기](response-comparison.md) |
| `tcp-services` | [포트와 TCP 연결](tcp-services.md) | [준비된 터미널 명령 사용하기](terminal-commands.md) |
| `network-trust` | [연결 가능성과 자료 읽기 권한](network-trust.md) | [포트와 TCP 연결](tcp-services.md) |
| `packet-streams` | [패킷에서 전송 자료 읽기](packet-streams.md) | [포트와 TCP 연결](tcp-services.md), [Web 요청과 응답 읽기](http-messages.md) |
| `transfer-evidence` | [자료 전달을 입증하는 기록](transfer-evidence.md) | 없음 |
| `dns-records` | [DNS 질의 기록 읽기](dns-records.md) | 없음 |
| `base32` | [Base32로 적힌 데이터](base32.md) | 없음 |
| `data-in-names` | [조회 이름에 담기는 정보](data-in-names.md) | 없음 |
| `encoding-secrecy` | [표현 변환과 정보 보호](encoding-secrecy.md) | 없음 |
| `detached-signatures` | [문서와 분리된 서명 확인하기](detached-signatures.md) | [해시와 비밀번호 후보](hashing.md) |
| `document-authenticity` | [문서 내용과 서명의 확인](document-authenticity.md) | [문서와 분리된 서명 확인하기](detached-signatures.md) |
| `path-boundaries` | [폴더 경계와 실제 파일 읽기](path-boundaries.md) | [폴더와 상대 경로](file-paths.md) |
| `query-boundaries` | [입력값과 조회 구조의 경계](query-boundaries.md) | [Web 요청과 응답 읽기](http-messages.md) |
| `curl-json` | [curl로 JSON API 읽기](curl-json.md) | [준비된 터미널 명령 사용하기](terminal-commands.md), [Web 요청과 응답 읽기](http-messages.md), [쿠키와 신원](http-cookies.md) |
| `program-reading` | [작은 입력 검사 코드 읽기](program-reading.md) | 없음 |
| `input-checks` | [입력 검사와 조건의 근거](input-checks.md) | [작은 입력 검사 코드 읽기](program-reading.md) |

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
등록부에 포함되며 위 표에서 모두 확인할 수 있다. 각 문서의 경로는 `knowledge/<id>.md`다. 문제는
`[learning].requires`와 `teaches`로 개념을 참조한다. 플랫폼에서 선수 문서를
현재 풀이 화면에서 펼쳐 읽고 연결된 선행·후속·관련 문제로 이동할 수 있다.
학습 목표는 풀이 원리가 드러날 수 있어 처음에는 접혀 있다.
