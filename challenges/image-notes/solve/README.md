## 조사와 결과

`file files/notice.png`는 정상 PNG로 판별한다. 확장자를 바꾼 파일이 아니라,
실제 이미지에 화면 밖의 속성이 붙은 경우다. 배포 규칙은 픽셀 디자인만 공개하고
복구 코드와 운영 메모는 내부에 남기도록 정한다.

`exiftool files/notice.png`에서 Comment 속성을 발견한다. 다음처럼 JSON을 읽는다.

```sh
exiftool -s3 -Comment files/notice.png | jq '.internal_memo'
exiftool -s3 -Comment files/notice.png | jq -r '.internal_memo.recovery_code'
```

출력은 `pwnden{picture_pixels_are_not_all}`이다. 코드가 그림의 픽셀과 별도로
파일에 포함됐으므로 공개 파일을 받은 사람도 읽을 수 있다.

## 확인한 원리와 조치

이미지를 눈으로 검토하는 것만으로 파일의 공개 범위를 확인할 수는 없다.
내보내기에서 허용한 속성만 남기고, 별도 사본의 속성과 픽셀을 함께 검사해야 한다.
실제 복구 코드가 노출됐다면 코드도 교체한다. 메타데이터를 제거한 대조 파일은
같은 픽셀을 유지하면서 복구 코드 속성을 잃는다.
