FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user and switch to it
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 appuser
USER appuser

# Create a directory for streamlit config with the correct permissions
RUN mkdir -p /home/appuser/.streamlit

# Copy Streamlit configuration file (optional)
COPY .streamlit/config.toml /home/appuser/.streamlit/config.toml

# Expose the port that Streamlit runs on
EXPOSE 5000

# Define the entrypoint
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]