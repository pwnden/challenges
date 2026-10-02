#!/bin/bash
set -euo pipefail
work=$(mktemp -d /tmp/commit-trail.XXXXXX)
trap 'rm -rf "$work"' EXIT
tar -xzf files/source.tar.gz -C "$work"
repo="$work/source"
path=$(sed -n 's/^private_config=//p' "$repo/config/release.txt")
deleted=$(git -C "$repo" log --diff-filter=D --format=%H -- "$path")
test -n "$deleted"
git -C "$repo" show "$deleted^:$path" | rg -o 'pwnden\{[^}]+\}'
