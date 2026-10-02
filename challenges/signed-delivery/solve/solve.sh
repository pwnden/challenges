#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/signed-delivery.XXXXXX)
trap 'rm -rf "$work"' EXIT
valid=()
for document in files/copy-*.txt; do
    if openssl dgst -sha256 -verify files/sender-public.pem -signature files/delivery.sig "$document" > "$work/verification" 2>&1; then
        valid+=("$document")
    fi
done
test "${#valid[@]}" = 1
digest=$(sha256sum "${valid[0]}" | cut -d ' ' -f 1)
printf 'pwnden{%s}\n' "$digest"
