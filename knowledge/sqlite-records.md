# SQLite의 목록과 본문

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
