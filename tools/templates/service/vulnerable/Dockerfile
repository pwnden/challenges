FROM --platform=$BUILDPLATFORM node:24.21.0-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6 AS frontend
WORKDIR /web
RUN npm install --global --no-audit --no-fund pnpm@12.8.1
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY web/ ./
COPY challenges/{{SLUG_PATH}}/vulnerable/web/ /scenario/
RUN SCENARIO_DIR=/scenario pnpm build

FROM {{IMAGE}}
ARG APP_SOURCE=vulnerable/app.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY challenges/{{SLUG_PATH}}/${APP_SOURCE} /app/app.py
COPY web/__init__.py web/server.py /app/web/
COPY --from=frontend /web/dist/ /app/public/
USER 10001:10001
CMD ["python3", "/app/app.py"]
