FROM --platform=$BUILDPLATFORM node:24.21.0-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6 AS frontend
WORKDIR /web
RUN npm install --global --no-audit --no-fund pnpm@12.8.1
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY web/ ./
COPY challenges/note-vault/vulnerable/web/ /scenario/
RUN SCENARIO_DIR=/scenario pnpm build

FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b
ARG POLICY=vulnerable/policy.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY challenges/note-vault/vulnerable/app.py /app/app.py
COPY challenges/note-vault/${POLICY} /app/policy.py
COPY web/__init__.py web/server.py /app/web/
COPY --from=frontend /web/dist/ /app/public/
USER 10001:10001
CMD ["python3", "/app/app.py"]
