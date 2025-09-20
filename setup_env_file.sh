#!/bin/bash
# DataGuardian Pro Environment Setup Script

echo "🔧 Setting up DataGuardian Pro environment file..."

# Stop the service first
systemctl stop dataguardian 2>/dev/null || true

# Copy the environment file to the correct location
cp dataguardian_env_config.txt /opt/dataguardian/.env

# Set proper permissions
chmod 600 /opt/dataguardian/.env
chown dataguardian:dataguardian /opt/dataguardian/.env

echo "✅ Environment file configured at /opt/dataguardian/.env"
echo "📝 Remember to update your API keys in /opt/dataguardian/.env"
echo "🚀 You can now start the DataGuardian service: systemctl start dataguardian"