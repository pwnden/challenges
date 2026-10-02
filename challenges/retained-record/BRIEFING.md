::message{from="도토리장"}
복구 절차 문서를 삭제했더니 목록에서는 사라졌어요. 같이 만든 백업에도 내용이 없는지 봐 주세요. 삭제했다고 안내해도 되는지 확인하고 싶어요.
::

도토리장은 팀 작업 보드의 문서를 관리한다. 보드 복구 절차에는 담당자만 보관할
코드가 있어, 일반 문서 목록에서 치우기로 했다. 삭제 버튼을 누른 뒤 목록에서는
문서가 보이지 않았고, 담당자는 본문도 제거됐다고 생각했다.

하지만 화면용 목록과 데이터베이스가 무엇을 보관하는지는 다를 수 있다.
도토리장은 같은 시점의 목록과 SQLite 백업을 길드에 맡기고, 삭제 조치 후에도
내부 복구 코드가 남았는지 조사해 달라고 요청했다. 자료는 실습용 보드에서 생성했다.

::objective
목록과 백업을 비교하고, 보드 복구 절차 문서의 마지막 승인 본문에 남은 코드를 찾자.
::

::resources{title="삭제 후 만든 백업"}
- `files/visible-documents.csv`: 화면에 표시된 문서 ID와 제목.
- `files/snapshot.sqlite`: 문서 상태와 변경된 본문을 함께 보관한 DB.
- `files/backup-note.txt`: 담당자의 조치와 조사 범위.

준비된 SQLite 도구로 원본을 읽기 전용으로 확인하자.

```sh
cat files/visible-documents.csv
cat files/backup-note.txt
sqlite3 -readonly files/snapshot.sqlite '.tables'
sqlite3 -readonly files/snapshot.sqlite '.schema'
```

문서 제목은 `Board recovery procedure`다. `publication`이 `published`면 승인된
본문이고 `draft`면 미승인 초안이다. 삭제 문서는 여럿일 수 있고 가장 큰 버전이
항상 승인본인 것은 아니다. 조사할 문서와 승인 상태를 먼저 고른 뒤 버전을 비교하자.
이번 조사는 저장된 행을 확인하며 디스크의 삭제 영역을 복구할 필요는 없다.
::

::knowledge{concepts="terminal-commands,sqlite-records"}
::

::submission
보드 복구 절차의 마지막 승인 본문에서 찾은 `pwnden{...}` 코드를 제출하자.
::
