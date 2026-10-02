# CLI로 직접 조사하는 문제

2026-10-03 작성한 신규 문제 8개의 설계와 구현 기록이다. 현재 Linux/WSL의 Linux amd64
Docker에서 검증한 공통 CLI 이미지와 격리 실행기로 자료·요청·서비스를 직접 조사한다.
8개 모두 대상·배포 자료·브리핑·힌트·해설·CLI 해답을 구현하고 문제별 기술 검증을
마쳤다. 독립 학습자 리뷰와 최종 난도 확인은 배포 전에 별도로 수행한다.

기존 [12개 문제](../README.md)의 입문·초급 학습 흐름을 이어 간다는 가정으로
범위를 잡았다. 아래 난도는 설계 목표이며, 완성된 풀이 경로와 독립 학습자
리뷰를 통해 최종 결정한다. CLI 사용 검사의 통과를 새 문제의 검증으로 대신하지 않는다.

## 공통 설계

- 플레이어는 제공된 명령의 입력을 바꾸고 결과를 비교한다. 각 문제의 일반 풀이에는
  Python 작성이 필요하지 않으며, 필요한 셸·SQL·JSON 문법을 시작 설명에 제공한다.
- 8개 모두 초급을 목표로 한다. 짧은 자료에서 단서 두세 개를 연결하고 대상·버전·
  승인 상태·응답 본문으로 후보를 구분한다. 선택 기준은 첫 행동 전에 제공한다.
  그럴듯한 과거 코드나 정상 응답도 포함하며 정답과 구분되는지 대조 검사로 확인한다.
- 한 문제에는 보안 학습 목표 하나를 둔다. 명령의 실행 결과에서 무엇을 관찰하고
  어떤 판단을 해야 하는지 브리핑·추가 정보·사건 보고서에 연결한다.
- 대상은 실제 Git 저장소, SQLite DB, 이미지, HTTP/TCP 서비스, PCAP, 전자서명을
  사용한다. 파일 출처와 실습 자료의 생성 방법을 작성 기록에 남긴다.
- `[player].tools = ["terminal"]`을 기본으로 한다. 배포 자료는 `files`로 선언하고
  브리핑에서 정확한 경로와 역할을 안내한다. 파일 탭이나 웹 탭이 풀이에 필요한
  경우에만 추가하고 터미널을 첫 도구로 유지한다.
- 새 문제의 `solve.writable = true`를 사용해 쿠키·응답·추출 결과를 문제별
  256MiB 임시 복사본에 남긴다. 환경 종료 후 새로 시작하면 처음 자료로 돌아간다.
- HTTP/TCP 서비스는 같은 문제의 `app` 호스트에서 제공하고 파일 문제는 네트워크
  `none`을 사용한다. 사전·키·참고 자료는 미리 배포한다.
- 작성자 해답은 `command = ["bash", "solve/solve.sh"]`로 실행한다. 해답도 플레이어와
  같은 CLI를 사용하고 stdout에는 제출할 값 하나만 출력한다. 중간 검사 결과는
  stderr나 파일에 기록한다. 자료 생성과 대조 검사는 작성자용 Python을 사용할 수 있다.
- 파일 문제는 고정 제출값의 SHA-256, 서비스 문제는 실행마다 생성된 flag를 사용한다.
  정답 획득과 보안 관찰을 구분해 해설에 둘 다 남긴다.
- 기존 [작성 기준](authoring-standard.md), [시나리오 틀](scenario-authoring.md),
  [계약](contract.md), [런타임 한도](verification.md#runtime-limits)를 적용한다.
  분야·주제는 `AUTHORING.md`에 기록한다.

## 문제 목록과 구현 순서

| 순서 | 표시 제목 / slug | 도구 | 형태·이미지 | 목표 난도 |
| --- | --- | --- | --- | --- |
| 1 | [공개 이미지에 남은 내부 메모](../challenges/image-notes/README.md) / `image-notes` | `file`, `exiftool`, `jq` | 파일·basic | 2 초급 |
| 2 | [지운 설정 파일의 이전 내용](../challenges/commit-trail/README.md) / `commit-trail` | `tar`, `git`, `rg` | 파일·basic | 2 초급 |
| 3 | [삭제한 문서가 남은 백업](../challenges/retained-record/README.md) / `retained-record` | `sqlite3` | 파일·basic | 2 초급 |
| 4 | [내보내기에서 빠진 권한 검사](../challenges/export-gap/README.md) / `export-gap` | `curl`, `jq` | 서비스 1개·basic | 2 초급 |
| 5 | [개발용 점검 포트](../challenges/diagnostic-port/README.md) / `diagnostic-port` | `nmap`, `ncat`, `curl` | 서비스 1개·basic | 2 초급 |
| 6 | [모든 경로가 200을 반환하는 서버](../challenges/quiet-route/README.md) / `quiet-route` | `ffuf`, `curl`, `jq` | 서비스 1개·basic | 2 초급 |
| 7 | [패킷에 남은 전송 파일](../challenges/packet-delivery/README.md) / `packet-delivery` | `tshark`, `file`, `tar`, `jq` | 파일·pcap | 2 초급 |
| 8 | [서명이 맞는 납품 문서](../challenges/signed-delivery/README.md) / `signed-delivery` | `openssl`, `sha256sum` | 파일·basic | 2 초급 |

basic은 `pwnden-cli:basic-20261003`, pcap은 `pwnden-cli:pcap-20261003`을 뜻한다.
현재 8개 문제에는 basic과 basic에 `tshark`만 추가한 pcap 두 이미지를 사용한다.
도구는 문제의 학습 목표와 실제 풀이 명령을 기준으로 선택한다. 새 문제가 추가
도구를 요구하면 해당 문제용 이미지를 준비하고, 기능·용량·격리 조건을 검증한다.
현재 PC에 빌드된 로컬 이미지를 사용한다. 새로운 PC에서 실행할 때는
[공통 이미지의 빌드 방법](../images/cli/README.md)을 먼저 따른다.

## 1. 공개 이미지에 남은 내부 메모

- **의뢰:** 작업 관리 도구에서 내보낸 공개 안내 이미지에 내부 메모까지 따라갔다는
  제보를 확인한다. 화면에 보이는 안내와 파일이 실제로 담고 있는 내용을 비교한다.
- **학습 목표:** 보이는 이미지와 메타데이터의 공개 범위가 다를 수 있음을 입증한다.
  분야 `digital-forensics`, 주제 `forensics-files-metadata`, category `forensics`.
- **자료:** `files/notice.png`, `files/export-policy.txt`. 실제 PNG의 `Comment`에
  여러 배너·버전의 JSON 메모와 코드가 있고 Description에는 내보낸 배너 ID·버전이 있다.
  공개 정책은 이미지 안내문만 외부에 배포하도록 정한다.
- **풀이:** file로 형식을 확인하고 exiftool로 메타데이터를 읽는다. Description과
  Comment의 JSON을 대조해 같은 배너·버전의 활성 메모를 고른다. 다른 배너와 폐기 버전의
  코드도 있어 첫 코드만 읽으면 오답이다. PNG·Comment·JSON의 역할을 설명하고
  정답과 무관한 작은 JSON 예제로 필드 선택을 안내한다.
- **완료:** 이미지 메타데이터에서 확인한 `pwnden{...}` 복구 코드를 제출한다.
- **추가 정보:** 화면 밖의 속성 확인 → 내부 메모 필드의 의미 순으로 제공한다.
- **검증:** 원본 PNG의 파싱과 코드 회수, 메타데이터를 제거한 사본에서 회수 실패,
  두 사본의 이미지 픽셀 동일성을 확인한다. 브리핑과 파일명에는 코드가 없다.

## 2. 지운 설정 파일의 이전 내용

- **의뢰:** 팀이 공개한 소스 묶음에서 설정 파일을 지웠지만 이전 내용도 배포됐는지
  확인해 달라는 요청이다. 전달된 저장소는 이 실습을 위해 만든 작은 로컬 Git 저장소다.
- **학습 목표:** 현재 파일 삭제와 Git 이력에 저장된 비밀 제거의 차이를 확인한다.
  분야 `software-supply-chain-security`, 주제 `supply-chain-history`, category `misc`.
- **자료:** `files/source.tar.gz` 안의 정상 Git 저장소. 8개 커밋에 키 교체·설정 이름
  변경·삭제가 있다. 현재 release 안내는 적용 버전과 설정 경로를 지정한다. 원격 주소와 외부 객체 참조가
  없는 독립 저장소다. 터미널에서 임시 폴더에 압축을 풀어 조사한다.
- **풀이:** 현재 파일을 조사한 뒤 `git log --all`로 변경을 찾고, 해당 커밋의 diff와
  `git log --follow`로 이름 변경과 키 교체를 따라간다. 삭제 직전의 적용 버전에서
  키를 읽으며 더 오래된 폐기 키는 제외한다. 커밋·diff·과거 파일 경로를
  작은 별도 예제로 소개한다.
- **완료:** 과거 설정에 남은 `pwnden{...}` 복구 키를 제출한다.
- **추가 정보:** 현재 파일과 이력의 범위 → 삭제 커밋의 부모 내용 읽기.
- **검증:** 현재 checkout에 키가 없는 상태, 과거 객체를 통한 회수, 전체 이력에서
  키를 제거한 대조 저장소의 회수 실패를 확인한다. 자료 생성은 실제 Git 명령을 사용한다.
  해설에는 노출된 실제 자격 증명의 교체와 배포 이력 정리의 역할을 설명한다.

## 3. 삭제한 문서가 남은 백업

- **의뢰:** 문서 목록에서 사라진 문서가 백업에도 없는지 확인한다. 전달받은 목록과
  DB는 같은 시점에 만든 실습 자료이며, 이를 통해 그 시점의 보관 상태를 조사한다.
- **학습 목표:** 목록에서 숨기는 삭제 표시와 데이터 보관 상태를 구분한다.
  분야 `digital-forensics`, 주제 `forensics-event-reconstruction`, category `forensics`.
- **자료:** `files/visible-documents.csv`, `files/snapshot.sqlite`. `documents`에는
  문서 상태가, revisions에는 버전별 본문과 published/draft 상태가 있다.
  삭제 문서는 둘이고 조사 대상에는 승인 버전 둘과 더 최신인 미승인 초안이 남는다.
- **풀이:** `sqlite3 -readonly`로 `.tables`·`.schema`를 확인한다. 목록과 문서 상태를
  비교하고 제목·문서 ID·승인 상태를 확인한 뒤 마지막 승인 버전을 읽는다. SELECT·WHERE·JOIN·
  ORDER BY·LIMIT 중 실제 풀이에 쓰는 문법과 열의 의미를 시작 설명에 제공한다.
- **완료:** 조사 대상의 마지막 승인 본문에 남은 `pwnden{...}` 코드를 제출한다.
- **추가 정보:** 화면용 목록의 필터 → 상태와 본문 테이블의 연결 → 버전 순서.
- **검증:** 실제 SQLite 상태 변경과 목록 내보내기로 자료를 생성한다. 활성 문서 조회,
  삭제 문서의 잔존 본문, 해당 본문을 제거한 대조 DB의 회수 실패를 확인한다.
  디스크의 삭제 영역 복구가 아닌 애플리케이션의 논리 삭제와 백업 범위 분석이다.

## 4. 내보내기에서 빠진 권한 검사

- **의뢰:** 일반 조회에서는 다른 사람의 문서를 차단하지만 JSON 사본을 내려받는
  내보내기 기능에도 같은 권한이 적용되는지 확인한다.
- **학습 목표:** 같은 자료를 다루는 각 작업에서 소유권 검사가 필요한 이유를 관찰한다.
  분야 `web-security`, 주제 `web-access-control`, category `web`.
- **대상:** guest 계정으로 로그인하는 실제 HTTP API. 자기 문서와 다른 소유자의
  문서가 있으며 `GET /api/notes/<id>`는 소유권을 검사한다. 취약한
  POST /api/exports는 note_id와 형식을 받는다. 기본 summary는 본문 없는 정상
  요약이고 full에서 소유권 검사가 빠졌다. 실제 서비스 안내에 형식의 역할이 있다.
- **풀이:** `curl`로 로그인하고 쿠키를 임시 작업 공간에 저장한다. 자기 문서의 조회와
  내보내기를 확인하고, 타인 조회·정상 summary·취약한 full을 jq로 비교한다.
  summary의 200은 유출 증거가 아니며 redacted와 실제 본문 포함 여부를 확인한다.
  요청 메서드·JSON 본문·쿠키·소유자의 의미를 첫 행동 전에 설명한다.
- **완료:** 잘못 허용된 내보내기 응답에서 현재 환경의 복구 코드인 flag를 회수한다.
- **추가 정보:** 같은 문서의 두 작업 비교 → POST 본문의 대상 값 → 응답 본문 확인.
- **검증:** 정상 자기 문서 조회·내보내기, 타인 조회 거부, 취약한 타인 내보내기 성공,
  패치 후 타인 내보내기 거부와 정상 기능 유지, 로그아웃 상태 거부를 검사한다.
  기존 `note-vault`에서 배운 소유권을 다른 API 작업에도 적용하는 진행 문제다.

## 5. 개발용 점검 포트

- **의뢰:** 정식 HTTP 기능에서 보호한 복구 정보를 개발용 점검 기능으로 읽을 수
  있다는 제보를 조사한다. `app` 호스트와 작은 TCP 포트 범위를 제공한다.
- **학습 목표:** 같은 네트워크에서 연결할 수 있다는 사실이 읽기 권한을 뜻하지 않음을
  입증한다. 분야 `network-security`, 주제 `network-service-trust`, category `misc`.
- **대상:** 컨테이너 하나의 HTTP 8000, 건강 검사 TCP 8003, 점검 TCP 8007.
  정식 기능은 복구 정보를 거부하지만 점검 기능은 민감한 READ를 허용한다.
  HELP·STATUS·LIST·READ를 구현하며 현재·폐기 자료를 함께 보관한다.
- **풀이:** 정상 HTTP 응답을 먼저 확인한다. `nmap --unprivileged -sT -Pn -n`으로
  제공된 11개 이내의 포트를 조사하고 `ncat`으로 각 열린 포트의 동작을 확인한다.
  도움말로 기능을 구분하고 STATUS의 active_resource와 LIST를 대조해 현재 자료를
  요청한다. 폐기 코드는 오답이다. 포트·TCP 연결·줄바꿈 입력을 안내한다.
- **완료:** TCP 점검 기능이 잘못 제공한 현재 환경의 flag를 회수한다.
- **추가 정보:** HTTP 이외의 listener 확인 → TCP 도움말 → 민감한 READ 요청.
- **검증:** 열린 포트와 닫힌 포트, HTTP의 거부와 TCP의 성공, 불완전한 명령 처리,
  패치 후 민감한 READ 거부와 STATUS·HTTP 건강 검사 유지를 확인한다.
  진단 포트만 발견해 성공한 것으로 처리하지 않는다. 기본 HTTP endpoint를 선언하고
  내부 점검 listener는 같은 문제의 터미널에서 조사한다.

## 6. 모든 경로가 200을 반환하는 서버

- **의뢰:** 존재하지 않는 경로도 200 상태로 응답하는 서버에서 공개된 운영 점검
  자료가 있는지 확인한다. 정상 안내와 점검 자료의 공개 규칙을 함께 전달한다.
- **학습 목표:** 응답 코드만으로 자원의 존재나 공개 적합성을 판단할 수 없음을 확인한다.
  분야 `web-security`, 주제 `web-information-disclosure`, category `web`.
- **대상:** 알 수 없는 경로에는 길이가 일정한 안내 응답을 반환하는 실제 HTTP 서비스.
  공개 도움말·건강 검사와 운영 점검 경로의 본문은 이 응답과 다르다. 취약한 운영
  점검 경로에는 비공개 복구 코드가 포함되며 안내와 같은 256바이트로 맞춘다.
- **자료와 풀이:** 후보 경로 12개가 든 files/paths.txt를 제공한다.
  curl로 없는 두 경로의 본문을 비교하고, 크기 필터가 실제 자료도 숨긴다는 점을
  판단한다. 안내의 view 표시를 ffuf의 -fr로 제외한 뒤 후보의 JSON을 직접 확인한다.
  상태 코드·본문 크기·후보 탐색·오탐을 작은 예제로 설명한다.
- **완료:** 공개 규칙에 어긋난 점검 응답에서 현재 환경의 flag를 회수한다.
- **추가 정보:** 공통 안내의 표시 → 내용 필터 → 후보 본문과 공개 규칙 비교.
- **검증:** 여러 잘못된 경로의 200·동일 크기, 정상 경로의 후보 포함, 취약한 점검
  자료 회수, 패치 후 점검 접근 거부와 공개 기능 유지를 검사한다. 후보 결과를
  정답으로 취급하지 않는다. 요청은 2 worker·초당 10건 이하·15초 이내로 제한한다.

## 7. 패킷에 남은 전송 파일

- **의뢰:** 테스트용 자료 전송 기록에 비공개 문서도 포함됐는지 조사한다.
  요청 주소와 응답 상태뿐 아니라 전송된 파일 내용으로 결론을 확인한다.
- **학습 목표:** 캡처에 남은 TCP 대화를 재조립해 실제로 전달된 자료를 확인한다.
  분야 `digital-forensics`, 주제 `forensics-network-evidence`, category `forensics`.
- **자료:** 작은 files/delivery.pcap와 공개 자료 목록. 세 HTTP 대화에 안내와
  같은 URL로 전송된 폐기 버전·승인 버전의 tar.gz가 포함된다.
  tar.gz 안의 내부 문서에 실습용 복구 코드가 들어 있다.
- **생성:** 로컬 실습 HTTP 대상의 실제 요청·응답 바이트를 얻고, 이를 프로토콜에 맞는
  TCP 패킷으로 오프라인 구성한다. 브리핑에서 교육용 합성 패킷임을 밝힌다.
  sequence·ACK·길이·checksum과 전송 객체 바이트를 작성자 검사로 확인한다.
- **풀이:** `tshark -r`로 HTTP 요청과 관련 대화를 찾고 HTTP 객체를 내보낸다.
  file로 객체 형식을 확인하고 tar·jq로 내부 영수증의 배치·버전·상태를 비교한다.
  승인된 묶음을 골라 내부 문서를 읽는다. 중복 저장 이름에 번호가 붙을 수 있다. TCP stream·재조립·
  파일 내보내기의 역할과 제한된 필터 예제를 제공한다.
- **완료:** 재조립한 비공개 문서의 `pwnden{...}` 코드를 제출한다.
- **추가 정보:** 관련 HTTP 대화 선택 → 전송 객체 복원 → 압축 파일 내부 확인.
- **검증:** 실제 HTTP 응답과 내보낸 객체의 바이트 일치, 객체의 해시·압축 해제·
  코드 회수, 핵심 payload를 빠뜨린 대조 캡처의 회수 실패를 확인한다. 패킷 단위
  문자열 검색만으로 전체 코드를 찾지 못하도록 압축된 본문을 사용한다.
  공통 pcap 이미지에서 작은 합성 캡처의 HTTP 객체 내보내기를 검증했다.
  실제 문제의 HTTP 바이트 일치·checksum·sequence/ACK·불완전 캡처·재생성
  검사도 `authoring/check.py`에서 통과했다.

## 8. 서명이 맞는 납품 문서

- **의뢰:** 내용이 다른 납품 문서 사본 가운데 발신자가 실제로 서명한 원문을
  확인한다. 발신자는 검증용 공개키와 원문에 대한 분리된 서명을 따로 전달한다.
- **학습 목표:** 신뢰한 공개키로 문서의 서명을 검증해 내용 변경을 구분한다.
  분야 `cryptographic-security`, 주제 `crypto-public-keys-signatures`, category `crypto`.
- **자료:** 신뢰한 발신자의 공개키와 승인 안내, 버전별 실제 서명 두 개,
  과거 승인본·현재 승인본·변조 사본 세 개. 과거 승인본의 서명도 유효하다.
  사본의 파일명과 수정 시각만으로 원문을 고를 수 없도록 구성한다.
- **풀이:** 승인 안내의 배치·버전으로 대응하는 서명을 선택한다.
  `openssl dgst -sha256 -verify ... -signature ...`로 각 문서를 검증하고
  통과한 문서의 SHA-256을 계산한다. 공개키·서명·검증 실패·해시의 역할을
  설명한다. 수학이나 개인키 생성은 플레이어의 선수 지식으로 요구하지 않는다.
- **완료:** 검증된 원문의 해시를 `pwnden{<64자리 소문자 SHA-256>}`로 제출한다.
  제출 형식은 브리핑에 명시하며 문서에 정답 문자열을 그대로 넣지 않는다.
- **추가 정보:** 믿을 수 있는 공개키 확인 → 후보별 서명 검증 → 원문의 해시 확인.
- **검증:** 버전별 승인 원문의 검증 성공과 과거 승인본의 오답 처리,
  내용 1바이트 변경·다른 공개키·다른 서명에서 실패,
  해시와 제출값의 일치를 검사한다. 서명용 개인키는 자료 생성 때 임시 생성하고
  배포·커밋하지 않는다. 자료 재생성 후에도 같은 원문만 통과하는지 확인한다.
  공통 이미지의 digest 검증과 별도로 이 RSA/SHA-256 서명 경로를 검증한다.

## 작업 단위와 완료 기준

### 공통 시작 설명

기존 [시작 지식](../knowledge/README.md)의 `terminal-commands`, `http-messages`,
`file-paths`, `hashing`을 재사용한다. 새 설명은 첫 소비 문제와 함께 추가한다.
Git 이력, SQLite 레코드, 메타데이터, curl·JSON 요청, TCP 서비스,
응답 비교, 패킷 대화, 전자서명을 각각 풀이에 필요한 범위로 작성한다.
출력 저장·따옴표·파이프는 정답과 무관한 작은 예제로 설명한다.

### 문제별 구현

위 순서로 한 문제씩 구현·검증·커밋한다. 작업 단위에는 다음을 함께 포함한다.

1. manifest와 실제 대상·배포 자료·재생성 방법.
2. 브리핑, 필요한 공통 시작 설명, 장애물에 맞춘 추가 정보, 사건 보고서.
3. `AUTHORING.md`의 목표·선수 능력·단계별 관찰·난도 근거·대안 풀이.
4. 같은 CLI를 호출하는 `solve/solve.sh`, 정상·잘못된 입력의 대조 검사.
   서비스 문제에는 패치와 정상 기능 검사를 포함한다.
5. 작성자 실행기와 소비자 실행기의 해답 재현, 실제 PTY에서 시작 명령과 풀이 확인,
   실패·중단·재시작·정리 결과. 실행 중 새 CLI 설치 없이 완주해야 한다.

문제별 배포 자료 합계는 8MiB 이하, PCAP은 2MiB 이하, 개별 자동 해답은 기본 60초 이내를
초기 예산으로 삼는다. HTTP/TCP 문제는 컨테이너 1개에 구성한다. 각 문제의 실제
검증 시간을 작성 기록에 남기고 현재 실행기의 자원 상한에서 확인한다.

각 문제의 가벼운 검사, 작성자 실행 검증과 소비자 재현을 마친 뒤 해당 단위를 커밋한다.
소비자 검증은 직접 `validate`·`run`·`verify`·`stop`을 호출해 확인한다.
최종 묶음에서는 두 실행기의 전체 카탈로그 검증을 순서대로 수행한다.
소비자의 `tools/verify.py`는 slug 인자를 받지 않고 전체 카탈로그를 검사한다.

```sh
# challenges 저장소: <slug>는 위에서 구현한 문제 식별자
python3 -B tools/content.py --check
python3 -B tools/validate.py
python3 -B -m unittest discover -s tools
python3 -B tools/verify.py <slug>

# 묶음 완료 시, workspace 루트에서 순서대로 실행
python3 -B challenges/tools/verify.py
python3 -B platform/tools/verify.py
```

파일 자료의 제거·변조·재생성 대조 검사는 문제별 `authoring/check.py`에 있다.
소비자 CLI를 준비한 workspace 루트에서 같은 문제 이미지로 다시 실행할 수 있다.
이 검사는 작성자용이며 일반 풀이에는 Python이 필요하지 않다.

```sh
set -e
for slug in image-notes commit-trail retained-record packet-delivery signed-delivery; do
  pwnden --repo challenges exec "$slug" -- python3 -B authoring/check.py
  pwnden --repo challenges stop "$slug"
done
```

CLI와 검사 스크립트 재현은 기술 검증이다. 배포 전에는 준비된 터미널에서 처음
풀이하는 학습자의 독립 리뷰로 시작 설명·힌트·난도를 확인하고 `AUTHORING.md`에
기록한다. 그때까지 문제의 구현·기술 검증과 공개 준비 상태를 구분해 관리한다.

## 문제별 완료 기록

각 기록은 자료 대조 검사(파일 문제), 작성자 해답과 서비스 패치·정상 기능,
소비자 validate·run·verify·stop 및 실제 PTY에서 시작 명령·해답·정답/오답 제출·
Ctrl+C·재접속·종료 후 새 작업 공간·원본 보존을 확인한 결과다.
시간은 이 검사 묶음의 총 시간이며 개별 해답의 timeout과 다르다.

| 문제 | 기록 | 검증 총 시간 | 배포 자료 | 문제 단위 커밋 |
| --- | --- | --- | --- | --- |
| image-notes | [통과](../challenges/image-notes/authoring/validation.json) | 11.04초 | 1,024 B | `332c307` |
| commit-trail | [통과](../challenges/commit-trail/authoring/validation.json) | 9.63초 | 5,477 B | `b583bd1` |
| retained-record | [통과](../challenges/retained-record/authoring/validation.json) | 10.97초 | 17,134 B | `5c335d8` |
| export-gap | [통과](../challenges/export-gap/authoring/validation.json) | 48.54초 | 0 B | `bc1232b` |
| diagnostic-port | [통과](../challenges/diagnostic-port/authoring/validation.json) | 92.52초 | 0 B | `0aa450e` |
| quiet-route | [통과](../challenges/quiet-route/authoring/validation.json) | 65.93초 | 289 B | `94c5bef` |
| packet-delivery | [통과](../challenges/packet-delivery/authoring/validation.json) | 11.37초 | 5,175 B | `c870b11` |
| signed-delivery | [통과](../challenges/signed-delivery/authoring/validation.json) | 9.65초 | 1,822 B | `651cf87` |

Ncat 7.95의 응답 이후 대기는 1초 idle 제한으로 끝낸다. 자동 검사는 해당 idle
메시지와 완전한 프로토콜 응답이 함께 있을 때만 종료 코드 1을 허용한다.
SQLite 재생성은 버전별 파일 헤더 차이를 고려해 SQL 내용으로 비교한다.
ffuf 후보에 403도 포함될 수 있으므로 본문의 공개 여부를 직접 확인한다.
브라우저 화면의 시각 검사는 이 기술 검증 기록에 포함하지 않는다.

2026-10-03 최종 묶음 검증에서 기존 12개와 신규 8개를 합한 20개 카탈로그의
콘텐츠 일치·형식 검사, 작성자 회귀 테스트 65개, 작성자 전체 verify와 소비자 전체
validate·run·verify·stop을 모두 통과했다. 위 소비자 CLI로 파일 대조 검사 5개도
재현했다. 커밋에서 내보낸 배포 파일은 작업 사본과 바이트가 일치하며 합계
30,921 B다. basic·pcap 이미지 ID를 유지해 추가 CLI 설치 없이 완주했다.

## 작성자용 기술 근거

- 비특권 TCP 연결 스캔은 [Nmap TCP connect scan](https://nmap.org/book/man-port-scanning-techniques.html)의 `-sT` 경로를 사용한다.
- 후보 경로·응답 필터는 [ffuf 공식 사용법](https://github.com/ffuf/ffuf)의 FUZZ·-fs·-fr 동작을 따른다.
- 캡처 파일 읽기와 HTTP 객체 내보내기는 [TShark 공식 문서](https://www.wireshark.org/docs/man-pages/tshark.html)의 `-r`·`--export-objects`를 사용한다.
- 공개키와 분리된 서명 검증은 [OpenSSL dgst 공식 문서](https://docs.openssl.org/3.5/man1/openssl-dgst/)의 `-verify`·`-signature`를 사용한다.

공식 문서는 설계 근거다. 실제 설치 버전과 새 대상·자료의 호환성은 문제별 실행
검사에서 확정하고, 결과를 해당 문제의 작성 기록에 남긴다.
