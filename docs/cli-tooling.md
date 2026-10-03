# 해킹 실습용 CLI 도구 목록과 도입 기준

조사일: 2026-10-02.

주요 해킹·워게임 CLI와 실제 분석에 필요한 기본 명령을 용도별로 정리한다.
각 도구의 모든 플러그인과 공격 모드를 지원한다는 뜻은 아니다.
도구의 기능은 공식 문서·저장소에서 확인했고, 추가 가능성은 현재
[계약](contract.md), [실행 범위](execution-feasibility.md), 실제 도구 컨테이너
실행 옵션을 바탕으로 판단했다. 표는 도구별 실습 방식·실행 제약·준비 사항을 제시한다.

현재 제공 기준은 문제의 학습 목표와 실제 풀이에 필요한 CLI다.
[8개 CLI 문제](cli-challenge-plan.md)는 7개에 `basic`, PCAP 문제 1개에
basic에 `tshark`를 추가한 `pcap`을 사용한다. 이 목록은 추가 도구를 고를 때
참고하는 후보 목록이며, 모든 문제에 모든 도구를 설치하는 요구 사항이 아니다.
구성·버전·사용법과 검증 결과는 [CLI 이미지](../images/cli/README.md)에 있다.

아래 판정은 도입 시 확인할 사용 방식이다. 94개 항목의 모든 기능이 검증됐다는
뜻은 아니다. 설치 여부와 실제 기능 검증, 실행 권한은 구분한다. 현재 비특권
사용자·작업 공간·자원 상한은 [runtime limits](verification.md#runtime-limits)를
따른다. 추가 설치를 위해 실행기의 권한·장치·통신 범위를 넓히지는 않았다.

## 판정 읽기

| 판정 | 의미 |
| --- | --- |
| 후보 | 파일 처리 또는 일반 사용자 공간 통신으로 구성할 수 있는 실습 후보. 설치된 이미지에서도 문제별 실제 명령과 풀이를 검증한다. |
| 모드 한정 | 도구 중 현재 정책에 맞는 기능만 후보. 인터넷·원시 패킷·장치 접근이 필요한 다른 모드는 함께 제공 가능한 기능으로 취급하지 않는다. |
| 검증 필요 | 디버깅, 특수 런타임, 복잡한 서비스, 자원 또는 아키텍처에 대한 실행 증거가 먼저 필요하다. |
| 범위 밖 | 명시한 사용 방식이 현재 호스트·장치·권한·외부 통신 제약과 맞지 않는다. |

모든 후보에는 다음 공통 조건이 적용된다.

- 풀이 도구는 컨테이너에 미리 설치되어 제공된다. 문제를 풀기 위해 사용자가 `apt`, `pip`, `npm` 설치를 수행할 필요가 없다.
- 서비스 문제의 도구는 같은 문제의 격리 네트워크만 사용한다. 파일 문제의 도구에는 네트워크가 없다.
- 인터넷·호스트·다른 문제에 대한 통신, 저장소 밖 호스트 마운트, Docker 소켓, 장치와 추가 capabilities를 허용하지 않는다.
- 파일 생성·추출·캐시는 컨테이너 안에 둔다. 문제 원본은 읽기 전용이고, 쓰기 허용 문제는 명령·터미널이 공유하는 256MiB 임시 복사본을 사용한다. 환경 종료 때 복사본과 생성한 파일을 지운다.
- 데이터베이스·서명 키·단어 목록·플러그인·심볼·규칙·템플릿은 필요한 것을 준비 단계에 포함한다. 런타임의 자동 업데이트·외부 API·원격 검증이 풀이의 전제가 되지 않도록 한다.
- Python·Ruby·Java 등 도구 내부의 실행 환경은 이미지가 제공한다. 도구 사용에 해당 언어로 프로그램을 작성하는 능력이 필요한지는 별도의 선수 지식으로 판단한다.

## 1. 기본 탐색·파일·텍스트

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| `bash`, `bash-completion` | 셸 명령, 파이프, 리다이렉션, 자동완성 | 후보 | 현재 셸 동작을 유지하고 제공 명령의 completion 자료를 포함한다. |
| `ls`, `find`, `cat`, `head`, `tail`, `less`, `grep`, `rg`, `sed`, `awk`, `sort`, `uniq`, `cut`, `tr`, `wc`, `diff` | 파일·로그 탐색과 문자열 비교 | 후보 | 기본 명령 묶음. 로컬 파일만 사용한다. |
| `file` | 확장자와 실제 파일 형식 비교 | 후보 | libmagic 자료를 포함한다. |
| `strings` | 실행 파일·덤프에서 읽을 수 있는 문자열 추출 | 후보 | Binutils의 실제 문자열 분석 명령. |
| `xxd`, `od`, `hexdump` | 바이트·16진수 확인 | 후보 | 동일 파일의 문자와 바이트 표현을 비교한다. |
| `base64`, `basenc` | 데이터 표현 변환 | 후보 | 암호화와 인코딩의 차이를 실습한다. |
| `sha256sum`, `sha512sum`, `md5sum`, `b2sum` | 파일·후보 문자열의 해시 비교 | 후보 | 사용 알고리즘의 목적과 한계를 설명한다. |
| `tar`, `unzip`, `7zz`, `gzip`, `xz`, `zstd` | 압축 자료 목록 확인·해제 | 후보 | 추출 결과는 별도 작업 경로에 둔다. |
| [`jq`](https://jqlang.org/manual/), [`yq`](https://github.com/mikefarah/yq) | JSON·YAML 등 구조화된 자료 탐색 | 후보 | 확장 이미지의 `yq`는 Mike Farah 구현이며 동명의 Python 프로그램과 구분한다. |
| `sqlite3` | 배포된 데이터베이스의 테이블·레코드 조사 | 후보 | 원본 DB의 분석과 수정할 복사본을 구분한다. |
| `git` | 로컬 변경 이력·삭제된 파일·과거 설정 조사 | 후보 | 실습용 이력을 문제 자료로 포함한다. 호스트 저장소·인증 정보와 연결하지 않는다. |

이 기본 명령은 명령마다 별도 보안 취약점을 만드는 것이 아니라, 여러 실습에서 관찰·비교·추출에 공통 사용한다.

## 2. HTTP·웹 탐색·요청 실험

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`curl`](https://curl.se/docs/manpage.html) | HTTP 헤더·쿠키·메서드·본문 변경, 응답 비교 | 후보 | 가장 먼저 제공할 웹 CLI. 현재 문제 주소만 사용한다. |
| `wget`, `http`(HTTPie) | 자료 요청·읽기 쉬운 HTTP 요청 | 후보 | 확장 이미지에 모두 포함한다. 문제의 요청·응답을 직접 비교한다. |
| [`ffuf`](https://github.com/ffuf/ffuf) | URL 경로·파라미터·가상 호스트 후보를 바꿔 응답 차이 찾기 | 후보 | 짧은 문제별 단어 목록과 제한된 요청량을 제공한다. |
| [`gobuster`](https://github.com/OJ/gobuster) | 경로·DNS·가상 호스트 후보 탐색 | 모드 한정 | 웹 경로는 같은 문제 사이트, DNS는 문제의 DNS 서버를 대상으로 한다. |
| [`feroxbuster`](https://github.com/epi052/feroxbuster) | 경로를 재귀적으로 탐색 | 후보 | 깊이·동시 요청·시간을 제한한다. `ffuf`와 겹치는 기능은 대안으로 둔다. |
| [`whatweb`](https://github.com/urbanadventurer/WhatWeb), [`httpx`](https://github.com/projectdiscovery/httpx) | 서버 응답·기술·서비스 정보 조사 | 모드 한정 | HTTPx는 ProjectDiscovery 도구다. 문제의 대상 목록과 로컬 관찰만 사용한다. |
| [`katana`](https://github.com/projectdiscovery/katana) | 페이지 링크·경로 수집 | 모드 한정 | 일반 HTTP 크롤링 후보. 외부 링크 추적은 범위를 벗어나며 headless 브라우저 모드는 별도 검증한다. |
| [`nikto`](https://github.com/sullo/nikto) | 웹 서버의 노출된 파일·설정 탐색 | 후보 | 검사 자료를 미리 포함하고 자동 업데이트를 풀이 조건으로 두지 않는다. |
| [`sqlmap`](https://github.com/sqlmapproject/sqlmap) | SQL 인젝션 탐지·취약한 조회의 데이터 확인 | 모드 한정 | 해당 문제의 DB·사이트를 대상으로 한다. 먼저 직접 요청으로 취약 원리를 관찰하고 자동화 결과와 비교하는 실습에 적합하다. |
| [`nuclei`](https://docs.projectdiscovery.io/opensource/nuclei/running) | 정해진 템플릿으로 노출·취약 응답 검사 | 모드 한정 | 고정된 로컬 템플릿을 제공한다. 업데이트 확인과 외부 Interactsh를 끈다. Headless·코드 실행 등은 별도 검증한다. |
| [`jwt_tool.py`](https://github.com/ticarpi/jwt_tool) | JWT 내용·서명·검증 규칙 실험 | 모드 한정 | 문제의 토큰·로컬 대상·관련 키 자료만 제공한다. |
| [`testssl.sh`](https://github.com/testssl/testssl.sh), `sslscan` | TLS 인증서·프로토콜·암호군 조사 | 후보 | 같은 문제의 실제 TLS 서버를 준비한다. |

Nuclei 공식 문서는 `-duc`(업데이트 확인 중단)과 `-ni`(외부 Interactsh 사용 중단)를 제공한다.
이를 준비된 실행 설정에 반영해도 격리 정책 검증은 별도로 수행한다.
외부 콜백 자체가 학습 목표라면 같은 문제 안의 실제 콜백 서비스를 준비해야 하며, 인터넷 콜백을 지원한다고 취급하지 않는다.

## 3. 포트·프로토콜·서비스 탐색

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`nmap`](https://nmap.org/book/man-port-scanning-techniques.html) | 열린 포트·서비스 조사 | 모드 한정 | 일반 TCP 연결 스캔(`-sT`)과 서비스 조사 후보. `--unprivileged`, `-Pn`, `-n`을 포함한 실제 명령을 검증한다. SYN·OS 탐지 등 raw 모드는 현재 권한으로 제공하지 않는다. |
| `rustscan` | TCP 포트를 빠르게 찾고 조사 도구에 연결 | 모드 한정 | 동시 연결 수와 후속 Nmap 모드를 지정해야 한다. 첫 포트 탐색 도구는 Nmap을 우선한다. |
| [`ncat`](https://nmap.org/ncat/), `nc`(netcat) | TCP/UDP로 직접 데이터를 주고받기 | 후보 | 확장 이미지에 Ncat과 OpenBSD netcat을 포함한다. 문제 설명에서 구현별 옵션을 구분한다. |
| `socat` | 소켓·스트림 연결과 프로토콜 실험 | 모드 한정 | 사용자 공간의 같은 문제 안 연결. 호스트 장치·외부 터널은 사용 범위 밖이다. |
| `dig`, `host`, `nslookup`, [`dnsrecon`](https://github.com/darkoperator/dnsrecon) | DNS 레코드·이름·구역 전송 조사 | 모드 한정 | 실제 문제 DNS 서버를 명시한다. 공개 DNS와 외부 자산 수집을 전제로 하지 않는다. |
| `openssl s_client` | TLS 서비스와 직접 대화·인증서 확인 | 후보 | 문제 서버와 실습용 신뢰 자료를 제공한다. |
| `ssh`, `scp`, `sftp` | 실제 문제의 SSH 인증·파일 권한 조사 | 모드 한정 | SSH 서버도 문제 서비스로 준비한다. 호스트 키·호스트 SSH 에이전트는 제공하지 않는다. |
| `lftp`, `ftp`, `telnet` | FTP·텍스트 프로토콜 서비스 조사 | 후보 | 제공할 클라이언트 구현과 실제 문제 서비스를 검증한다. |
| [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) | SMB 공유·권한·자료 탐색 | 검증 필요 | 클라이언트 기능과 실제 비특권 SMB 서비스 시작을 함께 검증한다. |
| `snmpwalk`, `snmpget` | SNMP가 노출하는 관리 정보 조사 | 후보 | 같은 문제 네트워크의 실제 UDP 서비스만 사용한다. |
| [`ldapsearch`](https://www.openldap.org/software/man.cgi?query=ldapsearch) | LDAP 디렉터리와 조회 권한 조사 | 후보 | 문제 안의 실제 LDAP 서버와 데이터를 제공한다. |
| [`redis-cli`](https://redis.io/docs/latest/develop/tools/cli/), [`psql`](https://www.postgresql.org/docs/current/app-psql.html), `mysql`/`mariadb` | 서비스 인증·조회·권한 실험 | 후보 | 실제 문제 DB와 해당 버전의 클라이언트를 준비한다. |
| `ss`, `ip` | 컨테이너 내부 소켓·인터페이스 상태 확인 | 모드 한정 | 조회 기능만 후보. 라우팅·인터페이스 변경은 현재 권한 밖이다. |
| `ping`, `traceroute`, `tracepath` | 연결·경로 관찰 | 검증 필요 | ICMP 소켓·raw 모드·비특권 UDP 방식이 다르다. 도구 전체의 사용 가능성을 일괄 약속하지 않는다. |

Nmap은 관리자 권한 없이 TCP `connect()`로 스캔하는 모드를 공식 제공한다.
[`--unprivileged`](https://nmap.org/book/man-misc-options.html)는 컨테이너의 UID가 root여도
raw 권한이 있다고 가정하지 않도록 하는 설정 후보다. 실제 기능 판정은 준비된 이미지에서 확인한다.
포트 발견 문제는 대상 주소를 제공하되, 찾아야 하는 포트나 서비스의 정답을 먼저 나열하지 않도록 작성한다.

## 4. 파일·문서·이미지 포렌식

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`exiftool`](https://github.com/ExifTool/exiftool) | 사진·문서 등의 메타데이터 조사 | 후보 | 개인정보 대신 실습용으로 작성한 위치·작성자·시간 자료를 사용한다. |
| [`binwalk`](https://github.com/ReFirmLabs/binwalk) | 바이너리·펌웨어의 포함 자료 조사·추출 | 모드 한정 | 필요한 추출기와 정확한 버전을 함께 준비하고 컨테이너 내부 복사본에서 추출한다. |
| `unsquashfs`, `dtc` | 파일시스템·장치 트리 자료 해석 | 후보 | 실제 배포 이미지 파일을 사용자 공간에서 분석한다. 장치 마운트가 필요하지 않은 경로를 검증한다. |
| `pdfinfo`, `pdftotext`, [`qpdf`](https://qpdf.readthedocs.io/en/stable/cli.html), `mutool` | PDF 구조·본문·포함 자료 조사 | 후보 | 필요한 기능 한두 개부터 묶고 출력 파일의 작업 경로를 준비한다. |
| [`oleid`, `olevba`(oletools)](https://github.com/decalage2/oletools) | Office 문서 구조·매크로 조사 | 후보 | 파일 분석만 제공한다. 실제 Office 앱에서 실행하는 실습과 구분한다. |
| `pngcheck`, [`zsteg`](https://github.com/zed-0xff/zsteg) | PNG/BMP 구조·숨겨진 자료 탐색 | 후보 | 파일 크기와 탐색 비용을 제한한다. |
| `steghide`, [`stegseek`](https://github.com/RickdeJager/stegseek) | 이미지 등에 숨긴 데이터 추출·짧은 암호 후보 조사 | 후보 | 고정된 작은 사전과 실제 작성한 파일을 제공한다. |
| `foremost`, `scalpel` | 파일 조각과 시그니처로 자료 복구 | 후보 | 디스크 이미지 파일의 컨테이너 내부 분석. 추출 용량과 출력 위치를 제한한다. |
| [`mmls`, `fsstat`, `fls`, `icat`(Sleuth Kit)](https://www.sleuthkit.org/sleuthkit/man/) | 파티션·파일시스템·삭제 자료 조사 | 후보 | 파일형 이미지에서 사용자 공간 분석. loop 장치·호스트 디스크 접근은 범위 밖이다. |
| `bulk_extractor` | 이미지·자료 묶음에서 유의미한 패턴 추출 | 검증 필요 | 메모리·출력 용량·시간을 측정한 전용 자료가 필요하다. |
| [`vol`/`vol.py`(Volatility 3)](https://github.com/volatilityfoundation/volatility3) | 메모리 덤프의 프로세스·파일·네트워크 흔적 조사 | 검증 필요 | 실제 덤프에 맞는 심볼과 캐시를 미리 제공하고 RAM 비용을 확인한다. 실시간 호스트 메모리 수집을 제공하지 않는다. |

## 5. 패킷 자료 분석

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`tshark`](https://www.wireshark.org/docs/man-pages/tshark.html) | PCAP의 HTTP·DNS·TCP 정보 추출·대화 재구성 | 모드 한정 | `-r`로 제공된 실제 캡처 파일을 읽는 경로를 검증한다. 라이브 캡처와 구분한다. |
| `capinfos`, `editcap`, `mergecap` | 캡처의 시간·구조 확인, 분리·병합 | 후보 | Wireshark CLI 도구를 캡처 파일 분석용으로 포함한다. |
| `tcpdump` | 패킷 요약·필터링 | 모드 한정 | 파일 읽기 모드를 검증한다. 컨테이너의 root 여부와 권한 전환 동작도 확인한다. 라이브 캡처는 범위 밖이다. |
| `termshark`, `tcpflow` | 터미널에서 캡처 탐색·스트림 자료 추출 | 모드 한정 | PCAP 파일만 대상으로 하는 실행 경로와 TUI·출력 파일 동작을 확인한다. |

TShark는 공식적으로 `-r <infile>`을 제공한다. 캡처 자료 분석이 가능하다는 사실은
현재 권한으로 라이브 패킷 캡처도 가능하다는 뜻이 아니다.

## 6. 해시·암호·인증 시험

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`openssl`](https://docs.openssl.org/master/man1/openssl/), `gpg` | 암호화·복호화·해시·키·서명 확인 | 후보 | 실습용 키와 알고리즘을 지정하고 외부 키 서버 없이 사용한다. |
| [`hashid`](https://github.com/psypanda/hashID) | 해시 형태의 후보를 조사 | 후보 | 형태는 알고리즘의 확정 증거가 아님을 문제에서 구분한다. |
| [`john`(John the Ripper Jumbo)](https://www.openwall.com/john/) | 주어진 해시의 작은 암호 후보 비교 | 후보 | CPU 기준의 짧고 재현 가능한 실습을 우선한다. Jumbo와 기본 패키지의 지원 형식 차이를 고정한다. |
| `zip2john`, `ssh2john`, `office2john` | 배포 자료를 John이 읽는 형태로 변환 | 후보 | 선택한 Jumbo 버전과 실행 환경을 함께 제공한다. |
| [`hashcat`](https://hashcat.net/wiki/doku.php?id=frequently_asked_questions) | 여러 해시 형식의 후보 시험 | 검증 필요 | CPU backend와 아키텍처·자원 비용을 검증한다. GPU 장치 제공 방식은 현재 범위 밖이다. |
| `crunch`, `cewl` | 규칙이나 문제 사이트에서 작은 단어 목록 만들기 | 후보 | 전체 공간을 무작정 생성하는 대신 제한된 학습 자료와 출력 상한을 둔다. |
| [`hydra`](https://github.com/vanhauser-thc/thc-hydra), [`ncrack`](https://nmap.org/ncrack/) | 서비스의 인증·시도 제한·계정 후보 시험 | 모드 한정 | 문제의 실제 인증 서비스, 작은 후보 목록과 지원 프로토콜 모듈을 검증한다. |
| [`RsaCtfTool`](https://github.com/RsaCtfTool/RsaCtfTool) | 약한 RSA 키·자료 조사 | 검증 필요 | 필요한 수학 런타임·키·CPU 비용을 먼저 검증한다. 무거운 선수 지식은 심화 문제로 명시한다. |
| [`aircrack-ng`](https://www.aircrack-ng.org/doku.php?id=aircrack-ng) | 제공된 무선 교환 자료의 작은 암호 후보 시험 | 모드 한정 | 실제 제공 캡처를 오프라인 분석하는 실습. 무선 장치·라이브 수집을 제공하지 않는다. |

Hashcat은 CPU 실행에도 backend 준비가 필요하다. CPU로 실행 가능한 형태를 실제로
확인하기 전에는 단순히 패키지를 설치했다는 이유로 사용 가능 판정을 내리지 않는다.

## 7. 바이너리 정적 분석·익스플로잇 준비

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`readelf`, `objdump`, `nm`, `objcopy`, `addr2line`(Binutils)](https://sourceware.org/binutils/docs/binutils/) | 실행 파일 형식·섹션·심볼·명령어 조사 | 후보 | 분석 대상 아키텍처와 도구가 지원하는 형식을 확인한다. |
| [`checksec`](https://github.com/slimm609/checksec) | 실행 파일의 보호 기법 조사 | 후보 | 선택 구현·버전의 실제 파일 검사 명령을 제공한다. |
| `patchelf`, `scanelf` | ELF 로더·연결·속성 조사와 파일 실험 | 후보 | 파일 수정은 컨테이너 내부 복사본에서 한다. |
| [`radare2`](https://github.com/radareorg/radare2), [`rizin`](https://github.com/rizinorg/rizin) | 대화형 정적 분석·디스어셈블 | 모드 한정 | 확장 이미지에 두 도구를 포함한다. 정적 분석을 검사했고 동적 디버깅 기능은 아래 검증을 따른다. |
| [`ROPgadget`](https://github.com/JonathanSalwan/ROPgadget), [`ropper`](https://github.com/sashs/Ropper) | 바이너리에서 짧은 명령어 조각 조사 | 후보 | 지원 형식·명령어 집합과 실제 파일을 함께 검증한다. |
| [`pwn cyclic`, `pwn checksec`, `pwn asm`, `pwn disasm`(pwntools CLI)](https://github.com/Gallopsled/pwntools) | 패턴·파일 보호·기계어 변환 실험 | 모드 한정 | CLI 경로를 준비하고 필요한 assembler를 포함한다. Python으로 exploit을 작성해야 하는 단계는 별도의 선수 지식이다. |
| [`analyzeHeadless`(Ghidra)](https://github.com/NationalSecurityAgency/ghidra) | 자동 정적 분석·디컴파일 | 검증 필요 | Java·메모리·시작 비용을 검증한다. GUI를 터미널에 제공하는 도구로 취급하지 않는다. |
| [`yara`](https://github.com/VirusTotal/yara), [`capa`](https://github.com/mandiant/capa), [`floss`](https://github.com/mandiant/flare-floss) | 파일 패턴·기능·난독화된 문자열 조사 | 후보 | 해당 파일 형식에 필요한 엔진과 고정된 로컬 규칙을 준비한다. 파일별 분석 비용을 검증한다. |

## 8. 디버깅·추적·퍼징

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`gdb`](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Starting.html), `lldb` | 프로세스 실행·중단·메모리·레지스터 관찰 | 검증 필요 | 같은 컨테이너에서 대상 자식 프로세스를 시작하는 실제 경로를 검사한다. ptrace·seccomp·ASLR·아키텍처를 함께 검증한다. |
| [`pwndbg`](https://github.com/pwndbg/pwndbg), [`GEF`](https://github.com/hugsy/gef) | 디버거의 메모리·스택·힙 관찰 지원 | 검증 필요 | 확장 이미지에 `pwndbg`, `gdb-gef`를 포함하고 자식 프로세스의 중단·관찰을 검사했다. 문제별 대상과 기능도 검증한다. |
| [`strace`](https://github.com/strace/strace), `ltrace` | 시스템 호출·라이브러리 호출 추적 | 검증 필요 | 대상 시작과 추적을 실제 정책에서 수행한다. 호스트 또는 다른 컨테이너에 attach하지 않는다. |
| `AFL++`, `honggfuzz`, `libFuzzer` | 입력 변형으로 프로그램 오류 찾기 | 검증 필요 | 대상 빌드·계측·프로세스 수·CPU·메모리·시간·충돌 자료를 검증한다. 일부 관찰 모드는 권한에 따라 제한될 수 있다. |

Docker의 [seccomp 문서](https://docs.docker.com/engine/security/seccomp/)는 프로세스
관찰 제한을 설명한다. 모든 GDB 경로가 무조건 실패한다거나, 설치만 하면 모든 attach가
가능하다고 단정하지 않는다. 실제 필요한 동작을 검증하고 결과로 프로필을 결정한다.

## 9. 내부 인증 서비스·프록시·프레임워크

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`Impacket CLI`](https://github.com/fortra/impacket) | SMB·Kerberos·RPC 등 인증·프로토콜 실험 | 검증 필요 | 구체적인 하위 명령과 실제 로컬 서비스를 검증한다. 라이브러리 전체 지원으로 표현하지 않는다. |
| `NetExec`, `enum4linux-ng`, `rpcclient` | 계정·공유·디렉터리 권한 조사 | 검증 필요 | 비특권으로 구동할 수 있는 실제 서비스와 인증 자료가 먼저 필요하다. |
| [`msfconsole`, `msfvenom`(Metasploit)](https://github.com/rapid7/metasploit-framework) | 로컬 대상 모듈 실험·실습용 산출물 생성 | 검증 필요 | 선택 모듈, 내부 연결, 부가 서비스와 자원 비용을 검증한다. 일반 문제의 필수 기본 도구로 일괄 제공하지 않는다. |
| [`linpeas.sh`](https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS) | Linux 환경의 설정·권한 흔적 조사 | 모드 한정 | 컨테이너 내부 관찰 후보. 현재 `no-new-privileges`에서 실제 권한 상승이 가능한지는 따로 검증한다. 호스트·컨테이너 탈출 증거로 취급하지 않는다. |
| [`chisel`](https://github.com/jpillora/chisel), [`proxychains4`](https://github.com/rofl0r/proxychains-ng), SSH forwarding | 프록시·중계·권한 차이가 있는 내부 서비스 연결 | 모드 한정 | 중계자와 대상 모두 같은 문제의 선언된 네트워크에 둔다. 호스트 터널이나 외부 프록시는 제공 범위 밖이다. |

## 10. 모바일·공급망·클라우드·블록체인

| 도구 | 무엇을 하는가 / 가능한 실습 | 판정 | 준비 사항 |
| --- | --- | --- | --- |
| [`apktool`](https://github.com/iBotPeaches/Apktool), [`jadx`](https://github.com/skylot/jadx) | APK 자료·리소스·DEX 코드 조사 | 후보 | 필요한 Java 런타임과 실습용 APK를 포함한다. 실제 앱 실행·계측은 별도 실행 프로필이다. |
| [`gitleaks`](https://github.com/gitleaks/gitleaks) | 로컬 자료·Git 이력의 노출된 키 조사 | 후보 | 실습용 가짜 비밀과 저장소를 제공한다. 호스트 비밀을 검색하지 않는다. |
| [`semgrep`](https://github.com/semgrep/semgrep) | 제공된 코드의 패턴·취약한 사용 조사 | 모드 한정 | 고정된 로컬 규칙을 사용한다. 원격 규칙·클라우드 업로드·metrics를 전제로 하지 않는다. |
| [`syft`](https://github.com/anchore/syft) | 제공된 디렉터리·아카이브의 구성 요소 목록 작성 | 모드 한정 | 로컬 파일 입력만 후보. 호스트 Docker 소켓·외부 레지스트리 입력은 범위 밖이다. |
| [`trivy`](https://trivy.dev/docs/latest/advanced/air-gap/), [`grype`](https://github.com/anchore/grype) | 파일·구성 요소의 알려진 취약점 조사 | 모드 한정 | 정확한 DB snapshot과 오프라인 설정을 제공한다. 엔진과 DB 버전을 따로 고정한다. |
| [`cosign`](https://github.com/sigstore/cosign) | 제공된 산출물·서명·증명 자료 검증 | 모드 한정 | 실제 로컬 키·증명과 오프라인 검증 경로를 확인한다. 공개 서명 서비스·레지스트리 연결은 범위 밖이다. |
| [`aws`](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-endpoints.html), [`mc`](https://github.com/minio/mc) | 문제 안의 실제 객체 저장소·권한 조사 | 모드 한정 | 명시적인 내부 endpoint와 실습 키를 제공한다. 실제 AWS 계정 접근이나 전체 AWS 동작 재현을 의미하지 않는다. |
| [`cast`, `forge`, `anvil`(Foundry)](https://github.com/foundry-rs/foundry) | 실제 로컬 체인의 호출·상태·계약 실험 | 검증 필요 | 로컬 체인, compiler와 의존성, 시간·트랜잭션 제어를 먼저 검증한다. 공개 체인·실제 자금과 연결하지 않는다. |

## 11. 현재 실행 범위와 맞지 않는 사용 방식

| 도구·모드 | 판정 | 현재 정책과 맞지 않는 이유 |
| --- | --- | --- |
| Nmap SYN·OS 탐지·raw 패킷 모드, [`masscan`](https://github.com/robertdavidgraham/masscan), ZMap raw 스캔, `hping3` raw 전송 | 범위 밖 | 현재 컨테이너에 부여하지 않는 원시 패킷 권한을 전제로 한다. |
| `tcpdump`·TShark의 라이브 인터페이스 캡처 | 범위 밖 | 현재 raw 캡처 권한과 호스트 네트워크 접근을 제공하지 않는다. 오프라인 PCAP 분석은 별도 지원 후보다. |
| `arpspoof`, [`ettercap`](https://github.com/Ettercap/ettercap), Bettercap의 ARP/MITM·raw 모드 | 범위 밖 | raw 패킷·인터페이스·네트워크 변경 권한이 필요하다. 해당 모드의 실행을 다른 학습으로 대체해 완료 처리하지 않는다. |
| `airmon-ng`, `airodump-ng`, `aireplay-ng`, [`wifite`](https://github.com/derv82/wifite2)의 라이브 무선 실습 | 범위 밖 | 무선 장치·monitor 모드·장치 접근이 필요하다. 제공 캡처 분석과 구분한다. |
| GPU를 사용하는 Hashcat | 범위 밖 | 현재 호스트 GPU 장치를 제공하지 않는다. CPU PoCL backend는 작은 실제 해시로 검증했다. |
| [`subfinder`](https://github.com/projectdiscovery/subfinder), [`amass`](https://github.com/owasp-amass/amass)의 공개 인터넷 자산 수집 | 범위 밖 | 공개 DNS·검색·인증서·외부 API가 주된 입력인 사용 방식이다. 내부 DNS 실습은 `dig` 등과 실제 내부 서버로 별도 설계한다. |
| TUN·호스트 라우팅을 사용하는 터널, 실기기를 연결하는 `adb`·Frida | 범위 밖 | 현재 제공하지 않는 장치 또는 네트워크 관리 접근이 필요하다. Frida의 컨테이너 내부 자식 프로세스 계측은 별도로 검증했다. |
| 호스트 Docker·Kubernetes 대상 CLI, 호스트 privilege escalation·escape | 범위 밖 | 호스트 daemon·cluster·장치·비밀을 문제에 제공하지 않는다. 저장된 설정 파일 분석은 다른 명확한 목표로 작성한다. |

Burp Suite, Wireshark GUI, Ghidra GUI, Cutter, IDA 등은 이 CLI 공급 목록과 다른
화면·사용자 경험이 필요하다. Ghidra headless와 Wireshark CLI는 위에서 따로 판단했다.

## 실습 구성 순서

### 1차: 직접 관찰과 조작

- 기본 셸·텍스트 명령, `file`, `strings`, `xxd`, `base64`, 해시 명령, `tar`, `unzip`, `jq`, `openssl`, `git`.
- HTTP 요청: `curl`.
- TCP 연결·탐색: `ncat`, Nmap의 비특권 TCP 모드.
- 파일·메타데이터: `sqlite3`, `exiftool`.
- 경로 후보 탐색: `ffuf`와 작은 실습용 사전.

처음부터 프로그래밍 없이 요청·응답·바이트·로그·서비스를 직접 관찰하는 문제를
만들 수 있는 묶음이다. 기존 basic 이미지로 준비하고 문제별 풀이를 검증한다.

### 2차: 분야별 묶음

- 웹: `whatweb`, `sqlmap`, JWT 도구, 로컬 Nuclei 템플릿, TLS 검사.
- 포렌식: TShark의 파일 모드, `binwalk`, `zsteg`, Sleuth Kit, 문서 분석.
- 암호·인증: John Jumbo, 변환 도구, 작은 사전, 제한된 인증 실험.
- 리버싱: Binutils, `checksec`, `radare2`·`rizin`, `ROPgadget`·`ropper`.

### 3차: 실행 프로필 검증 후 선택

디버거·추적기·퍼저, Hashcat CPU, 메모리 덤프, AD/SMB 복합 서비스,
Metasploit, Ghidra headless, 실제 로컬 체인 등이다.
필수 작업이 현재 정책에서 실패하면 그 프로필은 미검증으로 남긴다.

확장 이미지에서는 John Jumbo·CPU Hashcat, JWT, TLS, 파일 복구·PCAP 스트림,
GEF·Pwndbg·Frida의 자식 프로세스 관찰, Ghidra headless, libFuzzer·honggfuzz,
로컬 규칙·오프라인 DB, Cosign 서명·변조 거부, Foundry, APK 처리를 검사했다.
Volatility와 NetExec는 CLI 시작만 확인했으며 실제 덤프·AD 서비스가 있는
문제의 검증은 추가로 필요하다. 전체 목록의 모든 모드를 검증한 결과는 아니다.

## 공급 구조와 책임

현재 계약은 `[solve].image`로 풀이 터미널과 자동 풀이에 사용할 이미지 하나를
지정한다. 소비자는 로컬 이미지를 확인하고 없으면 pull한다.
따라서 추가 도구를 이 이미지에 미리 포함하는 접근은 기존 인터페이스에 맞는다.
도구 이미지 소스·버전·검증·배포의 관리 주체는 challenges다.
platform은 선언된 이미지와 도구를 기존 격리 정책으로 실행한다.

현재 공급 구조는 다음과 같다.

- 현재 8개 문제에는 `basic`과 `pcap` 두 이미지를 준비한다. PCAP 문제는
  `tshark`만 추가하며 기본 이미지 레이어를 재사용한다.
- 문제마다 필요한 이미지 하나를 선택하고,
  터미널은 문제의 `[player].tools`에 필요한 경우에만 노출한다.
- 도구·런타임·규칙·DB는 해당 문제의 풀이에 필요한 것만 준비한다.
  단어 목록·심볼·대상 파일·서비스·예제·시작 지식도 문제별로 선택한다.
  Grype·Trivy 같은 취약점 DB는 해당 분석을 학습 목표로 삼는 문제용 이미지에
  포함한다. 도구 설치 코드를 문제마다 복사하지 않는다.
- `lab`, `extended`, `specialized`, `all`은 추가 도구의 선택형 구성이다.
  실제 풀이에 맞는 구성을 선택하고, 새 도구가 필요하면 작은 이미지부터 확장한다.
- 실제 문제 사이트의 Python 이미지는 풀이 도구 이미지와 별도로 관리한다.
  현재 생성기의 `--image`는 두 역할을 함께 바꾸므로, 도입 시 작성 도구에서
  두 선택을 분리해야 한다. 소비 계약에 중복된 프로필 해석기를 추가할 필요는 없다.
- 사용자의 호스트에는 Docker 전제만 유지한다. 추가 언어·패키지·도구 설치는
  준비된 컨테이너가 담당한다.

## 이미지 갱신과 문제 추가 시 통과할 검증

1. 버전·의존성·출처·라이선스를 고정한다. OS 패키지는 버전과 저장소 snapshot,
   언어 패키지는 exact 버전·lockfile, 배포 이미지는 immutable digest로 관리한다.
   현재 이미지의 exact 버전·artifact SHA256·출처는 `images/cli`의 lock에 있다.
   로컬 이미지와 공개 registry 배포를 구분한다.
2. 인터넷이 없는 실제 풀이 컨테이너에서 필요한 명령·정상 결과·오류 결과를
   실행한다. `--help`나 설치 성공만으로 기능을 검증했다고 처리하지 않는다.
3. `/workspace`의 읽기 전용 원본, 컨테이너 내부 작업 파일, 캐시·출력 위치를 확인한다.
   파일 분석과 네트워크 사용을 나누어 해당 종류의 실제 실행 경로를 검증한다.
4. 네트워크 도구는 같은 문제의 연결 성공과 인터넷·호스트·다른 문제의 차단을
   도달 가능한 대조군으로 확인한다. 플러그인·업데이트·콜백 경로도 포함한다.
5. cold/warm 준비 시간, 이미지 용량, CPU·RAM·프로세스·출력 비용을 측정한다.
   현재 author/consumer는 컨테이너당 2 CPU·2GiB RAM·256 PID 및 공통 총량
   상한을 적용한다. 무거운 대상도 해당 상한과 임시 공간 안에서 검사한다.
6. Linux 컨테이너의 지원 CPU 아키텍처를 고정하고 검증한다. 현재 호스트의 실행
   증거와 나중의 Windows/macOS 호스트 검증 범위를 구분한다.
7. 실제 문제의 풀이·정답 확인·선택한 패치·취소·정리를 검증한다.
   짧은 사용 설명과 공통 시작 지식을 제공하고, 필요한 도구 자체는 학습 목표와
   선수 지식에 연결한다. 자동 스캐너 결과만 복사하면 끝나는지를 학습 리뷰에서 확인한다.

현재 공통 이미지의 설치·로컬 빌드·대표 기능 검증을 완료했다.
[CLI 문제](cli-challenge-plan.md)의 8개 새 시나리오는 구현과 문제별 기술 검증을
마쳤다. 자료 대조, 풀이·정답, 서비스 패치·정상 기능, 소비자 실행과 실제 PTY의
중단·재접속·종료 후 초기화를 확인했다. 독립 학습자 리뷰는 배포 전 별도 단계다.
