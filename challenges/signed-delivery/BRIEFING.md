::message{from="온전한서명"}
납품 문서 사본의 수량과 도착지가 서로 달라요. 따로 받은 공개키와 서명으로 발신자가 승인한 원문을 확인해 주세요.
::

온전한서명은 납품 문서를 받는 담당자다. 발신자는 버전별로 문서를 승인하고
서명을 별도로 보냈다. 현재 묶음에는 과거 승인본과 현재 승인본, 변경된 사본이 섞였다.
이름이나 수정 시각만으로 승인된 사본을 고르면 다른 수량이나 도착지를 처리할 수 있다.

온전한서명은 발신자에게 확인한 검증용 공개키와 분리된 서명을 길드에 맡겼다.
이 실습에서 제공된 키는 신뢰한 경로로 전달된 발신자의 키다. 서명은 원문에
대한 것이다. 과거 승인본의 서명도 유효하므로 서명 성공만으로 현재 납품에
적용할 수 없다. 신뢰한 승인 안내의 배치와 버전을 먼저 확인한다. 실습용 키와 문서는
이 문제를 위해 생성했으며 실제 업무용 개인키는 사용하지 않는다.

::objective
승인 안내와 신뢰한 공개키로 현재 승인 원문을 고르고, 그 원문의 SHA-256을 확인하자.
::

::resources{title="문서와 검증 자료"}
- `files/copy-a.txt`, `files/copy-b.txt`, `files/copy-c.txt`는 내용이 다른 사본이다.
- `files/sender-public.pem`은 신뢰한 발신자의 공개키다.
- `files/delivery.sig`와 `files/delivery-v2.sig`는 버전별 RSA/SHA-256 분리 서명이다.
- `files/trust-note.txt`는 신뢰한 승인 배치·버전과 각 서명의 대응 관계를 정한다.

먼저 승인 안내를 읽고 현재 버전에 대응하는 서명을 고른다. 아래는 검증 형식이며
서명 파일을 선택한 값으로 바꿔 각 사본의 결과를 비교하자. 사본은 편집하지 않는다.

```sh
cat files/trust-note.txt
openssl dgst -sha256 -verify files/sender-public.pem -signature files/선택한서명 files/copy-a.txt
```

검증을 통과한 파일에 `sha256sum 파일경로`를 실행한다. 출력의 첫 64자리 소문자
해시만 제출 형식 안에 넣는다. 파일명과 공백은 포함하지 않는다.
::

::knowledge{concepts="terminal-commands,detached-signatures"}
::

::submission
검증된 원문의 해시를 `pwnden{64자리 소문자 SHA-256}` 형식으로 제출하자.
문서에 정답 문자열이 그대로 들어 있지는 않다.
::
