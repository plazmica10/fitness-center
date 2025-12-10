FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies and create a venv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r /app/requirements.txt

# Copy source
COPY . /app

FROM python:3.11-slim
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# Copy venv and app from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
