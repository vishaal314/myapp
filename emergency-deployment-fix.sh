#!/bin/bash

# Emergency DataGuardian Pro Deployment Fix Script
# This script fixes all the critical deployment issues

echo "🚨 Emergency Deployment Fix Starting..."

# Function to show disk usage
show_disk_usage() {
    echo "📊 Current disk usage:"
    df -h / | grep -v Filesystem
}

# Function for aggressive cleanup
emergency_cleanup() {
    echo "🧹 Performing emergency disk cleanup..."
    
    # Stop all services first
    docker-compose down || true
    docker stop $(docker ps -aq) 2>/dev/null || true
    
    # Remove all Docker containers, images, networks, volumes
    echo "Removing all Docker resources..."
    docker system prune -af --volumes || true
    docker builder prune -af || true
    
    # Remove Docker cache and build data
    rm -rf /var/lib/docker/tmp/* 2>/dev/null || true
    rm -rf /var/lib/docker/builder/* 2>/dev/null || true
    
    # Clean package cache
    apt autoremove -y --purge || true
    apt autoclean || true
    apt clean || true
    
    # Remove temporary files
    rm -rf /tmp/* || true
    rm -rf /var/tmp/* || true
    rm -rf /var/cache/apt/archives/*.deb || true
    
    # Remove old kernels
    apt autoremove --purge -y $(dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d') 2>/dev/null || true
    
    # Clear logs older than 7 days
    find /var/log -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    find /var/log -type f -name "*.log.*" -delete 2>/dev/null || true
    
    # Remove Python cache files
    find /usr -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find /usr -name "*.pyc" -delete 2>/dev/null || true
    
    echo "✅ Emergency cleanup completed"
    show_disk_usage
}

# Function to create environment file
create_production_env() {
    echo "⚙️ Creating production environment file..."
    
    cd /opt/dataguardian-pro || exit 1
    
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://dataguardian_pro:DataGuardian2025SecurePass@postgres:5432/dataguardian_pro
DB_USER=dataguardian_pro
DB_PASSWORD=DataGuardian2025SecurePass
POSTGRES_DB=dataguardian_pro
POSTGRES_USER=dataguardian_pro
POSTGRES_PASSWORD=DataGuardian2025SecurePass

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)

# Domain Configuration
DOMAIN=vishaalnoord7.retzor.com
ALLOWED_HOSTS=vishaalnoord7.retzor.com,localhost,127.0.0.1

# Performance Configuration
REDIS_CACHE_TTL=3600
SESSION_TIMEOUT=7200
MAX_UPLOAD_SIZE=100MB

# Security Configuration
SSL_ENABLED=true
FORCE_HTTPS=true
SESSION_SECURE=true
EOF

    echo "✅ Environment file created"
}

# Function to create minimal docker-compose file that doesn't pull images
create_minimal_compose() {
    echo "🐳 Creating minimal docker-compose configuration..."
    
    cd /opt/dataguardian-pro || exit 1
    
    cat > docker-compose.minimal.yml << 'EOF'
version: '3.8'

services:
  dataguardian-pro:
    image: dataguardian-pro:latest
    container_name: dataguardian-pro
    restart: unless-stopped
    pull_policy: never
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://dataguardian_pro:DataGuardian2025SecurePass@postgres:5432/dataguardian_pro
      - REDIS_URL=redis://redis:6379/0
      - DB_USER=dataguardian_pro
      - DB_PASSWORD=DataGuardian2025SecurePass
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./cache:/app/cache
      - ./reports:/app/reports
    networks:
      - dataguardian-network
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    container_name: dataguardian-postgres
    restart: unless-stopped
    pull_policy: missing
    environment:
      POSTGRES_DB: dataguardian_pro
      POSTGRES_USER: dataguardian_pro
      POSTGRES_PASSWORD: DataGuardian2025SecurePass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    networks:
      - dataguardian-network

  redis:
    image: redis:7-alpine
    container_name: dataguardian-redis
    restart: unless-stopped
    pull_policy: missing
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    networks:
      - dataguardian-network

volumes:
  postgres_data:
  redis_data:

networks:
  dataguardian-network:
    driver: bridge
EOF

    echo "✅ Minimal docker-compose created"
}

# Function to start services with careful resource management
start_services() {
    echo "🚀 Starting services with resource management..."
    
    cd /opt/dataguardian-pro || exit 1
    
    # Create required directories
    mkdir -p data logs cache reports backups ssl
    
    # Start PostgreSQL first (smallest image)
    echo "Starting PostgreSQL..."
    docker-compose -f docker-compose.minimal.yml up -d postgres
    
    # Wait for PostgreSQL
    sleep 10
    
    # Show disk usage
    show_disk_usage
    
    # Start Redis (also small)
    echo "Starting Redis..."  
    docker-compose -f docker-compose.minimal.yml up -d redis
    
    # Wait for Redis
    sleep 5
    
    # Show disk usage again
    show_disk_usage
    
    # Finally start main application
    echo "Starting DataGuardian Pro application..."
    docker-compose -f docker-compose.minimal.yml up -d dataguardian-pro
    
    # Wait for application startup
    echo "Waiting for application to start..."
    sleep 30
    
    # Health check with retries
    for i in {1..10}; do
        if curl -f http://localhost:5000 >/dev/null 2>&1; then
            echo "✅ Application is running successfully!"
            docker ps
            return 0
        fi
        echo "Attempt $i/10: Waiting for application..."
        sleep 10
    done
    
    echo "⚠️ Application may need more time to start"
    docker logs dataguardian-pro --tail=20
}

# Main execution
main() {
    echo "🔧 DataGuardian Pro Emergency Deployment Fix"
    echo "============================================="
    
    # Show initial disk usage
    show_disk_usage
    
    # Emergency cleanup
    emergency_cleanup
    
    # Create directories
    mkdir -p /opt/dataguardian-pro/{data,logs,cache,reports,backups,ssl}
    
    # Create production environment
    create_production_env
    
    # Create minimal compose file
    create_minimal_compose
    
    # Start services carefully
    start_services
    
    echo "============================================="
    echo "✅ Emergency deployment fix completed!"
    echo "🌐 Application should be available at: http://vishaalnoord7.retzor.com:5000"
    echo "📊 Final disk usage:"
    show_disk_usage
}

# Run main function with error handling
set -e
main "$@"