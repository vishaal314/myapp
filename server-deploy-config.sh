#!/bin/bash
# DataGuardian Pro Server Deployment Configuration

# Server Configuration
export SERVER_HOST="your-server.com"        # Your production server
export SERVER_USER="ubuntu"                 # Server user
export SERVER_PATH="/opt/dataguardian-pro"  # Deployment path
export DOMAIN_NAME="dataguardianpro.nl"     # Your domain

# Application Configuration
export APP_PORT="5000"
export SSL_CERT_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
export SSL_KEY_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"

# Database Configuration (if using external DB)
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="dataguardian_pro"
export DB_USER="dataguardian"

echo "📋 Server deployment configuration ready"
echo "🔧 Modify these values for your production server"
