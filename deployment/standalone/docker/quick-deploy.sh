#!/bin/bash

# DataGuardian Pro - One-Command Standalone Deployment
# This script deploys DataGuardian Pro as a standalone Docker container

set -e

echo "🚀 DataGuardian Pro - Standalone Docker Deployment"
echo "=================================================="
echo ""

# Check requirements
echo "🔍 Checking requirements..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker requirements satisfied"

# Create deployment directory
DEPLOY_DIR="dataguardian-pro-standalone"
echo "📁 Creating deployment directory: $DEPLOY_DIR"

if [ -d "$DEPLOY_DIR" ]; then
    echo "⚠️  Directory exists. Backing up..."
    mv "$DEPLOY_DIR" "${DEPLOY_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Download deployment files
echo "📥 Downloading deployment files..."

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  dataguardian:
    image: dataguardian/pro:latest
    container_name: dataguardian-pro
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
      - ./licenses:/app/licenses
    environment:
      - STANDALONE_MODE=true
      - DEFAULT_REGION=Netherlands
      - COMPLIANCE_MODE=UAVG
      - DATABASE_URL=sqlite:///app/data/dataguardian.db
    restart: unless-stopped

  # Optional PostgreSQL for enterprise
  postgres:
    image: postgres:16-alpine
    container_name: dataguardian-postgres
    environment:
      POSTGRES_DB: dataguardian
      POSTGRES_USER: dataguardian
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dataguardian2024}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    profiles:
      - enterprise

volumes:
  postgres_data:
EOF

# Create .env template
cat > .env.template << 'EOF'
# DataGuardian Pro Standalone Configuration

# Database (for enterprise PostgreSQL)
POSTGRES_PASSWORD=your_secure_password_here

# Optional API Keys
OPENAI_API_KEY=your_openai_key_here
STRIPE_SECRET_KEY=your_stripe_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Compliance Settings
DEFAULT_REGION=Netherlands
COMPLIANCE_MODE=UAVG
DATA_RESIDENCY=EU

# License (Enterprise customers)
LICENSE_KEY=your_license_key_here
EOF

# Create directories
echo "📂 Creating data directories..."
mkdir -p data reports licenses config

# Create demo license
echo "📝 Creating demo license (30 days)..."
cat > licenses/license.key << EOF
DEMO_LICENSE_30_DAYS_$(date +%Y%m%d)
DataGuardian Pro Demo
Valid until: $(date -d '+30 days' +%Y-%m-%d)
Features: All scanners enabled
Users: Up to 5 concurrent
Scans: Up to 100 per month
Support: Community only
EOF

# Create configuration guide
cat > README.md << 'EOF'
# DataGuardian Pro Standalone

## Quick Start

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - URL: http://localhost:8501
   - Demo license: 30 days included

3. **For enterprise with PostgreSQL:**
   ```bash
   docker-compose --profile enterprise up -d
   ```

## Configuration

- **Data**: Stored in `./data/`
- **Reports**: Generated in `./reports/`
- **License**: Place in `./licenses/license.key`
- **Environment**: Copy `.env.template` to `.env`

## Support

- Demo: Community support only
- Enterprise: Contact sales for full license and support

## Upgrade

Contact sales@dataguardian.pro for:
- Full license (unlimited users/scans)
- Enterprise PostgreSQL setup
- Professional support
- Custom integrations
EOF

# Start deployment
echo ""
echo "🚀 Starting DataGuardian Pro..."
echo ""

# Check if we should start with PostgreSQL
read -p "🗄️  Use PostgreSQL database? (y/N): " use_postgres

if [[ $use_postgres =~ ^[Yy]$ ]]; then
    echo "Starting with PostgreSQL..."
    docker-compose --profile enterprise up -d
else
    echo "Starting with SQLite (demo mode)..."
    docker-compose up -d
fi

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 30

# Check if running
if docker ps | grep -q dataguardian-pro; then
    echo ""
    echo "🎉 DataGuardian Pro is running!"
    echo ""
    echo "📍 Access your application:"
    echo "   🌐 Web Interface: http://localhost:8501"
    echo "   📊 Health Check: http://localhost:8501/_stcore/health"
    echo ""
    echo "📁 Data locations:"
    echo "   📄 Database: ./data/"
    echo "   📋 Reports: ./reports/"
    echo "   🔑 License: ./licenses/license.key"
    echo ""
    echo "🔧 Management commands:"
    echo "   docker-compose logs -f dataguardian    # View logs"
    echo "   docker-compose restart dataguardian    # Restart"
    echo "   docker-compose down                    # Stop"
    echo ""
    echo "💼 Enterprise features:"
    echo "   Contact: sales@dataguardian.pro"
    echo "   License: Unlimited users and scans"
    echo "   Support: Phone and email support"
    echo ""
    echo "✅ Deployment complete!"
else
    echo "❌ Startup failed. Checking logs..."
    docker-compose logs dataguardian
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check port 8501 is available: netstat -tulpn | grep 8501"
    echo "2. Check Docker logs: docker-compose logs"
    echo "3. Restart: docker-compose down && docker-compose up -d"
fi