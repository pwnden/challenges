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
목록과 백업의 보관 상태를 비교하고, 삭제 상태 문서의 마지막 본문에 남은 복구 코드를 찾자.
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

문서 상태와 본문의 연결 열, 버전 순서를 확인한 뒤 필요한 행을 조회할 수 있다.
이번 조사는 저장된 행을 확인하며 디스크의 삭제 영역을 복구할 필요는 없다.
::

::knowledge

### 준비된 터미널 명령 사용하기

터미널에는 한 줄의 명령을 입력하고 Enter를 누르면 된다. `files/`로 시작하는
경로는 이 문제의 배포 파일을 가리킨다. 명령 예제의 파일명은 조사할 자료의 이름으로 바꿔 넣자.

`printf '%s' 'hello'`는 줄바꿈 없이 `hello`를 출력한다.
`|`는 왼쪽 출력물을 오른쪽 프로그램의 입력으로 전달한다.
예를 들어 `printf '%s' 'hello' | sha256sum`은 정확히 다섯 글자를 해시한다.
`hello` 뒤에 줄바꿈이 추가되면 해시도 달라진다.

파일을 읽는 명령과 결과를 확인하는 명령은 문제의 전달받은 자료에 제공한다.
Ctrl+C는 오래 실행되는 명령을 중단하고, 위쪽 화살표는 이전 명령을 다시 가져온다.

### SQLite의 목록과 본문

SQLite 파일에는 표인 테이블이 들어 있다. 각 행은 문서나 변경 버전 같은 기록이며,
열은 ID·제목·상태·본문처럼 그 기록의 속성이다. 화면의 목록이 일부 행만 보여 주더라도
원본 테이블에는 더 많은 행이 남아 있을 수 있다.

`sqlite3 -readonly DB파일 '.tables'`는 테이블 이름을,
`sqlite3 -readonly DB파일 '.schema'`는 열과 연결 정보를 읽는다. `-readonly`는
원본을 읽기 전용으로 연다. 조회도 작은따옴표 안에 입력한다.

```sh
sqlite3 -readonly 예제.sqlite 'SELECT id, title FROM documents WHERE status = "active";'
```

`SELECT`는 읽을 열, `FROM`은 테이블, `WHERE`는 조건을 지정한다. 두 테이블의
연결은 `JOIN revisions AS r ON r.document_id = d.id`처럼 연결 열을 비교한다.
`AS d`와 `AS r`는 짧은 별칭이다. `ORDER BY r.version DESC`는 큰 버전부터,
`LIMIT 1`은 첫 행만 읽는다. 실제 테이블과 열은 `.schema` 결과에서 확인한다.
::

::submission
삭제 상태 문서의 마지막 본문에서 찾은 `pwnden{...}` 복구 코드를 제출하자.
::
