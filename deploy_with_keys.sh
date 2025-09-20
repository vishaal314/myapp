#!/bin/bash
# DataGuardian Pro Deployment Script with Real API Keys

echo "🚀 Deploying DataGuardian Pro with real API keys..."

# Export the actual API keys from current environment
export OPENAI_API_KEY="$OPENAI_API_KEY"
export STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY"  
export DATAGUARDIAN_MASTER_KEY="$DATAGUARDIAN_MASTER_KEY"

echo "🔑 API Keys loaded (lengths: OpenAI=${#OPENAI_API_KEY}, Stripe=${#STRIPE_SECRET_KEY})"

# Run the setup script with keys
./setup_env_file.sh

echo "✅ Deployment completed with real API keys!"