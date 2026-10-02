#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/packet-delivery.XXXXXX)
trap 'rm -rf "$work"' EXIT
tshark -r files/delivery.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri >&2
mkdir "$work/objects"
tshark -r files/delivery.pcap --export-objects "http,$work/objects" >&2
file "$work/objects/delivery.tar.gz" >&2
tar -tzf "$work/objects/delivery.tar.gz" >&2
tar -xzOf "$work/objects/delivery.tar.gz" internal/recovery.txt | rg -o 'pwnden\{[^}]+\}'
