#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/reused-cipher-memo-check.XXXXXX)
trap 'rm -rf "$work"' EXIT
probe() {
    local code=0
    printf '%s' "$1" | ncat -w 3 --idle-timeout 1 app 9200 > "$work/tcp" 2> "$work/ncat-error" || code=$?
    if [ "$code" != 0 ]; then
        test "$code" = 1
        grep -qx 'Ncat: Idle timeout expired (1000 ms).' "$work/ncat-error"
    fi
}

probe $'HELLO\n'
grep -qx 'MEMO-VAULT/1' "$work/tcp"
grep -q 'commands: HELLO, MEMO, CHECK <hex>' "$work/tcp"

probe $'MEMO\n'
sealed=$(grep -o '^OK [0-9a-f]*' "$work/tcp" | cut -d' ' -f2)
test -n "$sealed"
zeros=$(python3 -c "print('00' * (len('$sealed') // 2))")

probe "CHECK $zeros"$'\n'
first=$(grep -o '^OK [0-9a-f]*' "$work/tcp" | cut -d' ' -f2)
test -n "$first"

probe "CHECK $zeros"$'\n'
second=$(grep -o '^OK [0-9a-f]*' "$work/tcp" | cut -d' ' -f2)
test -n "$second"

# A fresh random pad per CHECK call means two identical requests disagree.
if [ "$first" = "$second" ]; then exit 1; fi

# The vulnerable recovery (zero-pad CHECK XOR MEMO) no longer yields the flag.
recovered=$(python3 -c "
sealed = bytes.fromhex('$sealed')
pad = bytes.fromhex('$first')
plain = bytes(a ^ b for a, b in zip(sealed, pad))
print(plain)
")
if [[ "$recovered" == *"pwnden{"* ]]; then exit 1; fi

probe $'CHECK zz\n'
grep -qx 'ERR invalid_hex' "$work/tcp"

probe "CHECK $(python3 -c "print('00' * 129)")"$'\n'
grep -q '^ERR length_1_to_' "$work/tcp"

probe $'UNKNOWN\n'
grep -qx 'ERR unsupported_command' "$work/tcp"

printf '%s\n' 'CHECK no longer reuses the pad MEMO used to seal the memo'
