# 시작 지식 문서

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

작성자는 `BRIEFING.md`에 아래 블록을 둔다. `python3 tools/content.py`가
공통 문서를 기존 `::knowledge` 블록으로 묶어 배포용 `README.md`에 반영한다.
플레이어는 사이트의 문제 본문에서 읽고 현재 작업 공간을 계속 사용한다.

```md
::knowledge{concepts="http-messages,http-cookies"}
::
```

`--concept` 옵션을 반복해서 생성기에 전달하면 이 연결이 자동 생성된다.
원문과 생성 결과의 일치는 기존 validator와 verifier가 검사한다.
관계와 원본은 작성 자료에 남으며, 배포는 현재 계약 v5의 Markdown을 사용한다.
