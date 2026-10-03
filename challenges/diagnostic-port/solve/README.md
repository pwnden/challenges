## 같은 서버의 두 경로

`curl -i http://app:8000/api/recovery`로 요청하면 서버가 상태 코드 403과
`staff_access_required`라는 오류 메시지를 반환한다. 이 실습의 웹 서버는
해당 요청을 항상 거부한다. 오류 메시지에 담당자 권한이 필요하다고 나와도,
담당자 로그인이나 계정별 권한 검사를 구현한 것은 아니다.
Nmap TCP 연결 스캔에서 8000·8003·8007은 열려 있다. 8003은 건강 검사만 제공한다.

```sh
nmap --unprivileged -sT -Pn -n -p 8000-8010 app
printf 'HELP\n' | ncat -w 3 --idle-timeout 1 app 8007
printf 'STATUS\n' | ncat -w 3 --idle-timeout 1 app 8007
printf 'LIST\n' | ncat -w 3 --idle-timeout 1 app 8007
printf 'READ recovery-current\n' | ncat -w 3 --idle-timeout 1 app 8007
```

8007의 HELP는 STATUS·LIST·READ를 안내한다. STATUS의 active_resource는 현재
자료를 지정하고 LIST에는 폐기된 자료도 있다. 폐기된 자료에서도 그럴듯한 코드가
나오지만 현재 자료의 `OK pwnden{...}`가 제출값이다. 연결 후 공개된
안내만 보고 끝내지 않고, 민감한 자료 읽기가 잘못 허용됐다는 증거까지 확인한다.

## 원인과 수정

웹 서버는 복구 정보 요청을 거부하지만, 별도의 TCP 점검 서비스는 연결한 사람의
권한을 확인하지 않고 복구 자료를 읽는 READ 명령을 허용한다. 한 경로에서
읽기를 막아도 다른 경로의 접근까지 막는 것은 아니라는 점을 확인할 수 있다.
수정한 서버는 해당 자료 읽기를 거부하면서 HELP·STATUS와 HTTP 건강 검사를
유지한다. 작은 범위의 연결 조사에는 raw 패킷이나 관리자 권한이 필요하지 않다.
