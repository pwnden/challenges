::message{from="moru17"}
백업 장치의 비밀번호를 잊어버렸어요. 예전에 쓰던 비밀번호 여섯 개와 장치의 로그인 기록은 남아 있어요. 어떤 비밀번호가 맞는지 찾아 줄래요?
::

:person[moru17]은 파일을 보관하던 오래된 백업 장치에 다시 로그인하려고 한다.
비밀번호가 기억나지 않아, 예전에 쓰던 값 여섯 개를 메모에서 찾아 보냈다.
장치에는 비밀번호를 확인할 때 사용하는 계정 정보도 남아 있다.

계정 정보에는 비밀번호 글자 대신 **해시**라는 계산 결과가 저장돼 있다.
같은 비밀번호를 같은 방식으로 계산하면 같은 결과가 나오므로, 후보를 하나씩 계산해
저장된 값과 비교할 수 있다. 계산 방식은 SHA-256이며 필요한 명령은 아래에 준비돼 있다.
여섯 후보 중 어느 것이 이 계정의 비밀번호인지 확인해 보자.

::objective
기록의 해시와 일치하는 비밀번호를 찾아 제출하자.
::

::resources{title="전달받은 자료"}
- `files/account.txt`: 계정 이름, 해시 방식과 저장된 비밀번호 해시.
- `files/candidates.txt`: 후보 비밀번호 여섯 개.

터미널에서 `cat files/account.txt`, `cat files/candidates.txt`로 자료를 읽을 수 있다.
후보 하나의 SHA-256은 아래 명령의 `후보`를 실제 값으로 바꿔 확인한다.
출력 왼쪽의 64글자를 account.txt의 password_hash와 비교하자.

```sh
printf '%s' '후보' | sha256sum
```
::

::knowledge{concepts="terminal-commands,hashing"}
::

::submission
찾은 비밀번호를 `pwnden{비밀번호}`로 감싸 제출하자. 예를 들어 비밀번호가
`sample42`라면 제출 형태는 `pwnden{sample42}`다.
::
