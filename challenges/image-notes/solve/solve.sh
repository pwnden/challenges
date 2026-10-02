#!/bin/bash
set -euo pipefail
file files/notice.png | grep -q 'PNG image data'
exiftool -s3 -Comment files/notice.png | jq -er '.internal_memo.recovery_code | select(startswith("pwnden{"))'
