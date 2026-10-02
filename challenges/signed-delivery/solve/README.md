## 조사 결과와 재현

승인 안내는 LAB-17의 버전 2와 delivery-v2.sig를 지정한다. 같은 신뢰한 공개키로
검증하면 과거 서명 delivery.sig에는 copy-b가, 현재 서명에는 copy-c가 통과한다.
copy-a는 도착지가 바뀌어 둘 다 실패한다. 유효한 과거 승인본도 현재 제출값은 아니다.

```sh
cat files/trust-note.txt
openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery-v2.sig files/copy-a.txt
openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery-v2.sig files/copy-b.txt
openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery-v2.sig files/copy-c.txt
sha256sum files/copy-c.txt
```

검증된 원문의 SHA-256은
`9db69b79d37e536f0df08a0e837861c24c94c5675b4cd6d7ffba64a5d4aba7e5`다.
제출값은 `pwnden{9db69b79d37e536f0df08a0e837861c24c94c5675b4cd6d7ffba64a5d4aba7e5}`다.
화면에서 읽은 문장을 다시 입력하지 않고 파일 바이트 자체를 해시해야 한다.

## 드러난 원리

크기·이름·시각은 발신자의 승인 증거가 아니다. 신뢰한 키로 서명을 검증하면
바이트 변경을 구분할 수 있다. 해시만 계산해서는 발신자를 확인할 수 없으며
검증용 공개키의 전달 경로도 보호해야 한다. 서명용 개인키는 수신자에게 필요 없다.
서명 성공은 해당 내용에 대한 발신자의 승인을 보여 준다. 현재 납품에 적용할
버전인지는 신뢰한 승인 안내와 대조해야 한다.
