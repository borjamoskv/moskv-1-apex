FROM python:3.12-slim

WORKDIR /app

# Install native dependencies for cryptography / LanceDB / SQLite
RUN apt-get update && apt-get install -y gcc g++ make curl libsqlite3-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY . .

# Initialize deterministic database volume mount point
RUN mkdir -p /app/data

# Use a non-root user for security
RUN useradd -m cortexuser && chown -R cortexuser:cortexuser /app
USER cortexuser

EXPOSE 8000

# Lanza el bridge SSE y el motor FastAPI
CMD ["uvicorn", "src.moskv_1.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
