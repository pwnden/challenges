## 조사 결과와 재현

두 HTTP 요청 중 `/notice.txt`는 공개 안내이고 `/delivery.tar.gz`는 압축 묶음이다.
TShark가 여러 TCP 조각을 재조립하면 전달된 압축 묶음을 읽을 수 있다.

```sh
tshark -r files/delivery.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri
mkdir objects
tshark -r files/delivery.pcap --export-objects http,objects
file objects/delivery.tar.gz
tar -tzf objects/delivery.tar.gz
tar -xzOf objects/delivery.tar.gz internal/recovery.txt
```

묶음에는 공개 안내 외에도 `internal/recovery.txt`가 있다. 공개 목록은 그 복구
절차와 코드를 담당자 전용으로 정한다. 복원한 문서에는
`pwnden{tcp_reassembles_the_delivery}`가 있으며 이 값을 제출한다.
요청된 이름이나 응답 상태만 추측한 것이 아니라 실제 전달된 바이트로 확인했다.

## 드러난 원리

암호화되지 않은 HTTP 전송이 완전한 캡처에 남으면 재조립해 본문을 읽을 수 있다.
압축은 비밀 보호를 제공하지 않는다. 서버는 수신자의 권한에 맞는 자료만 묶어
보내고, 전송 경로에서도 적절한 기밀성 보호를 사용해야 한다. 이 문제는
교육용 합성 기록을 오프라인으로 분석하므로 캡처 권한이 필요하지 않다.
