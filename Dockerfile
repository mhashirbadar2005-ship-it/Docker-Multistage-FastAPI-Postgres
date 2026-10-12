# Stage 1: "builder" — installs dependencies only.

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# --user installs into a self-contained folder (~/.local) so the
# next stage can copy just that folder — no pip cache, no compilers.

RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: "runtime" — this is the image that actually ships.

FROM python:3.11-slim AS runtime

# Runtime needs libpq itself (the client library), but NOT the
# -dev headers used only for compiling — that's the size saving.

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Run as a non-root user — basic but important container security.

RUN useradd --create-home appuser
WORKDIR /app

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser main.py .

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


