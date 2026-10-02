FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b
ARG POLICY=vulnerable/policy.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY vulnerable/app.py /app/app.py
COPY ${POLICY} /app/policy.py
USER 10001:10001
CMD ["python3", "/app/app.py"]
