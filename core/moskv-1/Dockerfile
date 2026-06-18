# Stage 1: Build
FROM python:3.12-slim as builder

WORKDIR /build
RUN apt-get update && apt-get install -y gcc g++ make libsqlite3-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -e .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r <(pip freeze)

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . .
RUN mkdir -p /app/data && useradd -m cortexuser && chown -R cortexuser:cortexuser /app
USER cortexuser

EXPOSE 8000
CMD ["uvicorn", "src.moskv_1.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
