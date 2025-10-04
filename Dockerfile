# ================================
# Stage 1: Base image
# ================================
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Prevent interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# ================================
# Stage 2: System dependencies
# ================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-jdk \
    git \
    curl \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ================================
# Stage 3: Copy & install Python dependencies
# ================================
# COPY requirements.txt .
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python packages
# RUN pip install --no-cache-dir -r requirements.txt
RUN bash -c "pip install --no-cache-dir -r requirements.txt && PYTHONPATH=. pytest app/tests"


# ================================
# Stage 4: Copy application code
# ================================
COPY . .

# ================================
# Stage 5: Expose ports
# ================================
# FastAPI backend
EXPOSE 8000
# Gradio UI
EXPOSE 7895

# ================================
# Stage 6: Default command
# ================================
# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
