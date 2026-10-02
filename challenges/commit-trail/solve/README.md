## 조사 과정

묶음을 작업 폴더에 풀면 현재의 `config/example.env`에는 키를 입력하라는 예제만
있다. release.txt는 lab-v2와 config/worker.env를 기록한다. Git 이력에는 키 교체와
runtime.env에서 worker.env로 이름을 변경한 뒤 공개 전에 worker.env를 삭제한 기록이
보인다. 파일 삭제는 현재 상태의 조치이며 과거 커밋의 내용을 지우지 않는다.

저장소에서 다음 순서로 삭제 전 파일을 읽는다.

```sh
cat config/release.txt
git log --all --oneline -- config/worker.env
git log --follow --oneline -- config/worker.env
git show 삭제커밋ID^:config/worker.env
```

`RECOVERY_KEY`는 `pwnden{deleted_file_live_history}`다. Git에 저장된 객체가
배포 묶음에도 들어갔으므로, 현재 파일만 검토한 배포에서는 내부 값이 남는다.
이전 lab-v1의 키는 교체된 값이다. 전체 이력의 첫 코드만 골라서는 이번 배포의
키를 확정할 수 없다. 이름 변경과 교체 순서를 확인해 삭제 직전 값을 선택한다.

## 조치

실제 비밀이 노출됐다면 우선 교체하고, 공개할 이력과 배포 자료의 범위를 검토한다.
이력 정리를 수행했더라도 이미 전달된 사본이나 다른 복사본까지 회수됐다고
단정할 수 없다. 현재 파일의 삭제와 비밀의 폐기·배포 이력 정리는 별도 작업이다.
