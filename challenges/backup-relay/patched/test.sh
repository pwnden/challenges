#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/backup-relay-check.XXXXXX)
trap 'rm -rf "$work"' EXIT
probe() {
    local code=0
    printf '%s' "$1" | ncat -w 3 --idle-timeout 1 app 9000 > "$work/tcp" 2> "$work/ncat-error" || code=$?
    if [ "$code" != 0 ]; then
        test "$code" = 1
        grep -qx 'Ncat: Idle timeout expired (1000 ms).' "$work/ncat-error"
    fi
}
probe $'HELLO\n'
grep -qx 'BACKUP-RELAY/1' "$work/tcp"
grep -q 'commands: HELLO, AUTH <token>, STATUS, READ <name>' "$work/tcp"

probe $'STATUS\n'
grep -qx '^OK role=guest' "$work/tcp"

probe $'READ backup-current\n'
grep -q '^DENIED staff_auth_required' "$work/tcp"
if grep -q 'pwnden{' "$work/tcp"; then exit 1; fi

probe $'READ backup-retired\n'
grep -qx 'OK pwnden{retired_backup_cleared}' "$work/tcp"

probe $'AUTH wrong-token\nSTATUS\nREAD backup-current\n'
grep -qx '^DENIED bad_token' "$work/tcp"
grep -q '^OK role=guest' "$work/tcp"
grep -q '^DENIED staff_auth_required' "$work/tcp"

probe $'AUTH relay-guest-7f2c\nSTATUS\nREAD backup-current\n'
grep -qx '^OK authenticated' "$work/tcp"
grep -q '^OK role=staff' "$work/tcp"
grep -q '^OK pwnden{' "$work/tcp"

probe $'READ missing\n'
grep -q '^ERR unknown_resource' "$work/tcp"

probe 'HELLO'
grep -q '^ERR newline_required' "$work/tcp"

probe $'UNKNOWN\n'
grep -q '^ERR unsupported_command' "$work/tcp"

printf '%s\n' 'HELLO, STATUS and the retired backup stay reachable; the current backup now needs AUTH first'
