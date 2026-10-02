#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/packet-delivery.XXXXXX)
trap 'rm -rf "$work"' EXIT
tshark -r files/delivery.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri >&2
mkdir "$work/objects"
tshark -r files/delivery.pcap --export-objects "http,$work/objects" >&2
valid=()
for object in "$work"/objects/*; do
    if tar -xzOf "$object" public/receipt.json > "$work/receipt.json" 2>/dev/null; then
        if jq -e '.batch == "LAB-17" and .revision == 2 and .status == "approved"' "$work/receipt.json" >/dev/null; then
            valid+=("$object")
        fi
    fi
done
test "${#valid[@]}" = 1
file "${valid[0]}" >&2
tar -tzf "${valid[0]}" >&2
tar -xzOf "${valid[0]}" internal/recovery.txt | rg -o 'pwnden\{[^}]+\}'
