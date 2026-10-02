#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/signed-delivery.XXXXXX)
trap 'rm -rf "$work"' EXIT
valid=()
signature=$(sed -n 's/^signature=//p' files/trust-note.txt)
test "$signature" = delivery-v2.sig
for document in files/copy-*.txt; do
    if openssl dgst -sha256 -verify files/sender-public.pem -signature "files/$signature" "$document" > "$work/verification" 2>&1; then
        valid+=("$document")
    fi
done
test "${#valid[@]}" = 1
grep -qx 'Batch: LAB-17' "${valid[0]}"
grep -qx 'Revision: 2' "${valid[0]}"
digest=$(sha256sum "${valid[0]}" | cut -d ' ' -f 1)
printf 'pwnden{%s}\n' "$digest"
