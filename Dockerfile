FROM python:3.12-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Copy requirements first (cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy source
COPY app/ .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1


# Production uvicorn (NO --reload)
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]



