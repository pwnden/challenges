# 공통 CLI 이미지

문제의 `solve.image`로 풀이 터미널과 자동 풀이에 쓸 이미지를 선택한다.
도구와 내부 Python·Ruby·Java 런타임은 Docker 이미지에 미리 설치한다.
지원·검증 환경은 Linux/WSL의 Linux amd64 Docker다.

## 이미지 선택과 빌드

| 이미지 | 구성 |
| --- | --- |
| `pwnden-cli:basic-20261003` | 기본 파일 명령, Bash, rg, Binutils, xxd, 압축 도구, curl, jq, OpenSSL, Git, Nmap, Ncat, SQLite, ExifTool, ffuf, socat, DNS·SSH 클라이언트 |
| `pwnden-cli:lab-20261003` | basic + PCAP·파일 포렌식, DB·SMB·LDAP 클라이언트, sqlmap, Hydra·Ncrack, 기본 John, CPU Hashcat/PoCL, GDB·LLDB·strace, AFL++, GCC, pwntools, ROPgadget·ropper, oletools, Volatility 3 |
| `pwnden-cli:extended-20261003` | 조사 목록의 일반 CLI 묶음. 웹 탐색·TLS·JWT, John Jumbo, 정적 분석·디버깅·퍼징, APK, 공급망 분석, Foundry, Frida와 오프라인 DB·규칙·템플릿 포함. 명령 174개 |
| `pwnden-cli:specialized-20261003` | extended + Ghidra headless, Metasploit, linPEAS. 명령 178개 |
| `pwnden-cli:all-20261003` | specialized + raw 스캔·무선·공개 자산 수집·ADB 도구의 실행 파일. 명령 191개. 실행 권한과 장치·인터넷 정책은 동일 |

기존 basic/lab 이미지는 유지한다. 확장 세 이미지는 `extended → specialized → all`
순서로 레이어를 공유한다. 작은 문제는 basic/lab, 모든 도구를 준비해 둘 때는 all을
선택한다. 서비스 컨테이너는 문제에 필요한 별도 이미지를 사용한다.

```sh
cd /path/to/challenges
docker build --platform linux/amd64 --target basic -t pwnden-cli:basic-20261003 images/cli
docker build --platform linux/amd64 --target lab -t pwnden-cli:lab-20261003 images/cli
docker build --platform linux/amd64 --target extended -f images/cli/Dockerfile.toolbox -t pwnden-cli:extended-20261003 images/cli
docker build --platform linux/amd64 --target specialized -f images/cli/Dockerfile.toolbox -t pwnden-cli:specialized-20261003 images/cli
docker build --platform linux/amd64 --target all -f images/cli/Dockerfile.toolbox -t pwnden-cli:all-20261003 images/cli
```

이미지 준비에는 인터넷과 디스크 공간이 필요하다. 확장 이미지에는 Grype·Trivy의
큰 DB도 포함된다. Docker가 보고한 크기와 검증한 image ID는 [validation.json](validation.json)에
기록한다. 빌드 캐시와 이전 이미지까지 남아 있으면 실제 디스크 사용량은 더 크다.
이미지 크기가 풀이 컨테이너의 RAM 예약량을 뜻하지는 않는다.

문제 선언 예:

```toml
[solve]
image = "pwnden-cli:all-20261003"
command = ["sh", "solve.sh"]
writable = true
timeout_seconds = 30
```

이름은 로컬 태그다. 외부 registry에 게시하지 않았다. 배포 시에는 검증한 이미지를
준비하고 registry digest를 고정한다. 문제별 설치 코드를 반복할 필요는 없다.

## 실행 범위와 풀이 자료

실행기는 UID/GID `10001:10001`, read-only root, 모든 capability 제거,
`no-new-privileges`, 2 CPU·2GiB RAM·256 PID 상한을 적용한다.
`/tmp`는 128MiB, 홈은 64MiB다. `writable = true`는 명령과 터미널이 공유하는
문제별 256MiB 임시 복사본에서 실행하며, 환경 종료 때 지운다.
원본 저장소는 읽기 전용이다. 읽기 전용 문제도 `/tmp`에 결과를 만들 수 있다.
정확한 조건은 [runtime limits](../../docs/verification.md#runtime-limits)를 따른다.

Nmap은 `nmap --unprivileged -sT -Pn -n TARGET`처럼 TCP 연결 스캔을 사용한다.
이미지의 파일 capability와 setuid/setgid도 제거하므로 Nmap 실행 자체가
capability 없는 환경에서 거부되는 문제를 피한다. Hashcat은 CPU PoCL backend를
포함하며 CPU 스레드를 2개로 제한한다. Java에도 CPU·힙 상한을 지정한다.

all에 실행 파일이 있어도 raw 패킷, 라이브 캡처, 무선 장치, GPU, 호스트 접근,
외부 인터넷을 허용하지 않는다. 서비스 문제는 같은 문제의 격리 네트워크를 쓴다.
Volatility에는 문제 덤프에 맞는 심볼, RsaCtfTool의 일부 공격에는 Sage 같은 추가
런타임, Trivy의 Java 분석에는 별도 Java DB가 필요할 수 있다. 이런 입력·의존성은
해당 문제 준비 단계에서 포함하고 검증한다.

공통 자료와 명령 이름은 다음과 같다.

| 항목 | 제공 형태 |
| --- | --- |
| `yq` | Mike Farah 구현. 동명의 Python 프로그램과 구분 |
| `httpx` | ProjectDiscovery HTTP 조사 CLI. `httpx-toolkit`도 사용 가능 |
| `nuclei` | `/opt/upstream/nuclei_templates`; 업데이트 확인과 외부 Interactsh를 끈 wrapper. `-t`로 문제의 로컬 템플릿 선택 가능 |
| `capa` | 고정 규칙 `/opt/upstream/capa_rules`; 문제별 규칙은 `-r`로 지정 |
| `jwt_tool.py` | 첫 실행 시 임시 홈에 개인별 키·설정 생성. 외부 콜백 기본값 없음. 사전 경로는 절대 경로 |
| `pwndbg`, `gdb-gef` | 각각 준비한 디버거 확장을 실행. 자식 프로세스 디버깅 검증 |
| `john`, `zip2john`, `ssh2john`, `office2john` | 확장 이미지에서는 Jumbo와 변환 도구. lab의 기본 John과 구분 |
| `7zz`, `testssl.sh` | 설치된 `7z`, `testssl`의 별칭 |
| `chisel`, `foundry-chisel` | 전자는 네트워크 프록시, 후자는 Foundry Solidity REPL |
| `cast`, `forge`, `anvil`, `solc` | Ethereum Foundry 및 로컬 Solidity compiler. 동명의 GNOME IDE 패키지와 구분 |
| `grype`, `trivy` | 빌드 시 초기화한 고정 DB, 자동 업데이트 중단. Trivy는 read-only root에서 DB를 읽는 공식 버전 사용 |

고정한 JWT Tool은 정상 디코딩 후에도 종료 코드 1을 반환한다. 자동 풀이에서는
디코딩 출력까지 검사한다. 초기 설정은 첫 명령 전에 wrapper가 준비한다.
규칙과 DB는 실습용 snapshot이다. 최신 취약점 진단 결과를 보장하지 않는다.
Semgrep은 로컬 규칙을 지정한다. Cosign은 문제의 로컬 키·번들로 오프라인 검증한다.
단어 목록·PCAP·해시·APK·메모리 덤프·심볼·서비스 인증 자료는 문제별로 제공한다.

## 출처와 고정 방식

기존 basic/lab은 Python base digest, Debian `20261002T000000Z` snapshot과
Python 44개 버전을 고정한다. 확장 이미지에는 별도 Kali base digest를 사용한다.

- [toolbox-packages.json](toolbox-packages.json): APT 묶음의 직접 의존성.
- `extended.apt.lock`, `specialized.apt.lock`, `restricted.apt.lock`: 각 묶음의 누적
  설치 의존성 901·930·963개. 서명 검증한 Kali 인덱스의 버전·URL·SHA256을 저장한다.
  빌드는 각 `.deb`의 SHA256을 확인한 뒤 로컬 저장소로 설치하며 이동하는 인덱스를 조회하지 않는다.
  `restricted`는 all 단계에 추가되는 도구 묶음의 내부 이름이다.
- [apt-provenance.json](apt-provenance.json): base digest와 서명 검증한 인덱스의 날짜·해시.
- [python-toolbox.lock](python-toolbox.lock): CPython 3.13/Linux amd64의 Python 패키지
  121개, exact 버전과 artifact SHA256. 별도 venv로 OS Python과 분리한다.
- [upstream.lock.json](upstream.lock.json): 공식 배포 바이너리·source commit·규칙·템플릿
  12개의 버전·URL·SHA256. RsaCtfTool은 고정한 source commit에서 설치한다.
- [ruby-toolbox.lock.json](ruby-toolbox.lock.json): zsteg와 의존성 gem 7개의 버전·SHA256.
- [databases.lock.json](databases.lock.json): Grype·Trivy의 고정 DB와 SHA256.

이미지 내부 `/opt/toolbox`에 lock과 출처를 포함한다. `/opt/package-versions.txt`,
`/opt/python-versions.txt`, `/opt/ruby-versions.txt`에는 설치 결과를 기록한다.
패키지의 copyright·license 자료와 source 배포에 포함된 자료도 유지한다.
바이트 단위로 동일한 빌드 결과나 모든 도구의 추가 플러그인 설치까지 보장하지는 않는다.

버전 갱신은 유지보수 작업으로 별도 수행한다. `lock_toolbox.py`는 digest로 고정한
Kali 준비 컨테이너에서 서명 검증을 유지한 `apt-get update` 후 실행한다. 인덱스 출처도
함께 갱신한다. Python은 동일한 Python base의 `pip install --dry-run --report` 결과를
`lock_python.py`에 전달한다. `lock_upstream.py`, `lock_databases.py`는 공식 endpoint의
현재 자료를 lock에 저장한다. 변경한 lock을 검토하고 이미지를 다시 빌드·검증한다.
이 생성기는 준비 단계의 유지보수용이며 풀이 중에 실행하지 않는다.

## 검증

```sh
python3 -B images/cli/verify_toolbox.py pwnden-cli:all-20261003 --profile restricted --report /tmp/toolbox-report.json
```

[commands.json](commands.json)은 profile별 필수 명령 목록이다. all은 191개 이름을
포함한다. 94개 조사 항목에는 묶음·별칭·같은 도구의 여러 모드가 있으므로, 명령 수와
도구 수·검증된 기능 수는 서로 다르다.

검사기는 인터넷 없는 컨테이너에서 실제 사용자·권한·자원·임시 공간 조건을 적용한다.
직접 만든 파일, loopback HTTP·TLS 서버, 작은 해시·퍼징 대상·로컬 체인·APK로
기능을 검사하고 원문 출력이 포함된 보고서를 지정 경로에 저장한다.
실행 후 자체 컨테이너를 제거한다. 간략한 결과는 [validation.json](validation.json)에 있다.
현재 all 이미지의 검사 72개가 통과했다. 기능 검사 65개, 시작 확인 2개,
설치 확인 1개, 권한 검사 3개, 자원 관찰 1개로 구성한다.
실제 Python 작성기에서도 읽기 전용·쓰기 허용 실행, 원본 보존과 임시 공간 정리를
별도로 확인했다. 확장 세 이미지의 명령 목록과 레이어 공유도 확인했다.

대표 기능은 Nmap TCP 연결 스캔, John Jumbo·CPU Hashcat, JWT, TLS,
파일 복구·PCAP 스트림 추출, GEF·Pwndbg·Frida의 자식 프로세스 관찰,
Ghidra headless, libFuzzer·honggfuzz, Semgrep·SBOM·오프라인 DB 조회,
Cosign 정상 서명·변조 거부, Foundry 로컬 체인, APK 빌드·해석이다.
Volatility와 NetExec 검사는 CLI 시작 확인이며 실제 덤프·AD 분석 검증은 아니다.
나머지 191개 명령도 모두 기능 검증했다고 해석하지 않는다.
문제별 풀이·정답·패치·정리 검증과 author/consumer 네트워크 격리 검증은 계속 필요하다.
