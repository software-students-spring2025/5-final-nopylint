# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-slim AS base

# Don’t write .pyc files and don’t buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy and install dependencies
# requirements.txt lives in web_app/
COPY web_app/requirements.txt ./requirements.txt
RUN python -m pip install -r requirements.txt

# Copy application code into a web_app package and the Pi agent package
COPY web_app/ ./web_app/
COPY raspberry_pi/ ./raspberry_pi/

# Ensure Python can import modules from /app
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Fix permissions so appuser can write cache/database files
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user
USER appuser

WORKDIR /app/web_app

EXPOSE 4000

CMD ["python", "app.py"]


