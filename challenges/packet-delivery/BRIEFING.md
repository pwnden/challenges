::message{from="새벽전송"}
공개 안내만 보내야 하는데 내부 문서도 묶였다는 제보가 있어요. 요청 주소만 말고, 실제 전달된 파일 내용까지 확인해 주세요.
::

새벽전송은 자료 전송 서비스를 점검하는 담당자다. 테스트 수신자는 공개 안내만
받아야 한다. 내부 복구 절차와 복구 코드는 운영 담당자가 장애 대응에 쓰는
자료이며 공개 대상이 아니다.

새벽전송은 당시의 전송을 재현한 교육용 기록과 공개 목록을 길드에 전달했다.
이 PCAP은 로컬 테스트 HTTP 서버의 실제 요청·응답 바이트를 바탕으로 만든
합성 패킷이다. 실제 사용자나 외부 서버의 통신을 수집한 기록은 아니다.
HTTP 대화 두 개에 안내문과 압축 묶음의 전송이 담겨 있다. 묶음 응답은 여러
TCP 조각으로 나뉘어 있으므로 전달된 파일을 복원해 제보를 확인해야 한다.

::objective
전송 기록에서 파일을 복원하고 공개 목록과 비교해, 비공개 문서가 실제로 전달됐는지 확인하자.
::

::resources{title="전송 기록과 공개 범위"}
- `files/delivery.pcap`는 두 HTTP 연결을 담은 작은 합성 PCAP이다.
- `files/public-list.txt`는 전송 자료 중 공개 가능한 문서를 정한다.
- 저장된 파일 분석만 필요하며 새 통신이나 라이브 캡처는 필요 없다.

먼저 요청 주소를 확인하고 전송 파일을 빈 폴더에 복원하자.

```sh
tshark -r files/delivery.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri
mkdir objects
tshark -r files/delivery.pcap --export-objects http,objects
file objects/*
```

압축 묶음의 내부 경로를 확인한 뒤, 공개 목록과 다른 문서의 내용을 읽자.
파일 분석 명령의 출력은 요청 URL의 이름과 별도로 전달된 내용을 보여 준다.
::

::knowledge{concepts="terminal-commands,file-paths,packet-streams"}
::

::submission
복원한 비공개 문서에서 찾은 `pwnden{...}` 복구 코드를 제출하자.
::
