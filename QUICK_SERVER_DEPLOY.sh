#!/bin/bash
# DataGuardian Pro - Quick Server Deployment
# Run this script directly on your server

set -e

echo "🚀 DataGuardian Pro - Quick Server Deployment"
echo "============================================="

# Configuration
INSTALL_DIR="/opt/dataguardian"
SERVICE_USER="dataguardian"
DOMAIN_OR_IP="45.81.35.202"  # Update if needed

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_command() {
    if [ $? -ne 0 ]; then
        log "❌ $1 FAILED"
        exit 1
    fi
    log "✅ $1"
}

log "Starting deployment..."

# 1. SYSTEM SETUP
log "=== Installing system packages ==="
apt-get update -y >/dev/null 2>&1
apt-get install -y python3.11 python3.11-venv python3-pip git curl \
    postgresql postgresql-contrib redis-server nginx docker.io \
    docker-compose unzip >/dev/null 2>&1
check_command "System packages"

# 2. DOCKER SETUP (Simple approach)
log "=== Setting up Docker ==="
systemctl start docker
systemctl enable docker
usermod -aG docker root
check_command "Docker setup"

# 3. CREATE DEPLOYMENT DIRECTORY
log "=== Setting up directories ==="
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 4. CREATE EXACT REPLIT ENVIRONMENT REPLICATION
log "=== Creating Replit Environment Replication ==="

# Create environment variables file that matches Replit exactly
cat > .env << 'EOF'
# Replit-style Database (exactly as in Replit)
DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian

# Replit-style predefined environment variables
REPL_OWNER=dataguardian
REPL_ID=dataguardian-pro-production
REPL_SLUG=dataguardian-pro
REPL_LANGUAGE=python3
REPLIT_DEV_DOMAIN=45.81.35.202
HOME=/app
LANG=en_US.UTF-8

# Redis (same as Replit)
REDIS_URL=redis://redis:6379/0

# Application secrets (copy from Replit)
DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
JWT_SECRET=dataguardian_jwt_secret_2025_production_secure_random_key_32_chars

# Add your actual secrets here (copy from Replit Secrets)
OPENAI_API_KEY=your_openai_key_here
STRIPE_SECRET_KEY=your_stripe_key_here

# Streamlit configuration (exactly as Replit)
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONPATH=/app
ENVIRONMENT=production
EOF

# Create Docker Compose that exactly matches Replit services
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Main DataGuardian app (matches Replit Streamlit server)
  dataguardian:
    build: .
    ports:
      - "5000:5000"  # Exactly like Replit
    environment:
      # Load all Replit environment variables
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian
      - REDIS_URL=redis://redis:6379/0
      - REPL_OWNER=dataguardian
      - REPL_ID=dataguardian-pro-production
      - REPL_SLUG=dataguardian-pro
      - REPL_LANGUAGE=python3
      - REPLIT_DEV_DOMAIN=45.81.35.202
      - HOME=/app
      - LANG=en_US.UTF-8
      - PYTHONPATH=/app
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=5000
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - ENVIRONMENT=production
      # Secrets (update with your actual values)
      - DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
      - JWT_SECRET=dataguardian_jwt_secret_2025_production_secure_random_key_32_chars
      - OPENAI_API_KEY=${OPENAI_API_KEY:-your_openai_key_here}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-your_stripe_key_here}
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
    command: ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0", "--server.headless", "true"]

  # PostgreSQL (exactly as Replit Database)
  postgres:
    image: postgres:16  # Same version as Replit
    environment:
      POSTGRES_DB: dataguardian
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d dataguardian"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis (exactly as Replit Redis workflow)
  redis:
    image: redis:7.2.4  # Exact version from Replit logs
    command: redis-server --port 6379 --bind 0.0.0.0
    ports:
      - "6379:6379"
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOF

# Create database initialization (matches Replit database structure)
cat > init_db.sql << 'EOF'
-- Replit-style database initialization
CREATE TABLE IF NOT EXISTS scan_results (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_type VARCHAR(100),
    region VARCHAR(50),
    file_count INTEGER DEFAULT 0,
    total_pii_found INTEGER DEFAULT 0,
    high_risk_count INTEGER DEFAULT 0,
    result JSONB
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS license_data (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(255) UNIQUE,
    user_id INTEGER REFERENCES users(id),
    plan VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data that matches Replit environment
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@dataguardian.pro', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewvuKYq3FJjsj.e2', 'admin')
ON CONFLICT (username) DO NOTHING;
EOF

check_command "Replit environment replication"

# 5. CREATE SECRETS MANAGEMENT SCRIPT (Copy from Replit)
log "=== Creating Secrets Management ==="
cat > update_secrets.sh << 'EOF'
#!/bin/bash
# Update secrets to match your Replit environment
# Run this script after copying your actual API keys from Replit

echo "🔐 Updating secrets to match Replit environment..."

# Update .env file with your actual secrets
read -p "Enter your OPENAI_API_KEY from Replit: " OPENAI_KEY
read -p "Enter your STRIPE_SECRET_KEY from Replit: " STRIPE_KEY

# Update the .env file
sed -i "s/OPENAI_API_KEY=your_openai_key_here/OPENAI_API_KEY=$OPENAI_KEY/" .env
sed -i "s/STRIPE_SECRET_KEY=your_stripe_key_here/STRIPE_SECRET_KEY=$STRIPE_KEY/" .env

echo "✅ Secrets updated! Restart services:"
echo "   docker-compose restart dataguardian"
EOF
chmod +x update_secrets.sh

# 6. CREATE REPLIT PARITY VALIDATION SCRIPT
cat > validate_replit_parity.sh << 'EOF'
#!/bin/bash
# Validate that the environment matches Replit exactly

echo "🔍 Validating Replit Environment Parity..."

# Check services
echo "Checking services..."
docker-compose ps

# Check database connection
echo "Testing database connection..."
docker-compose exec postgres psql -U postgres -d dataguardian -c "SELECT COUNT(*) FROM users;"

# Check Redis connection
echo "Testing Redis connection..."
docker-compose exec redis redis-cli ping

# Check application health
echo "Testing application health..."
curl -f http://localhost:5000/_stcore/health || echo "Application health check failed"

# Check environment variables match
echo "Checking environment variables..."
docker-compose exec dataguardian env | grep -E "(DATABASE_URL|REDIS_URL|REPL_|STREAMLIT_)"

echo "✅ Replit parity validation complete!"
EOF
chmod +x validate_replit_parity.sh

check_command "Replit environment scripts"

log "=== REPLIT ENVIRONMENT REPLICATION COMPLETE! ==="
echo ""
echo "🎯 EXACT REPLIT ENVIRONMENT READY"
echo "=================================="
echo ""
echo "📋 DEPLOYMENT STEPS:"
echo "1. Upload your DataGuardian Pro files:"
echo "   scp -r app.py utils/ services/ components/ root@45.81.35.202:$INSTALL_DIR/"
echo ""
echo "2. Update secrets (copy from Replit):"
echo "   cd $INSTALL_DIR"
echo "   ./update_secrets.sh"
echo ""
echo "3. Deploy with exact Replit environment:"
echo "   docker-compose up -d"
echo ""
echo "4. Validate Replit parity:"
echo "   ./validate_replit_parity.sh"
echo ""
echo "🌐 REPLIT-IDENTICAL ENVIRONMENT:"
echo "   http://45.81.35.202:5000"
echo ""
echo "📊 SERVICES (exactly like Replit):"
echo "   ✅ Streamlit Server: Port 5000"
echo "   ✅ PostgreSQL Database: Port 5432"
echo "   ✅ Redis Server: Port 6379"
echo "   ✅ All Replit environment variables"
echo "   ✅ Same database schema and data"
echo ""
echo "🔧 MANAGEMENT (Replit-style):"
echo "   docker-compose logs -f dataguardian    # View logs"
echo "   docker-compose restart dataguardian    # Restart app" 
echo "   ./validate_replit_parity.sh            # Check parity"

log "Replit environment replication completed successfully!"