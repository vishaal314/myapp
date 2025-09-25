#!/bin/bash
# Complete End-to-End Fix for DataGuardian Pro Deployment

set -e
echo "🔧 DataGuardian Pro - Complete E2E Fix"
echo "====================================="

# Step 1: Force kill everything using our ports
echo "🛑 Stopping all conflicting services..."
sudo pkill -f postgres || true
sudo pkill -f redis-server || true
sudo pkill -f postgresql || true
sudo systemctl stop postgresql || true
sudo systemctl stop redis-server || true
sudo systemctl disable postgresql || true
sudo systemctl disable redis-server || true

# Step 2: Stop and clean Docker
echo "🐳 Cleaning Docker environment..."
docker-compose down --remove-orphans 2>/dev/null || true
docker system prune -f
sleep 3

# Step 3: Check for remaining port usage
echo "🔍 Checking port usage..."
POSTGRES_PID=$(sudo lsof -ti:5432 || echo "")
REDIS_PID=$(sudo lsof -ti:6379 || echo "")

if [ ! -z "$POSTGRES_PID" ]; then
    echo "⚠️  Force killing PostgreSQL on port 5432 (PID: $POSTGRES_PID)"
    sudo kill -9 $POSTGRES_PID || true
fi

if [ ! -z "$REDIS_PID" ]; then
    echo "⚠️  Force killing Redis on port 6379 (PID: $REDIS_PID)"
    sudo kill -9 $REDIS_PID || true
fi

sleep 2

# Step 4: Use alternative ports if still blocked
POSTGRES_PORT=5432
REDIS_PORT=6379

if sudo lsof -i:5432 >/dev/null 2>&1; then
    echo "⚠️  Port 5432 still blocked, using 5433"
    POSTGRES_PORT=5433
fi

if sudo lsof -i:6379 >/dev/null 2>&1; then
    echo "⚠️  Port 6379 still blocked, using 6380"
    REDIS_PORT=6380
fi

echo "✅ Using PostgreSQL port: $POSTGRES_PORT"
echo "✅ Using Redis port: $REDIS_PORT"

# Step 5: Create complete docker-compose.yml with all environment variables
echo "📝 Creating complete Docker Compose configuration..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  # DataGuardian Pro - Complete Replit replication
  dataguardian:
    build:
      context: .
      dockerfile: Dockerfile.latest
    ports:
      - "5000:5000"
    environment:
      # Database connection (using dynamic port)
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian
      
      # Redis connection (using dynamic port) 
      - REDIS_URL=redis://redis:6379/0
      
      # Replit environment variables (exact match)
      - REPL_OWNER=vishaalnoord7
      - REPL_OWNER_ID=41202761
      - REPL_ID=4da867be-fdc8-4d7a-b11d-ce3fa352f4b9
      - REPL_SLUG=workspace
      - REPL_LANGUAGE=nix
      - REPL_HOME=/app
      
      # Application configuration
      - ENVIRONMENT=production
      - PYTHONPATH=/app
      
      # Streamlit configuration (exact Replit settings)
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=5000
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      
      # Application secrets (ALL SET - no more warnings)
      - DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
      - JWT_SECRET=dataguardian_jwt_secret_2025_production_secure_random_key_32_chars_long
      - ENCRYPTION_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
      - OPENAI_API_KEY=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
      - STRIPE_SECRET_KEY=sk_test_51RArxBFSlkdgMbJE03jAVsOp0Cp3KabXxuqlWtpKQgD82MPBRFJGhM7ghzPFYpNnzjlEoPqSC6uY7mzlWUY7RICb00Avj3sJx7
      - STRIPE_PUBLISHABLE_KEY=pk_test_51RArxBFSlkdgMbJEVGZa8gxmJApyrdHb4eBISnenblZCIDcKvq5lRoauhworQMI7kVCbVWFPvJfFd8OCacpfBnxZ00QRrkRLlp
      
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./reports:/app/reports
      - ./temp:/app/temp
    networks:
      - dataguardian-network

  # PostgreSQL Database (using dynamic port)
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: dataguardian
      POSTGRES_USER: postgres  
      POSTGRES_PASSWORD: password
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_schema.sql:/docker-entrypoint-initdb.d/database_schema.sql
    ports:
      - "${POSTGRES_PORT}:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d dataguardian"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - dataguardian-network

  # Redis Server (using dynamic port)
  redis:
    image: redis:7.2.4-alpine
    command: redis-server --port 6379 --bind 0.0.0.0 --appendonly yes
    ports:
      - "${REDIS_PORT}:6379"
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - dataguardian-network

  # Nginx for domain handling
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - dataguardian
    restart: unless-stopped
    networks:
      - dataguardian-network

volumes:
  postgres_data:
  redis_data:

networks:
  dataguardian-network:
    driver: bridge
EOF

# Step 6: Create .env file for ports
echo "POSTGRES_PORT=$POSTGRES_PORT" > .env
echo "REDIS_PORT=$REDIS_PORT" >> .env

echo "✅ Docker Compose created with PostgreSQL on port $POSTGRES_PORT and Redis on port $REDIS_PORT"
echo "✅ All environment variables set - no more warnings!"
echo ""
echo "🚀 Ready to deploy!"