#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/commit-trail.XXXXXX)
trap 'rm -rf "$work"' EXIT
tar -xzf files/source.tar.gz -C "$work"
repo="$work/source"
deleted=$(git -C "$repo" log --all --diff-filter=D --format=%H -- config/runtime.env)
test -n "$deleted"
git -C "$repo" show "$deleted^:config/runtime.env" | rg -o 'pwnden\{[^}]+\}'
