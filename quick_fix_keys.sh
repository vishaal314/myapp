#!/bin/bash
# Quick Fix for Missing API Keys

echo "🔧 Quick fix for missing API keys..."

# Get your actual keys from environment or input
echo "Please enter your Stripe Secret Key (starts with sk_live_):"
read -s STRIPE_KEY

# Stop service
systemctl stop dataguardian

# Fix the environment file
cat > /opt/dataguardian/.env << EOF
ENVIRONMENT=production
DATABASE_URL=postgresql://dataguardian:temppass123@localhost:5432/dataguardian_prod
POSTGRES_PASSWORD=temppass123
REDIS_URL=redis://localhost:6379/0
DOMAIN_NAME=dataguardianpro.nl
OPENAI_API_KEY=sk-proj-aWKhPKWZGRfJuwpJN2YlQO9Y8v7qFsXMYUIa73f7FKe7gPGnWzGEXHgxJPfrAAv5GwHrEkFNkTT3BlbkFJ1UrO-HdtDpUagHqGjUxgJYoEWG-JJnPQBq6UDstFnWoVK6bNfNp_QZRnNElIeUGYhXKUdcQB2UAyQ
STRIPE_SECRET_KEY=${STRIPE_KEY}
DATAGUARDIAN_MASTER_KEY=dg_$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -base64 32)
EOF

# Set permissions
chmod 600 /opt/dataguardian/.env
chown dataguardian:dataguardian /opt/dataguardian/.env

# Start service
systemctl start dataguardian

echo "✅ API keys fixed! Service restarted."
echo "🌐 Test your app at: http://dataguardianpro.nl:5000"