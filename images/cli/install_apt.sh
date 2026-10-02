#!/bin/sh
set -eu
lock=$1
mkdir -p /tmp/toolbox-debs
chmod 1777 /tmp/toolbox-debs
awk '!/^#/ {print $1, $2, $3, $4}' "$lock" | xargs -n 4 -P 4 sh -ec '
    installed=$(dpkg-query -W -f='"'"'${Version}'"'"' "$1" 2>/dev/null || true)
    if [ "$installed" = "$2" ]; then exit 0; fi
    /usr/lib/apt/apt-helper -o Acquire::https::CaInfo=/etc/ssl/certs/ca-certificates.crt \
        download-file "$3" "/tmp/toolbox-debs/$1.deb" "SHA256:$4" >/dev/null
' sh
# Use a local repository so APT can order Pre-Depends before unpacking hundreds
# of archives. All bytes were authenticated against the signed-index lock above.
for archive in /tmp/toolbox-debs/*.deb; do
    dpkg-deb -f "$archive"
    printf 'Filename: ./%s\nSize: %s\nSHA256: %s\n\n' \
        "${archive##*/}" "$(wc -c < "$archive")" "$(sha256sum "$archive" | cut -d ' ' -f 1)"
done > /tmp/toolbox-debs/Packages
printf 'deb [trusted=yes] file:/tmp/toolbox-debs ./\n' > /tmp/toolbox-sources.list
set --
while IFS="$(printf '\t')" read -r package version url sha; do
    case "$package" in '#'*) continue ;; esac
    set -- "$@" "$package=$version"
done < "$lock"
apt-get -o Dir::Etc::sourcelist=/tmp/toolbox-sources.list -o Dir::Etc::sourceparts=- update
apt-get -o Dir::Etc::sourcelist=/tmp/toolbox-sources.list -o Dir::Etc::sourceparts=- \
    --yes --no-install-recommends install "$@"
dpkg-query -W > /opt/package-versions.txt
while IFS="$(printf '\t')" read -r package version url sha; do
    case "$package" in '#'*) continue ;; esac
    actual=$(dpkg-query -W -f='${Version}' "$package")
    test "$actual" = "$version"
done < "$lock"
rm -rf /tmp/toolbox-debs /tmp/toolbox-sources.list /var/lib/apt/lists/* /var/cache/apt/archives/*.deb
