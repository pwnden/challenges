## 조사 결과와 재현

세 HTTP 요청 중 /notice.txt는 안내이고 /delivery.tar.gz는 두 번 내려온다.
URL은 같지만 public/receipt.json의 버전은 다르다. 첫 묶음은 폐기된 버전 1이다.
TShark가 여러 TCP 조각을 재조립하면 전달된 압축 묶음을 읽을 수 있다.

```sh
tshark -r files/delivery.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri
mkdir objects
tshark -r files/delivery.pcap --export-objects http,objects
file objects/*
for object in objects/*; do
  tar -xzOf "$object" public/receipt.json 2>/dev/null | jq .
done
```

공개 목록이 요구하는 LAB-17의 승인 버전 2에 해당하는 파일을 골라
`tar -xzOf 선택한파일 internal/recovery.txt`를 실행한다. 복원 시 중복 이름은
번호가 붙으므로 파일명만 고정해 선택하지 않는다.
묶음에는 공개 안내 외에도 `internal/recovery.txt`가 있다. 공개 목록은 그 복구
절차와 코드를 담당자 전용으로 정한다. 복원한 문서에는
`pwnden{tcp_reassembles_the_delivery}`가 있으며 이 값을 제출한다.
요청된 이름이나 응답 상태만 추측한 것이 아니라 실제 전달된 바이트로 확인했다.

## 드러난 원리

암호화되지 않은 HTTP 전송이 완전한 캡처에 남으면 재조립해 본문을 읽을 수 있다.
압축은 비밀 보호를 제공하지 않는다. 서버는 수신자의 권한에 맞는 자료만 묶어
보내고, 전송 경로에서도 적절한 기밀성 보호를 사용해야 한다. 이 문제는
교육용 합성 기록을 오프라인으로 분석하므로 캡처 권한이 필요하지 않다.
