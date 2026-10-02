::message{from="moru17"}
백업 계정의 비밀번호 원문은 없어졌는데, 저장된 해시와 예전에 쓰던 후보 목록은 있어요. 이 두 자료만으로 비밀번호를 알아낼 수 있는지 봐 주세요.
::

moru17은 오래된 백업 장치를 다시 연결하려고 한다. 장치는 로그인 확인에 쓰던 계정 기록을
남겨 두었지만, 거기에는 비밀번호의 SHA-256 해시만 들어 있다.
메모에서 찾은 후보 비밀번호는 여섯 개다.

계정 기록에는 사용한 해시 방식과 추가 값인 salt의 사용 여부가 적혀 있다.
이번 의뢰는 후보와 기록을 비교해 원래 비밀번호를 확인하는 일이다.
준비된 해시 명령을 사용하면 후보의 결과를 직접 관찰할 수 있다.

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
