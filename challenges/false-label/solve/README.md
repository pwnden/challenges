## 조사 순서

1. `od -An -tx1 -N8 files/banner.png`로 앞부분을 확인한다.
2. 시작은 `1f 8b 08`이다. PNG의 식별 바이트와 다르고 gzip에 해당한다.
3. `tar -tzf files/banner.png`로 실제 묶음 구조가 읽히는지 확인한다.
4. notes/transfer.txt와 recovery/key.txt가 나타난다.
5. `tar -xOzf files/banner.png recovery/key.txt`로 복구 키를 화면에 출력한다.
6. `pwnden{bytes_tell_the_story}`를 제출한다.

## 확인된 원리

이름이 banner.png여도 내부 바이트는 gzip으로 압축된 tar다.
식별 바이트로 형식을 추정하고, 해당 형식의 도구가 구조를 읽는 것으로 확인했다.
압축 자체는 내부 키를 기밀로 만들지 않는다.

명령의 대문자 O는 내용을 화면으로 내보낸다. 파일을 풀어 저장할 필요 없이
조사할 자료만 읽을 수 있다. 형식 검사에서도 확장자와 내용 검증을 함께 사용한다.
