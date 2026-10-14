# syntax=docker/dockerfile:1
FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b AS build
# A timestamped, signed Debian repository keeps the compiler (and the stack layout
# and PLT/GOT addresses it produces) reproducible; see images/cli/Dockerfile for
# the same pattern.
RUN sed -i 's|http://deb.debian.org/debian-security|https://snapshot.debian.org/archive/debian-security/20261002T000000Z|;s|http://deb.debian.org/debian|https://snapshot.debian.org/archive/debian/20261002T000000Z|' /etc/apt/sources.list.d/debian.sources \
    && printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99snapshot \
    && apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY vulnerable/winlibc.c vulnerable.c
COPY patched/winlibc.c patched.c
RUN gcc -O0 -fno-stack-protector -no-pie -z noexecstack -o winlibc_vulnerable vulnerable.c \
    && gcc -O0 -fno-stack-protector -no-pie -z noexecstack -o winlibc_patched patched.c

FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b
ARG POLICY=vulnerable/policy.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY vulnerable/app.py /app/app.py
COPY ${POLICY} /app/policy.py
COPY --from=build /src/winlibc_vulnerable /app/winlibc_vulnerable
COPY --from=build /src/winlibc_patched /app/winlibc_patched
RUN chmod 755 /app/winlibc_vulnerable /app/winlibc_patched
USER 10001:10001
CMD ["python3", "/app/app.py"]
