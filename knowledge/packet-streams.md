# 패킷에서 전송 자료 읽기

PCAP은 통신 패킷을 순서대로 담는 파일 형식이다. TCP는 한 자료를 여러 조각으로
전송할 수 있다. 분석기는 순서 번호로 조각을 연결해 대화를 재조립한다.
`tcp.stream`은 같은 TCP 연결을 구분하는 번호다.

`tshark -r 자료.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri`는
파일을 읽어 HTTP 요청의 연결 번호와 주소만 표시한다. `-r`은 저장된 파일을
읽으며 라이브 캡처를 시작하지 않는다. `-Y`는 표시할 패킷의 조건이다.

`mkdir objects`로 빈 폴더를 만든 뒤
`tshark -r 자료.pcap --export-objects http,objects`를 실행하면 재조립된 HTTP
전송 파일이 objects에 저장된다. 요청 주소를 봤다는 사실과 실제 파일 내용이
남아 있다는 사실은 구분해야 한다. 기록에 조각이 빠졌다면 완전한 복원이 어렵다.

`file objects/파일`은 실제 형식을 확인한다. tar.gz 파일이라면
`tar -tzf 파일.tar.gz`로 내부 경로를 나열하고
`tar -xzOf 파일.tar.gz 내부/문서.txt`로 선택한 문서 내용을 출력할 수 있다.

같은 URL에서 여러 파일을 받으면 내보낸 이름에 번호가 붙을 수 있다. 내부 영수증의
배치·버전·상태를 요구 사항과 비교해 파일을 고른다. JSON 영수증은 위 내용 출력에
`| jq .`를 붙여 읽기 좋게 표시할 수 있다. 파일명만으로 현재 버전을 판단하지 않는다.
