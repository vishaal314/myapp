#!/bin/bash
# Export Replit Environment Secrets for GitHub
# Copy these values to GitHub Secrets

echo "================================================"
echo "REPLIT ENVIRONMENT SECRETS"
echo "================================================"
echo ""
echo "Copy each value below to GitHub Secrets:"
echo "https://github.com/vishaal314/myapp/settings/secrets/actions"
echo ""
echo "================================================"
echo ""

echo "SECRET 1: JWT_SECRET"
echo "Value: ${JWT_SECRET}"
echo ""

echo "SECRET 2: DATAGUARDIAN_MASTER_KEY"
if [ -n "$DATAGUARDIAN_MASTER_KEY" ]; then
    echo "Value: ${DATAGUARDIAN_MASTER_KEY}"
elif [ -n "$MASTER_KEY_DASHBOARD" ]; then
    echo "Value: ${MASTER_KEY_DASHBOARD}"
else
    echo "Value: NOT FOUND - Check Replit Secrets"
fi
echo ""

echo "SECRET 3: OPENAI_API_KEY"
echo "Value: ${OPENAI_API_KEY}"
echo ""

echo "SECRET 4: STRIPE_SECRET_KEY"
echo "Value: ${STRIPE_SECRET_KEY}"
echo ""

echo "SECRET 5: DATABASE_URL"
echo "Value: ${DATABASE_URL}"
echo ""

echo "================================================"
echo "COPY THESE TO GITHUB SECRETS NOW!"
echo "================================================"
