#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/diagnostic-port-check.XXXXXX)
trap 'rm -rf "$work"' EXIT
test "$(curl -sS --max-time 5 -o "$work/http" -w '%{http_code}' http://app:8000/healthz)" = 200
test "$(curl -sS --max-time 5 -o "$work/http" -w '%{http_code}' http://app:8000/api/recovery)" = 403
if grep -q 'pwnden{' "$work/http"; then exit 1; fi
probe() {
    local code=0
    printf '%s' "$1" | ncat -w 3 --idle-timeout 1 app 8007 > "$work/tcp" 2> "$work/ncat-error" || code=$?
    if [ "$code" != 0 ]; then
        test "$code" = 1
        grep -qx 'Ncat: Idle timeout expired (1000 ms).' "$work/ncat-error"
    fi
    grep -qx 'LAB-DIAG/1' "$work/tcp"
    test "$(wc -l < "$work/tcp")" = 2
}
probe $'HELP\n'
grep -q 'commands: HELP, STATUS, READ' "$work/tcp"
probe $'STATUS\n'
grep -q '^OK board=ready' "$work/tcp"
probe $'READ recovery\n'
grep -q '^DENIED protected_recovery' "$work/tcp"
if grep -q 'pwnden{' "$work/tcp"; then exit 1; fi
probe $'READ missing\n'
grep -q '^ERR unknown_resource' "$work/tcp"
probe 'HELP'
grep -q '^ERR newline_required' "$work/tcp"
probe $'UNKNOWN\n'
grep -q '^ERR unsupported_command' "$work/tcp"
nmap --unprivileged -sT -Pn -n -p 8000,8007 --max-retries 1 -oG "$work/scan" app >/dev/null
grep -q '8000/open/tcp' "$work/scan"
grep -q '8007/open/tcp' "$work/scan"
nmap --unprivileged -sT -Pn -n -p 8008 --max-retries 1 app > "$work/closed"
grep -q 'closed' "$work/closed"
printf '%s\n' 'HTTP and diagnostic health preserved; sensitive READ, incomplete and invalid requests handled'
