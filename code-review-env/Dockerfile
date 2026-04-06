# ── Builder ────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies into a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# ── Runtime ────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy the venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY . .

# Environment variables (override at runtime)
ENV OPENAI_API_KEY=""
ENV PYTHONUNBUFFERED=1

# Default entrypoint: run inference on a random easy task
ENTRYPOINT ["python", "inference.py"]
CMD ["--difficulty", "easy"]
