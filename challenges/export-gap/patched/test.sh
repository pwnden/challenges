#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/export-gap-check.XXXXXX)
trap 'rm -rf "$work"' EXIT
base=http://app:8000
request() { curl --silent --show-error --max-time 5 -o "$work/body" -w '%{http_code}' "$@"; }
test "$(request "$base/healthz")" = 200
test "$(request -H 'Content-Type: application/json' -d '{"note_id":42}' "$base/api/exports")" = 401
test "$(request -H 'Content-Type: application/json' -d '{"username":"guest","password":"wrong"}' "$base/api/login")" = 401
test "$(request -c "$work/cookies" -H 'Content-Type: application/json' -d '{"username":"guest","password":"lab-guest"}' "$base/api/login")" = 200
test "$(request -b "$work/cookies" "$base/api/catalog")" = 200
if grep -q 'pwnden{' "$work/body"; then exit 1; fi
test "$(request -b "$work/cookies" "$base/api/notes/7")" = 200
jq -e '.owner == "guest"' "$work/body" >/dev/null
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":7}' "$base/api/exports")" = 200
jq -e '.redacted == true and (.export | has("body") | not)' "$work/body" >/dev/null
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":7,"format":"full"}' "$base/api/exports")" = 200
jq -e '.export.owner == "guest" and .export.body == "Meeting is on Friday."' "$work/body" >/dev/null
test "$(request -b "$work/cookies" "$base/api/notes/42")" = 403
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":42}' "$base/api/exports")" = 200
jq -e '.redacted == true and (.export | has("body") | not)' "$work/body" >/dev/null
if grep -q 'pwnden{' "$work/body"; then exit 1; fi
for body in '{"note_id":42,"format":"full"}' '{"note_id":42,"format":"full","owner":"guest"}'; do
    test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d "$body" "$base/api/exports")" = 403
    if grep -q 'pwnden{' "$work/body"; then exit 1; fi
done
for body in '{"note_id":"42"}' '{"note_id":true}' '{"note_id":42,"format":[]}' '{"note_id":42,"format":"binary"}' '[]' 'invalid'; do
    test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d "$body" "$base/api/exports")" = 400
done
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":999}' "$base/api/exports")" = 404
test "$(request -H 'Cookie: session=forged' "$base/api/notes/7")" = 401
printf '%s\n' 'Normal note reads/exports preserved; other owners and invalid/unauthenticated requests rejected'
