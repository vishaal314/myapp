FROM python:3.11-slim

WORKDIR /app

# Install dependencies for textract and other system libraries including curl for health checks
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    antiword \
    unrtf \
    tesseract-ocr-all \
    libreoffice \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from pyproject.toml
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'streamlit>=1.44.1' \
    'beautifulsoup4>=4.8.2' \
    'dnspython>=2.7.0' \
    'matplotlib>=3.10.1' \
    'openai>=1.75.0' \
    'pandas>=2.2.3' \
    'plotly>=6.0.1' \
    'psycopg2-binary>=2.9.10' \
    'pypdf2>=3.0.1' \
    'python-whois>=0.9.5' \
    'reportlab>=4.4.0' \
    'requests>=2.32.3' \
    'stripe>=12.0.0' \
    'textract>=1.6.5' \
    'tldextract>=5.2.0' \
    'trafilatura>=2.0.0'

# Create directory structure
RUN mkdir -p /app/services /app/utils /app/translations /app/reports /app/uploads /app/database

# Copy application files
COPY app.py .
COPY services/ ./services/
COPY utils/ ./utils/
COPY translations/ ./translations/
COPY database/schema.sql ./database/
COPY database/postgres-init.sql ./database/

# Create Streamlit config directory and file for proper server setup
RUN mkdir -p /root/.streamlit
RUN echo "\
[server]\n\
headless = true\n\
address = 0.0.0.0\n\
port = 5000\n\
" > /root/.streamlit/config.toml

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Expose the port the app runs on
EXPOSE $PORT

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Command to run the application with dynamic port
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true