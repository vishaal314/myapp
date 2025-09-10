#!/bin/bash

# DataGuardian Pro Production Deployment Setup Script
# This script automates the initial setup for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}DataGuardian Pro Production Deployment Setup${NC}"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Create deployment directory
DEPLOY_DIR="/opt/dataguardian-pro"
echo -e "${YELLOW}Setting up deployment directory: $DEPLOY_DIR${NC}"

if [[ ! -d "$DEPLOY_DIR" ]]; then
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $USER:$USER "$DEPLOY_DIR"
    echo -e "${GREEN}✓ Created deployment directory${NC}"
else
    echo -e "${GREEN}✓ Deployment directory already exists${NC}"
fi

cd "$DEPLOY_DIR"

# Create required subdirectories
echo -e "${YELLOW}Creating required subdirectories...${NC}"
mkdir -p {data,logs,cache,reports,backups,ssl,certbot-var}
mkdir -p backups/{database,files}
mkdir -p ssl/{live,archive}
sudo mkdir -p /var/www/html
sudo chown -R $USER:$USER ssl /var/www/html

echo -e "${GREEN}✓ Created all required subdirectories${NC}"

# Copy and configure environment file
if [[ -f "production.env.template" ]]; then
    if [[ ! -f ".env" ]]; then
        echo -e "${YELLOW}Setting up environment configuration...${NC}"
        cp production.env.template .env
        
        # Generate secure passwords and keys
        DB_PASSWORD=$(openssl rand -base64 32)
        SECRET_KEY=$(openssl rand -hex 32)
        
        # Update .env with generated values
        sed -i "s/generate_secure_password_here/$DB_PASSWORD/g" .env
        sed -i "s/generate_32_char_secret_key_here/$SECRET_KEY/g" .env
        
        echo -e "${GREEN}✓ Created .env file with generated passwords${NC}"
        echo -e "${YELLOW}IMPORTANT: Edit .env file to set your domain and API keys:${NC}"
        echo "  - DOMAIN=your-actual-domain.com"
        echo "  - CERTBOT_EMAIL=your-email@domain.com"
        echo "  - OPENAI_API_KEY=your_actual_openai_key"
        echo "  - STRIPE_SECRET_KEY=your_actual_stripe_key"
        echo ""
    else
        echo -e "${GREEN}✓ .env file already exists${NC}"
    fi
else
    echo -e "${RED}production.env.template not found. Please ensure all application files are uploaded.${NC}"
    exit 1
fi

# Check if docker-compose.prod.yml exists
if [[ ! -f "docker-compose.prod.yml" ]]; then
    echo -e "${RED}docker-compose.prod.yml not found. Please upload all application files.${NC}"
    exit 1
fi

# Check if application files exist
if [[ ! -f "app.py" ]]; then
    echo -e "${RED}app.py not found. Please upload all application files.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Required files found${NC}"

# Configure firewall (if ufw is available)
if command_exists ufw; then
    echo -e "${YELLOW}Configuring firewall...${NC}"
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    echo -e "${GREEN}✓ Firewall configured${NC}"
fi

# Build and start services
echo -e "${YELLOW}Building Docker image...${NC}"
if docker build -t dataguardian-pro:latest .; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting services...${NC}"
if docker-compose -f docker-compose.prod.yml up -d; then
    echo -e "${GREEN}✓ Services started successfully${NC}"
else
    echo -e "${RED}Failed to start services${NC}"
    exit 1
fi

# Wait a moment for services to initialize
echo -e "${YELLOW}Waiting for services to initialize...${NC}"
sleep 10

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Create backup script
echo -e "${YELLOW}Setting up backup script...${NC}"
cat > backup.sh << 'EOF'
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/opt/dataguardian-pro/backups"

# Database backup
docker exec dataguardian-postgres pg_dump -U dataguardian_pro dataguardian_pro > "$backup_dir/database/backup_$timestamp.sql"

# Files backup
tar -czf "$backup_dir/files/files_backup_$timestamp.tar.gz" -C /opt/dataguardian-pro data reports

# Cleanup old backups (keep 7 days)
find "$backup_dir/database" -name "backup_*.sql" -mtime +7 -delete
find "$backup_dir/files" -name "files_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $timestamp"
EOF

chmod +x backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/dataguardian-pro/backup.sh") | crontab -
echo -e "${GREEN}✓ Backup script created and scheduled${NC}"

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your actual domain and API keys:"
echo "   nano .env"
echo ""
echo "2. After configuring .env, generate SSL certificates:"
echo "   docker-compose -f docker-compose.prod.yml run --rm certbot"
echo ""
echo "3. Restart nginx to load certificates:"
echo "   docker-compose -f docker-compose.prod.yml restart nginx"
echo ""
echo "4. Test your deployment:"
echo "   curl -f http://your-domain.com"
echo "   curl -f https://your-domain.com"
echo ""
echo -e "${YELLOW}Support:${NC} If you encounter issues, check logs with:"
echo "docker-compose -f docker-compose.prod.yml logs -f"