#!/bin/bash
# DataGuardian Pro SSL/HTTPS Setup Script

echo "🔒 Setting up HTTPS for DataGuardian Pro..."

# Install certbot if not already installed
echo "📦 Installing certbot..."
apt update && apt install certbot python3-certbot-nginx -y

# Check nginx configuration
echo "🔧 Checking nginx configuration..."
if ! nginx -t; then
    echo "❌ Nginx configuration error. Please check nginx config."
    exit 1
fi

# Generate SSL certificate
echo "🔐 Generating SSL certificate for dataguardianpro.nl..."
certbot --nginx -d dataguardianpro.nl --non-interactive --agree-tos --email admin@dataguardianpro.nl

# Verify certificate was created
if [ $? -eq 0 ]; then
    echo "✅ SSL certificate generated successfully!"
    
    # Test HTTPS access
    echo "🌐 Testing HTTPS access..."
    sleep 3
    
    HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dataguardianpro.nl 2>/dev/null || echo "000")
    if [ "$HTTPS_CODE" = "200" ]; then
        echo "✅ HTTPS Test: SUCCESS! (200 OK)"
        echo ""
        echo "🎉 DataGuardian Pro is now live at:"
        echo "📱 HTTPS: https://dataguardianpro.nl"
        echo "🔓 HTTP:  http://dataguardianpro.nl:5000"
        echo ""
        echo "🔒 SSL Certificate will auto-renew every 90 days"
    else
        echo "⚠️  HTTPS Test: Response code $HTTPS_CODE"
        echo "🔧 Please check nginx configuration"
    fi
    
    # Show certificate details
    echo ""
    echo "📋 Certificate Details:"
    certbot certificates
    
else
    echo "❌ SSL certificate generation failed"
    echo "🔧 Please check:"
    echo "   - DNS: dataguardianpro.nl points to this server (45.81.35.202)"
    echo "   - Nginx: Properly configured"
    echo "   - Port 80/443: Open and accessible"
fi