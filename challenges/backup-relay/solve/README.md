## 조사 결과

중계기는 `STATUS`에는 인증 상태를 반영하지만, `READ`는 인증 여부를 전혀
확인하지 않았다. `AUTH`를 한 번도 보내지 않고 `READ backup-current`만 보내면
현재 백업의 flag가 그대로 돌아온다.

## 조사 과정

`ncat -w 3 --idle-timeout 1 app 9000`으로 접속하면 `BACKUP-RELAY/1` 배너가
먼저 온다. `HELLO`를 보내면 지원 명령 목록(`HELLO`, `AUTH <token>`, `STATUS`,
`READ <name>`)을 알려 준다.

`STATUS`만 먼저 보내면 `OK role=guest`가 온다. 제공된 테스트 토큰으로
`AUTH relay-guest-7f2c`를 보낸 뒤 다시 `STATUS`를 보내면 `OK role=staff`로
바뀐다. 중계기가 연결마다 인증 여부를 실제로 기억한다는 뜻이다.

같은 연결에서 `AUTH`를 한 번도 보내지 않고 바로 `READ backup-current`를
보내면 `DENIED staff_auth_required`가 아니라 `OK pwnden{...}`가 온다.
`READ backup-retired`(폐기 백업, 제출 대상 아님)는 인증 여부와 무관하게 항상
같은 값을 돌려주므로 대조군이 된다. `STATUS`가 인증을 확인하는 것과 달리
`READ`는 인증 여부를 전혀 확인하지 않는다는 결론은 이 둘의 차이로 뒷받침된다.

## 의뢰 완료 확인

새 연결에서 `HELLO`만 보낸 뒤 바로 `READ backup-current`를 보내면 현재
실행의 `pwnden{...}` flag를 얻는다. `solve/solve.py`가 같은 순서로 접속해
이 값을 표준 출력에 그대로 출력한다.

## 드러난 보안 원리

여러 단계로 이루어진 프로토콜에서는 각 명령이 "지금 상태에서 허용되는
명령인가"를 스스로 확인해야 한다. 이 중계기는 세션의 인증 상태를 실제로
기억했지만(`STATUS`가 이를 보여 준다), `READ`를 처리하는 코드가 그 상태를
읽지 않아 안내한 순서를 지키지 않아도 보호된 자료를 읽을 수 있었다.
수정한 서버는 `READ backup-current`를 처리하기 전에 같은 `authenticated`
상태를 확인하며, `patched/test.sh`가 AUTH 없이는 거부되고 올바른 토큰으로
AUTH한 뒤에만 현재 백업을 읽을 수 있음을 확인한다. `backup-retired`와
오류 응답은 패치 전후로 그대로 유지된다.
