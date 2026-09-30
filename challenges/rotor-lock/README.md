# Rotor Lock

분야: rev · 입문

잠금장치의 입력 검사 코드를 얻었다. 각 바이트는 위치와 앞선 결과에 따라 다른 값으로 바뀐다. 검사기를 분석해 잠금장치를 여는 입력을 찾아라.

배포 파일은 [`files/checker.py`](files/checker.py) 하나다. Python 3로 실행한다.

```text
python3 checker.py <flag>
```

정답이면 `unlocked`와 종료 코드 0, 오답이면 `locked`와 종료 코드 1을 반환한다. 플래그 형식은 `pwnden{...}`다. 호스트 CPU에 종속된 바이너리는 없다.

`platform` 저장소에서 실행한다.

```sh
go run ./cmd/pwnden --repo ../challenges validate rotor-lock
go run ./cmd/pwnden --repo ../challenges verify rotor-lock
```

풀이 검증은 고정된 Python 컨테이너에서 실행된다. 파일형이므로 서비스 시작은 필요 없다. 해설은 [solve/README.md](solve/README.md)에 있다.
