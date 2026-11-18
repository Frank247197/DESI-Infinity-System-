# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - PRODUCTION DOCKERFILE
# Multi-Stage Build for High-Performance Computational Biology
# ============================================================

# Stage 1: Build and compile dependencies
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install core scientific libraries
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime container image
FROM python:3.10-slim AS runtime

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Copy source repository code
COPY . /app

# Ensure user local bin is in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Default execution command verifying system initialization
CMD ["python", "physics_energy.py"]
