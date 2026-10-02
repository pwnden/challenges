#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/quiet-route-check.XXXXXX)
trap 'rm -rf "$work"' EXIT
for path in does-not-exist another-missing missing-3; do
    test "$(curl -sS --max-time 5 -o "$work/$path" -w '%{http_code}' "http://app:8000/$path")" = 200
    jq -e '.view == "fallback"' "$work/$path" >/dev/null
    cmp "$work/does-not-exist" "$work/$path"
done
size=$(wc -c < "$work/does-not-exist")
ffuf -w files/paths.txt -u http://app:8000/FUZZ -fs "$size" -t 2 -rate 10 -maxtime 15 -timeout 3 -noninteractive -of json -o "$work/candidates.json" >/dev/null 2>&1
jq -e '[.results[].url | split("/")[-1]] | sort == ["healthz","help","ops-check"]' "$work/candidates.json" >/dev/null
jq -e '[.results[] | select(.url | endswith("/ops-check"))] | length == 1 and .[0].status == 403' "$work/candidates.json" >/dev/null
for path in / /help /healthz; do
    test "$(curl -sS --max-time 5 -o "$work/body" -w '%{http_code}' "http://app:8000$path")" = 200
    jq -e 'type == "object"' "$work/body" >/dev/null
    if grep -q 'pwnden{' "$work/body"; then exit 1; fi
done
for path in /ops-check '/ops-check?role=staff'; do
    test "$(curl -sS --max-time 5 -H 'X-Role: staff' -o "$work/body" -w '%{http_code}' "http://app:8000$path")" = 403
    jq -e '.error == "staff_access_required"' "$work/body" >/dev/null
    if grep -q 'pwnden{' "$work/body"; then exit 1; fi
done
printf '%s\n' 'Fallback and public functions preserved; candidate filter and private-route denial passed'
