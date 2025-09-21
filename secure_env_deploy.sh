#!/bin/bash
# Secure Environment Deployment with Real API Keys

echo "🔐 Setting up DataGuardian Pro with secure API keys..."

# Stop service
systemctl stop dataguardian 2>/dev/null

# Create environment file with real keys
# Note: Replace these with your actual keys when running on production server
cat > /opt/dataguardian/.env << 'EOF'
ENVIRONMENT=production
DATABASE_URL=postgresql://dataguardian:temppass123@localhost:5432/dataguardian_prod
POSTGRES_PASSWORD=temppass123
REDIS_URL=redis://localhost:6379/0
DOMAIN_NAME=dataguardianpro.nl
OPENAI_API_KEY=sk-proj-aWKhPKWZGRfJuwpJN2YlQO9Y8v7qFsXMYUIa73f7FKe7gPGnWzGEXHgxJPfrAAv5GwHrEkFNkTT3BlbkFJ1UrO-HdtDpUagHqGjUxgJYoEWG-JJnPQBq6UDstFnWoVK6bNfNp_QZRnNElIeUGYhXKUdcQB2UAyQ
STRIPE_SECRET_KEY=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
DATAGUARDIAN_MASTER_KEY=dg_$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -base64 32)
EOF

# Set proper permissions
chmod 600 /opt/dataguardian/.env
chown dataguardian:dataguardian /opt/dataguardian/.env

echo "✅ Environment configured with real API keys"

# Start service
systemctl start dataguardian

echo "🚀 DataGuardian service restarted"
echo "🌐 Testing access..."

sleep 5

# Test if service is running
if systemctl is-active --quiet dataguardian; then
    echo "✅ Service is running successfully!"
    echo "🌐 Access your app at: http://dataguardianpro.nl:5000"
    
    # Test HTTP response
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ HTTP Test: Application responding correctly (200 OK)"
    else
        echo "⚠️  HTTP Test: Got response code $HTTP_CODE"
    fi
else
    echo "❌ Service failed to start. Checking logs..."
    systemctl status dataguardian --no-pager -l
fi