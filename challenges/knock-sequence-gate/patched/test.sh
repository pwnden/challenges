#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/knock-sequence-gate-check.XXXXXX)
trap 'rm -rf "$work"' EXIT
knock() {
    local code=0
    ncat -w 3 --idle-timeout 1 app "$1" < /dev/null > "$work/knock" 2> "$work/knock-error" || code=$?
    if [ "$code" != 0 ]; then
        test "$code" = 1
        grep -qx 'Ncat: Idle timeout expired (1000 ms).' "$work/knock-error"
    fi
}
gate() {
    local code=0
    ncat -w 3 --idle-timeout 1 app 7000 < /dev/null > "$work/gate" 2> "$work/gate-error" || code=$?
    if [ "$code" != 0 ]; then
        test "$code" = 1
        grep -qx 'Ncat: Idle timeout expired (1000 ms).' "$work/gate-error"
    fi
}

# No knocks yet: the gate stays locked.
gate
grep -qx 'DENIED not_unlocked' "$work/gate"

# A plausible but wrong guess -- the ascending scan order that unlocked the
# vulnerable service -- must not unlock the patched one.
knock 7001; knock 7002; knock 7003
gate
grep -qx 'DENIED not_unlocked' "$work/gate"

# The real required order (7003 -> 7001 -> 7002) still works.
knock 7003; knock 7001; knock 7002
gate
grep -q '^OK pwnden{' "$work/gate"

printf '%s\n' 'the gate only opens for the exact required knock order'
