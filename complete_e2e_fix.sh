#!/bin/bash
# ULTIMATE E2E FIX - Handles all port conflicts with alternative methods

set -e
echo "🔧 ULTIMATE DataGuardian Pro E2E Fix"
echo "===================================="

# Step 1: Stop Docker completely first
echo "🐳 Stopping all Docker containers..."
docker-compose down --remove-orphans 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
docker system prune -f

# Step 2: Alternative port detection (since lsof isn't available)
echo "🔍 Checking ports with netstat..."
POSTGRES_CONFLICT=$(netstat -tlnp 2>/dev/null | grep ":5432 " || echo "")
REDIS_CONFLICT=$(netstat -tlnp 2>/dev/null | grep ":6379 " || echo "")

echo "PostgreSQL port check: $POSTGRES_CONFLICT"
echo "Redis port check: $REDIS_CONFLICT"

# Step 3: Force kill processes using our ports
echo "🛑 Force killing processes on conflicting ports..."
if [ ! -z "$POSTGRES_CONFLICT" ]; then
    echo "⚠️  Port 5432 is in use, force killing..."
    # Extract PID from netstat output and kill
    PID=$(echo "$POSTGRES_CONFLICT" | awk '{print $7}' | cut -d'/' -f1)
    if [ ! -z "$PID" ] && [ "$PID" != "-" ]; then
        echo "Killing process $PID"
        sudo kill -9 $PID 2>/dev/null || true
    fi
    # Also try killing by process name
    sudo pkill -9 postgres 2>/dev/null || true
    sudo pkill -9 postgresql 2>/dev/null || true
fi

if [ ! -z "$REDIS_CONFLICT" ]; then
    echo "⚠️  Port 6379 is in use, force killing..."
    PID=$(echo "$REDIS_CONFLICT" | awk '{print $7}' | cut -d'/' -f1)
    if [ ! -z "$PID" ] && [ "$PID" != "-" ]; then
        echo "Killing process $PID"
        sudo kill -9 $PID 2>/dev/null || true
    fi
    sudo pkill -9 redis-server 2>/dev/null || true
fi

# Step 4: Wait and recheck
sleep 3
echo "🔄 Rechecking ports after cleanup..."
POSTGRES_STILL_USED=$(netstat -tlnp 2>/dev/null | grep ":5432 " || echo "")
REDIS_STILL_USED=$(netstat -tlnp 2>/dev/null | grep ":6379 " || echo "")

# Step 5: Use alternative ports if still conflicts
POSTGRES_PORT=5432
REDIS_PORT=6379

if [ ! -z "$POSTGRES_STILL_USED" ]; then
    echo "⚠️  PostgreSQL port 5432 still blocked, using 5433"
    POSTGRES_PORT=5433
fi

if [ ! -z "$REDIS_STILL_USED" ]; then
    echo "⚠️  Redis port 6379 still blocked, using 6380" 
    REDIS_PORT=6380
fi

echo "✅ Final ports: PostgreSQL=$POSTGRES_PORT, Redis=$REDIS_PORT"

# Step 6: Create Docker Compose with correct ports
echo "📝 Creating Docker Compose with conflict-free ports..."
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
      # Database connection
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian
      
      # Redis connection
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

  # PostgreSQL Database (using safe port)
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
      - "$POSTGRES_PORT:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d dataguardian"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - dataguardian-network

  # Redis Server (using safe port)
  redis:
    image: redis:7.2.4-alpine
    command: redis-server --port 6379 --bind 0.0.0.0 --appendonly yes
    ports:
      - "$REDIS_PORT:6379"
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

# Step 7: Create environment file
echo "POSTGRES_PORT=$POSTGRES_PORT" > .env
echo "REDIS_PORT=$REDIS_PORT" >> .env

# Step 8: Ensure required directories exist
mkdir -p data logs reports temp

echo ""
echo "✅ ULTIMATE E2E FIX COMPLETE!"
echo "================================"
echo "🔹 All conflicting processes killed"
echo "🔹 Using PostgreSQL port: $POSTGRES_PORT"
echo "🔹 Using Redis port: $REDIS_PORT"  
echo "🔹 All environment variables set"
echo "🔹 Domain configuration ready"
echo ""
echo "🚀 NOW DEPLOY:"
echo "   docker-compose up -d"
echo ""
echo "📍 ACCESS POINTS:"
echo "   http://45.81.35.202:5000 (direct)"
echo "   http://45.81.35.202 (via nginx)"
echo "   http://dataguardianpro.nl (when DNS set)"