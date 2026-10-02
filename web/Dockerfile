FROM --platform=$BUILDPLATFORM node:24.21.0-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6 AS check
WORKDIR /web
RUN npm install --global --no-audit --no-fund pnpm@12.8.1
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY web/ ./
COPY challenges/ /challenges/
RUN pnpm typecheck && pnpm test
