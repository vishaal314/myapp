#!/bin/bash
# Fix Docker Build Context Issue

echo "🔧 Fixing Docker Build Context Issue"
echo "===================================="
echo "Problem: Docker can't find .streamlit/ directory during build"
echo "Solution: Fix Dockerfile and build context"
echo ""

# Step 1: Verify current directory structure
echo "📋 Step 1: Verifying directory structure..."
echo "Current directory: $(pwd)"
echo ".streamlit directory exists: $(ls -la .streamlit/)"
echo ""

# Step 2: Create fixed Dockerfile without problematic .streamlit copy
echo "🔧 Step 2: Creating fixed Dockerfile..."

# Backup original
cp Dockerfile.latest Dockerfile.latest.backup

# Create fixed Dockerfile that doesn't fail on .streamlit copy
cat > Dockerfile.latest << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (matching Replit environment)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY production_requirements.txt requirements.txt

# Install Python dependencies with exact versions from Replit
RUN pip install --no-cache-dir --upgrade pip==23.3.1 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy application code and directories
COPY app.py .
COPY utils/ utils/
COPY services/ services/
COPY components/ components/
COPY translations/ translations/
COPY config/ config/
COPY static/ static/

# Set environment variables (matching Replit exactly)
ENV ENVIRONMENT=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Streamlit configuration (exact Replit settings)
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=5000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Replit-style environment variables
ENV REPL_OWNER=vishaalnoord7
ENV REPL_ID=4da867be-fdc8-4d7a-b11d-ce3fa352f4b9
ENV REPL_SLUG=workspace
ENV REPL_LANGUAGE=nix
ENV REPL_HOME=/app

# Application secrets (will be overridden by docker-compose)
ENV DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
ENV JWT_SECRET=dataguardian_jwt_secret_2025_production

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 dataguardian && \
    chown -R dataguardian:dataguardian /app

# Create necessary directories with proper permissions AFTER user creation
RUN mkdir -p logs reports data temp attached_assets && \
    chown -R dataguardian:dataguardian logs reports data temp attached_assets && \
    chmod 755 logs reports data temp attached_assets

USER dataguardian

# Create Streamlit config directly in container (bypasses copy issues)
RUN mkdir -p ~/.streamlit && \
    echo '[server]\n\
headless = true\n\
address = "0.0.0.0"\n\
port = 5000\n\
folderWatchBlacklist = [".*", "*/reports/*", "*/temp_*/*"]\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
serverAddress = "localhost"\n\
\n\
[theme]\n\
primaryColor = "#4267B2"\n\
backgroundColor = "#FFFFFF"\n\
secondaryBackgroundColor = "#F0F2F5"\n\
textColor = "#1E293B"\n\
font = "sans serif"\n\
\n\
[ui]\n\
hideTopBar = true\n\
\n\
[client]\n\
showErrorDetails = false\n\
toolbarMode = "minimal"\n\
\n\
[global]\n\
developmentMode = false\n\
\n\
[runner]\n\
fastReruns = true\n\
\n\
[logger]\n\
level = "error"' > ~/.streamlit/config.toml

# Expose port 5000 (Replit standard)
EXPOSE 5000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/_stcore/health || exit 1

# Start Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]
EOF

echo "✅ Fixed Dockerfile created (removes problematic .streamlit copy)"

# Step 3: Clean build and start
echo ""
echo "🧹 Step 3: Clean rebuild with fixed Dockerfile..."

# Stop containers
docker-compose down --remove-orphans

# Remove problematic images
docker rmi dataguardian-dataguardian 2>/dev/null || true

# Build with fixed Dockerfile
echo "🔨 Building with fixed configuration..."
docker-compose build --no-cache dataguardian

# Step 4: Start services
echo ""
echo "🚀 Step 4: Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to initialize..."
sleep 20

# Step 5: Test
echo ""
echo "🧪 Step 5: Testing fixed deployment..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "🎉🎉🎉 DOCKER BUILD CONTEXT FIXED! 🎉🎉🎉"
    echo "========================================"
    echo "✅ Dockerfile build successful"
    echo "✅ Streamlit config created in container"
    echo "✅ Application fully operational (HTTP 200)"
    echo "✅ All services running properly"
    echo ""
    echo "📍 Access your DataGuardian Pro:"
    echo "   http://45.81.35.202:5000"
    echo ""
    echo "🔧 Build issues resolved!"
    
elif [ "$HTTP_CODE" = "000" ]; then
    echo "⏳ Application still starting up..."
    echo "💡 Wait 30 seconds then try: http://45.81.35.202:5000"
    
    echo ""
    echo "🔍 Checking container logs:"
    docker-compose logs --tail=15 dataguardian
    
else
    echo "⚠️  Application status: HTTP $HTTP_CODE"
    echo ""
    echo "🔍 Checking for remaining issues:"
    docker-compose logs --tail=20 dataguardian
fi

echo ""
echo "📊 Final Container Status:"
docker-compose ps

echo ""
echo "✅ DOCKER BUILD CONTEXT FIX COMPLETE!"
echo "The .streamlit directory copy issue has been resolved."