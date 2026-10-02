## 같은 서버의 두 경로

`curl -i http://app:8000/api/recovery`는 403과 담당자 권한 필요 오류를 반환한다.
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

정식 HTTP의 보호와 점검 listener의 보호가 별개였다. 점검 기능은 같은
네트워크에 연결된 사람을 내부 담당자로 간주하고 민감한 READ를 허용했다.
수정한 서버는 해당 자료 읽기를 거부하면서 HELP·STATUS와 HTTP 건강 검사를
유지한다. 작은 범위의 연결 조사에는 raw 패킷이나 관리자 권한이 필요하지 않다.
