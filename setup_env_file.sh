#!/bin/bash
# DataGuardian Pro Environment Setup Script

echo "🔧 Setting up DataGuardian Pro environment file..."

# Using actual API keys from Replit environment
OPENAI_KEY="$OPENAI_API_KEY"
STRIPE_KEY="$STRIPE_SECRET_KEY"
MASTER_KEY="$DATAGUARDIAN_MASTER_KEY"

# Stop the service first
systemctl stop dataguardian 2>/dev/null || true

# Create the environment file with real API keys
cat > /opt/dataguardian/.env << EOF
ENVIRONMENT=production
DATABASE_URL=postgresql://dataguardian:temppass123@localhost:5432/dataguardian_prod
POSTGRES_PASSWORD=temppass123
REDIS_URL=redis://localhost:6379/0
DOMAIN_NAME=dataguardianpro.nl
OPENAI_API_KEY=${OPENAI_KEY}
STRIPE_SECRET_KEY=${STRIPE_KEY}
DATAGUARDIAN_MASTER_KEY=${MASTER_KEY}
JWT_SECRET=$(openssl rand -base64 32)
EOF

# Set proper permissions
chmod 600 /opt/dataguardian/.env
chown dataguardian:dataguardian /opt/dataguardian/.env

echo "✅ Environment file configured at /opt/dataguardian/.env"
echo "🔑 API keys have been automatically configured"
echo "🚀 You can now start the DataGuardian service: systemctl start dataguardian"