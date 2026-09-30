# Note Vault

분야: web · 입문

개인 메모를 보관하는 서비스다. 목록에는 내 메모만 나타나지만, 관리자의 복구 키도 같은 서비스에 저장돼 있다. `guest` 계정으로 접속해 관리자의 복구 키를 찾아라.

로그인: `guest` / `guest`. 플래그 형식은 `pwnden{...}`다.

`platform` 저장소에서 실행한다.

```sh
go run ./cmd/pwnden --repo ../challenges validate note-vault
go run ./cmd/pwnden --repo ../challenges run note-vault
```

`run`이 출력하는 `http://127.0.0.1:<port>`를 브라우저에서 연다. 호스트 포트는 Docker가 빈 포트로 정한다. 자동 풀이 컨테이너는 같은 Compose 네트워크의 `http://app:8000`으로 접속한다.

```sh
go run ./cmd/pwnden --repo ../challenges verify note-vault
go run ./cmd/pwnden --repo ../challenges stop note-vault
```

`verify`는 현재 실행의 플래그를 회수하고, 별도 패치 서비스를 시작해 같은 풀이의 실패와 정상 기능 검사의 성공을 확인한다. 패치용 컨테이너는 검증이 끝나면 제거된다. `stop`은 실행 중인 문제 서비스를 정리한다.

서비스와 풀이에는 Python 표준 라이브러리만 사용한다. Linux amd64·arm64를 포함하는 Python 이미지 index digest를 고정하며 CPU 아키텍처를 강제하지 않는다. 서비스에는 호스트 bind mount가 없다. 코드는 이미지에 복사하고 상태는 메모리에 둔다. 해설은 [solve/README.md](solve/README.md)에 있다.
