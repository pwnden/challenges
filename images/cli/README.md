# 공통 CLI 이미지

문제마다 `solve.image`를 선택한다. 설치 코드를 문제 Dockerfile에 반복할 필요 없다.
현재 Linux/WSL의 Linux amd64 Docker에서 로컬로 빌드하는 두 프로필을 제공한다.

| 이미지 | 구성 |
| --- | --- |
| `pwnden-cli:basic-20261003` | 기본 파일 명령, Bash, rg, Binutils, xxd, 압축 도구, curl, jq, OpenSSL, Git, Nmap, Ncat, SQLite, ExifTool, ffuf, socat, DNS·SSH 클라이언트 |
| `pwnden-cli:lab-20261003` | 기본 이미지 + PCAP·파일 포렌식, DB·SMB·LDAP 클라이언트, sqlmap, Hydra·Ncrack, John, CPU Hashcat/PoCL, GDB·LLDB·strace, AFL++, GCC, pwntools, ROPgadget·ropper, oletools, Volatility 3 |

```sh
cd /path/to/challenges
docker build --target basic -t pwnden-cli:basic-20261003 images/cli
docker build --target lab -t pwnden-cli:lab-20261003 images/cli
```

문제 선언 예:

```toml
[solve]
image = "pwnden-cli:basic-20261003"
command = ["sh", "solve.sh"]
writable = true
timeout_seconds = 30
```

`writable = true`는 문제별 256MiB 임시 복사본에서 실행한다. 명령과 터미널이
같은 공간을 쓰고, 환경이 종료되면 지운다. 원본 저장소는 그대로 유지한다.
읽기 전용 문제는 `/tmp`에 결과를 만들 수 있다. 인터넷 다운로드는 런타임에
차단되므로 규칙, 단어 목록, 심볼, PCAP, 해시, 문서 등 풀이 자료를 미리 배포한다.

Base image digest, Debian 저장소의 `20261002T000000Z` snapshot, Python 의존성
44개 버전을 고정했다. Debian 서명 검증은 유지하고 오래된 snapshot의 날짜
만료 검사만 해제한다. 이미지 안의 `/opt/package-versions.txt`와 확장 이미지의
`/opt/python-versions.txt`에 실제 설치 버전을 기록한다. Python 파일 자체의
해시 및 빌드 도구까지 고정한 byte-for-byte 재현 빌드는 아직 제공하지 않는다.

UID/GID `10001:10001`, `/etc/passwd` 계정과 `/home/pwnden` 홈을 포함한다.
Hashcat은 PoCL CPU backend를 사용하고 스레드는 2개로 제한한다. Nmap은
`nmap --unprivileged -sT -Pn ...`처럼 TCP 연결 스캔을 사용한다. GPU, raw socket,
호스트·무선 장치와 외부 인터넷은 실행기 정책상 제공하지 않는다.

이름은 로컬 이미지 태그이며 외부 registry에 게시하지 않았다. 실습 배포 시에는
검증한 이미지를 준비하고 registry digest를 고정해야 한다. 94개 조사 항목 전체나
각 도구의 모든 기능을 지원한다는 뜻은 아니다. John은 Debian의 기본 John이며
Jumbo가 아니다. Volatility는 명령 실행만 확인했고 실제 메모리 덤프 분석은
별도 fixture 검증이 필요하다.
