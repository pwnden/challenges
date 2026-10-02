# syntax=docker/dockerfile:1
FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b AS basic
ENV DEBIAN_FRONTEND=noninteractive PIP_DISABLE_PIP_VERSION_CHECK=1
# Timestamped, signed Debian repositories keep dependency resolution stable.
RUN sed -i 's|http://deb.debian.org/debian-security|https://snapshot.debian.org/archive/debian-security/20261002T000000Z|;s|http://deb.debian.org/debian|https://snapshot.debian.org/archive/debian/20261002T000000Z|' /etc/apt/sources.list.d/debian.sources \
    && printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99snapshot \
    && apt-get update && apt-get install -y --no-install-recommends \
       bash-completion less file binutils xxd unzip zip 7zip ripgrep jq curl openssl git \
       nmap ncat sqlite3 libimage-exiftool-perl ffuf socat bind9-dnsutils openssh-client \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --home-dir /home/pwnden --shell /bin/bash pwnden \
    && dpkg-query -W > /opt/package-versions.txt
ENV HOME=/home/pwnden XDG_CACHE_HOME=/tmp/.cache POCL_CACHE_DIR=/tmp/pocl-cache POCL_MAX_PTHREAD_COUNT=2 OMP_NUM_THREADS=2
USER 10001:10001
WORKDIR /challenge
CMD ["/bin/bash"]

FROM basic AS lab
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    smbclient ldap-utils redis-tools postgresql-client mariadb-client \
    tshark tcpdump sleuthkit qpdf poppler-utils pngcheck steghide foremost yara \
    john hashcat pocl-opencl-icd clinfo strace gdb lldb afl++ gcc make patchelf \
    pax-utils hydra ncrack sqlmap iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.lock /opt/requirements.lock
RUN pip install --no-cache-dir -r /opt/requirements.lock \
    && dpkg-query -W > /opt/package-versions.txt && pip freeze > /opt/python-versions.txt
USER 10001:10001

# The default build adds only the offline packet reader to the basic toolbox.
FROM basic AS pcap
USER root
RUN apt-get update && apt-get install -y --no-install-recommends tshark \
    && rm -rf /var/lib/apt/lists/* \
    && dpkg-query -W > /opt/package-versions.txt
USER 10001:10001
