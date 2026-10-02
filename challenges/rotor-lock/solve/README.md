## 핵심: 계산을 거꾸로 실행하기

검사기는 입력을 변형한 결과를 `TARGET`과 비교한다. 사용된 연산을 반대 순서로 되돌리면
저장된 비교값에서 원래 입력을 구할 수 있다.

### 1. 바이트 하나의 변환을 정리한다

위치 `i`의 입력 바이트를 `b`, 앞선 출력 값을 `previous`라고 하자.
`mask`는 위치에 따라 계산되는 값이며, `shift`는 비트를 회전할 횟수다.

```text
mask = (0x53 + 13 * i) & 0xFF
mixed = b XOR mask XOR previous
shift = i % 7 + 1
출력 = mixed를 8비트 안에서 shift만큼 왼쪽 회전
```

`XOR`는 같은 값으로 한 번 더 연산하면 원래 값으로 돌아온다. 회전도 반대 방향으로 같은 횟수만큼 돌리면 복원된다.

### 2. 역변환한다

`TARGET[i]`를 `shift`만큼 오른쪽으로 회전해 `mixed`를 구한다. 여기에 `mask`와 `previous`를 XOR하면 `b`가 나온다.

첫 번째 출력은 `9`, 회전량은 `1`이다. 8비트 오른쪽 회전 결과는 `132`다. `132 XOR 83 XOR 167 = 112`이며, 문자로는 `p`다. 플래그의 시작과도 일치한다.

첫 바이트 이후의 `previous`는 `TARGET[i - 1]`이다. 앞선 입력을 알아야 하는 것이 아니라, 이미 있는 출력값을 사용한다.

### 3. 작업 공간에서 재현한다

준비된 풀이 터미널에서 아래 코드를 실행하면 전체 문자열을 복원한다.

```sh
python3 - <<'PY'
import runpy

target = runpy.run_path('files/checker.py')['TARGET']
previous = 0xA7
decoded = bytearray()
for i, encoded in enumerate(target):
    shift = i % 7 + 1
    mixed = ((encoded >> shift) | (encoded << (8 - shift))) & 0xFF
    decoded.append(mixed ^ ((0x53 + 13 * i) & 0xFF) ^ previous)
    previous = encoded
print(decoded.decode('utf-8'))
PY
```

복원된 플래그는 **`pwnden{rotate_then_xor_then_check}`**다. 이를 플래그 입력란에 제출하면 된다.

검사기에서도 확인하려면 같은 터미널에서 실행한다.

```sh
python3 files/checker.py 'pwnden{rotate_then_xor_then_check}'
```

`unlocked`가 출력된다. 문자열 끝에 다른 문자를 붙이면 `locked`가 나온다.

### 배운 점

복잡해 보이는 변형도 각 연산이 되돌릴 수 있는지 나누어 보면 풀린다. XOR와 회전은 값을 숨길 수 있지만, 변환 방식과 결과를 모두 공개한 이 검사에서는 비밀번호를 보호하지 못한다.
