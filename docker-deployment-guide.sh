#!/bin/bash
# DataGuardian Pro - Complete Docker Deployment Script
# Production-ready deployment with PostgreSQL, Redis, and Nginx

set -e  # Exit on any error

echo "🚀 DataGuardian Pro - Docker Deployment"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_step "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed."
}

# Create necessary directories
create_directories() {
    print_step "Creating necessary directories..."
    mkdir -p data logs reports config ssl nginx-logs
    chmod 755 data logs reports config
    print_status "Directories created successfully."
}

# Generate environment file
generate_env_file() {
    print_step "Generating environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# DataGuardian Pro Production Environment

# Application Settings
ENVIRONMENT=production
APP_NAME=DataGuardian Pro
APP_VERSION=1.0.0

# Database Configuration
DATABASE_URL=postgresql://dataguardian:secure_password_2024@postgres:5432/dataguardian_prod
POSTGRES_DB=dataguardian_prod
POSTGRES_USER=dataguardian
POSTGRES_PASSWORD=secure_password_2024

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=redis_password_2024

# Security Settings
SAP_SSL_VERIFY=true
SALESFORCE_TIMEOUT=30
SAP_REQUEST_TIMEOUT=30
OIDC_TIMEOUT=30

# Stripe Configuration (set your own keys)
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here

# JWT and Encryption
JWT_SECRET=your_jwt_secret_key_here_make_it_long_and_random
ENCRYPTION_KEY=your_encryption_key_here_32_characters

# GDPR Compliance
DATA_RESIDENCY=EU
PRIVACY_POLICY_URL=https://dataguardian.nl/privacy
TERMS_URL=https://dataguardian.nl/terms

# Logging
LOG_LEVEL=INFO
ENABLE_DEBUG=false

# Netherlands Specific
DEFAULT_COUNTRY=NL
DEFAULT_LANGUAGE=en
UAVG_COMPLIANCE=true
EOF
        print_status "Environment file (.env) created. Please update with your actual values."
    else
        print_warning ".env file already exists. Skipping generation."
    fi
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    print_step "Generating SSL certificates..."
    
    if [ ! -d "ssl" ]; then
        mkdir -p ssl
    fi
    
    if [ ! -f "ssl/cert.pem" ]; then
        print_status "Generating self-signed SSL certificate for development..."
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=NL/ST=North Holland/L=Amsterdam/O=DataGuardian Pro/CN=localhost"
        chmod 600 ssl/key.pem
        chmod 644 ssl/cert.pem
        print_status "SSL certificates generated."
        print_warning "These are self-signed certificates for development. Use proper certificates in production."
    else
        print_status "SSL certificates already exist."
    fi
}

# Build and start services
deploy_services() {
    print_step "Building and deploying services..."
    
    # Build the application image
    print_status "Building DataGuardian Pro image..."
    docker-compose build --no-cache dataguardian
    
    # Start all services
    print_status "Starting all services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    print_status "Checking service health..."
    docker-compose ps
}

# Initialize database
init_database() {
    print_step "Initializing database..."
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    until docker-compose exec -T postgres pg_isready -U dataguardian -d dataguardian_prod; do
        echo "Waiting for PostgreSQL..."
        sleep 2
    done
    
    print_status "Database is ready and initialized."
}

# Test deployment
test_deployment() {
    print_step "Testing deployment..."
    
    # Test application health
    if curl -f http://localhost:5000/_stcore/health > /dev/null 2>&1; then
        print_status "✅ Application health check passed"
    else
        print_warning "⚠️ Application health check failed"
    fi
    
    # Test database connection
    if docker-compose exec -T postgres psql -U dataguardian -d dataguardian_prod -c "SELECT 1;" > /dev/null 2>&1; then
        print_status "✅ Database connection successful"
    else
        print_warning "⚠️ Database connection failed"
    fi
    
    # Test Redis connection
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_status "✅ Redis connection successful"
    else
        print_warning "⚠️ Redis connection failed"
    fi
    
    # Test Nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_status "✅ Nginx proxy working"
    else
        print_warning "⚠️ Nginx proxy test failed"
    fi
}

# Setup monitoring
setup_monitoring() {
    print_step "Setting up monitoring and logging..."
    
    # Create log rotation configuration
    cat > logrotate.conf << EOF
/path/to/dataguardian/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart dataguardian
    endscript
}
EOF
    
    print_status "Log rotation configured."
}

# Create backup script
create_backup_script() {
    print_step "Creating backup script..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash
# DataGuardian Pro Backup Script

BACKUP_DIR="/opt/dataguardian/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U dataguardian dataguardian_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application data
echo "Backing up application data..."
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz data/ logs/ reports/ config/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
EOF
    
    chmod +x backup.sh
    print_status "Backup script created: backup.sh"
}

# Display deployment summary
show_summary() {
    echo ""
    echo "🎉 DataGuardian Pro Deployment Complete!"
    echo "========================================"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access Points:"
    echo "  • Application: http://localhost:5000"
    echo "  • Nginx Proxy: http://localhost"
    echo "  • Database: localhost:5432"
    echo "  • Redis: localhost:6379"
    echo ""
    echo "📁 Important Files:"
    echo "  • Environment: .env"
    echo "  • SSL Certs: ssl/"
    echo "  • Logs: logs/"
    echo "  • Data: data/"
    echo "  • Reports: reports/"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose logs -f dataguardian"
    echo "  • Restart: docker-compose restart"
    echo "  • Stop: docker-compose down"
    echo "  • Backup: ./backup.sh"
    echo ""
    echo "⚠️ Next Steps:"
    echo "  1. Update .env file with your actual API keys"
    echo "  2. Replace self-signed SSL certificates with real ones"
    echo "  3. Configure domain name and DNS"
    echo "  4. Set up automated backups"
    echo "  5. Configure monitoring and alerting"
    echo ""
    print_status "Deployment completed successfully! 🚀"
}

# Main deployment process
main() {
    print_status "Starting DataGuardian Pro deployment..."
    
    check_docker
    create_directories
    generate_env_file
    generate_ssl_certs
    deploy_services
    init_database
    test_deployment
    setup_monitoring
    create_backup_script
    show_summary
}

# Run main function
main "$@"