#!/bin/bash
# Fix SSL Certificate Dependencies and Generate Certificate

echo "🔧 Fixing SSL certificate dependencies..."

# Remove existing certbot installation
echo "🗑️ Removing broken certbot installation..."
apt remove certbot python3-certbot-nginx -y

# Clean up Python packages
echo "🧹 Cleaning up Python dependencies..."
apt autoremove -y
apt autoclean

# Install required system dependencies
echo "📦 Installing system dependencies..."
apt update
apt install -y python3-pip python3-dev libffi-dev libssl-dev build-essential

# Install CFFI backend specifically
echo "🔧 Installing CFFI backend..."
pip3 install --upgrade cffi cryptography

# Reinstall certbot using pip (more reliable)
echo "📥 Reinstalling certbot via pip..."
pip3 install certbot certbot-nginx

# Verify certbot installation
echo "✅ Verifying certbot installation..."
if /usr/local/bin/certbot --version; then
    echo "✅ Certbot installed successfully!"
    
    # Generate SSL certificate
    echo "🔐 Generating SSL certificate for dataguardianpro.nl..."
    /usr/local/bin/certbot --nginx -d dataguardianpro.nl --non-interactive --agree-tos --email admin@dataguardianpro.nl --redirect
    
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
            echo "🔒 HTTPS: https://dataguardianpro.nl (PRIMARY)"
            echo "🔓 HTTP:  http://dataguardianpro.nl:5000 (BACKUP)"
            echo ""
            echo "🔄 SSL Certificate will auto-renew every 90 days"
        else
            echo "⚠️  HTTPS Test: Response code $HTTPS_CODE"
            echo "🔧 Manual check needed"
        fi
        
        # Setup auto-renewal
        echo "🔄 Setting up SSL auto-renewal..."
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/certbot renew --quiet") | crontab -
        
        # Show certificate status
        echo ""
        echo "📋 Certificate Status:"
        /usr/local/bin/certbot certificates
        
    else
        echo "❌ SSL certificate generation failed"
        echo "🔧 Check DNS configuration and try again"
    fi
    
else
    echo "❌ Certbot installation failed"
    echo "🔧 Manual intervention required"
fi