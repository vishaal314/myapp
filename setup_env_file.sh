#!/bin/bash
# DataGuardian Pro Environment Setup Script

echo "🔧 Setting up DataGuardian Pro environment file..."

# Your actual API keys (replace with your real values)
OPENAI_KEY="${OPENAI_API_KEY:-your_openai_api_key_here}"
STRIPE_KEY="${STRIPE_SECRET_KEY:-sk_live_your_stripe_key_here}"

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
DATAGUARDIAN_MASTER_KEY=dg_$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -base64 32)
EOF

# Set proper permissions
chmod 600 /opt/dataguardian/.env
chown dataguardian:dataguardian /opt/dataguardian/.env

echo "✅ Environment file configured at /opt/dataguardian/.env"
echo "🔑 API keys have been automatically configured"
echo "🚀 You can now start the DataGuardian service: systemctl start dataguardian"