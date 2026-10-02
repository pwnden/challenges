#!/bin/bash
set -euo pipefail
file files/notice.png | grep -q 'PNG image data'
receipt=$(exiftool -s3 -Description files/notice.png)
exiftool -s3 -Comment files/notice.png | jq -er --argjson receipt "$receipt" '
  [.records[] | select(.asset_id == $receipt.asset_id and .revision == $receipt.revision and .state == "active") | .recovery_code]
  | select(length == 1) | .[0]
'
