#!/bin/bash
# Fix API Keys for DataGuardian Production

echo "🔧 Fixing API Keys for DataGuardian..."

# Stop service first
systemctl stop dataguardian

# You need to replace these with your actual API keys from the Replit secrets
read -p "Enter your OpenAI API Key (sk-proj-...): " OPENAI_KEY
read -p "Enter your Stripe Secret Key (sk_live_...): " STRIPE_KEY

# Update the environment file with real keys
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

echo "✅ API keys updated successfully!"
echo "🚀 Starting DataGuardian service..."

systemctl start dataguardian
systemctl status dataguardian --no-pager