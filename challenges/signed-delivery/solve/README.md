## 조사 결과와 재현

같은 신뢰한 공개키와 서명으로 세 사본을 비교하면 copy-b만 통과한다.
copy-a의 도착지, copy-c의 수량은 승인된 문서와 다르다.

```sh
openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery.sig files/copy-a.txt
openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery.sig files/copy-b.txt
openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery.sig files/copy-c.txt
sha256sum files/copy-b.txt
```

검증된 원문의 SHA-256은
`ad1ef4e179bb9025f72e1742c938a7782a90ce82aea229a968ac6ef22320631d`다.
제출값은 `pwnden{ad1ef4e179bb9025f72e1742c938a7782a90ce82aea229a968ac6ef22320631d}`다.
화면에서 읽은 문장을 다시 입력하지 않고 파일 바이트 자체를 해시해야 한다.

## 드러난 원리

크기·이름·시각은 발신자의 승인 증거가 아니다. 신뢰한 키로 서명을 검증하면
바이트 변경을 구분할 수 있다. 해시만 계산해서는 발신자를 확인할 수 없으며
검증용 공개키의 전달 경로도 보호해야 한다. 서명용 개인키는 수신자에게 필요 없다.
