#!/bin/sh
set -eu
# Package file capabilities can make execve fail with a zero capability bounding
# set (notably Kali's Nmap). Images provide ordinary user-space binaries.
getcap -r /usr /opt 2>/dev/null | while read -r filename capabilities; do
    setcap -r "$filename"
done
find /usr /opt -type f -perm /6000 -exec chmod a-s {} +
