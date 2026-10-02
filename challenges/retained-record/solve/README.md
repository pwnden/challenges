## 목록과 실제 보관 상태

CSV에는 문서 10과 31만 있다. `.schema`를 읽으면 `documents`의 상태와
`revisions`의 변경 본문이 별도 테이블이며 문서 ID로 연결된다는 것을 확인한다.

```sh
sqlite3 -readonly files/snapshot.sqlite 'SELECT id, title, status FROM documents;'
sqlite3 -readonly files/snapshot.sqlite 'SELECT version, body FROM revisions WHERE document_id = 26 ORDER BY version DESC;'
```

문서 26은 `deleted`지만 두 버전이 남아 있다. 마지막인 버전 2에
`pwnden{hidden_rows_remain_in_backup}`이 저장돼 있다. `JOIN`으로 삭제 상태와
본문을 함께 조회하는 것도 같은 결과를 얻는 방법이다.

## 확인한 원리

목록의 필터와 저장된 본문의 보관 상태는 다르다. 이 보드는 상태만 바꿔 화면에서
숨기는 논리 삭제를 수행했다. 백업은 그 행을 보관하므로 내부 코드도 남는다.
이번 결과는 해당 백업 시점의 행에 대한 증거이며 이후 시스템의 삭제 상태를
증명하지는 않는다. 보관 정책에 맞게 본문과 백업 범위를 관리하고, 노출된 실제
복구 코드는 교체해야 한다. 본문을 제거한 대조 DB에서는 같은 조회로 코드가 나오지 않는다.
