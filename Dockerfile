FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libpq-dev \
    postgresql-client \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY railway-requirements.txt requirements.txt

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports data temp

# Set production environment variables
ENV ENVIRONMENT=production
ENV SAP_SSL_VERIFY=true
ENV SALESFORCE_TIMEOUT=30
ENV SAP_REQUEST_TIMEOUT=30
ENV OIDC_TIMEOUT=30

# Expose port 5000 for production
EXPOSE 5000

# Health check
HEALTHCHECK CMD curl --fail http://localhost:5000/_stcore/health || exit 1

# Run application on port 5000
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]