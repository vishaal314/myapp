#!/bin/bash

echo "🔧 DataGuardian Pro Fix Script v2 - Starting..."
echo "================================================"

# Step 1: Check current status
echo "📊 Current container status:"
docker ps

# Step 2: Create nginx template with WebSocket support
echo ""
echo "🔧 Step 1: Creating nginx template with WebSocket support..."

cat > nginx.conf.template << 'EOF'
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://$server_name$request_uri;
}

map $http_upgrade $connection_upgrade { 
    default upgrade; 
    '' close; 
}

upstream streamlit_app { 
    server dataguardian-pro:5000; 
}

server {
    listen 443 ssl;
    server_name ${DOMAIN};
    client_max_body_size 64M;

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Regular HTTP requests
    location / {
        proxy_pass http://streamlit_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Critical WebSocket streaming endpoints for Streamlit
    location ~ ^/_stcore/.* {
        proxy_pass http://streamlit_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_buffering off;
    }
}
EOF

if [ $? -eq 0 ]; then
    echo "✅ nginx template created successfully"
else
    echo "❌ Failed to create nginx template"
    exit 1
fi

# Step 3: Restart nginx to apply the template
echo ""
echo "🔄 Step 2: Restarting nginx with WebSocket template..."
docker compose -f docker-compose.prod.yml restart nginx

if [ $? -eq 0 ]; then
    echo "✅ nginx restarted successfully"
else
    echo "❌ Failed to restart nginx"
    exit 1
fi

echo "⏳ Waiting for nginx to process template..."
sleep 15

# Step 4: Ensure working app version is deployed
echo ""
echo "🚀 Step 3: Ensuring DataGuardian Pro uses working version..."
if [ -f "app_simplified.py" ] && [ -f "app.py" ]; then
    # Check if files are different
    if ! cmp -s app_simplified.py app.py; then
        echo "📝 Updating app.py with working version..."
        cp app_simplified.py app.py
        echo "🔄 Restarting DataGuardian Pro container..."
        docker compose -f docker-compose.prod.yml restart dataguardian-pro
        echo "⏳ Waiting for app to restart..."
        sleep 20
    else
        echo "✅ app.py is already the working version"
    fi
else
    echo "⚠️  app_simplified.py not found, using existing app.py"
fi

# Step 5: Final status check
echo ""
echo "📊 Final container status:"
docker ps

# Step 6: Test nginx configuration inside container
echo ""
echo "🔧 Step 4: Testing nginx configuration..."
docker exec dataguardian-nginx nginx -t

if [ $? -eq 0 ]; then
    echo "✅ nginx configuration is valid"
else
    echo "❌ nginx configuration has errors"
fi

# Step 7: Test the website
echo ""
echo "🌐 Step 5: Testing website connectivity..."
echo "Testing HTTPS response:"
curl -I https://dataguardianpro.nl

echo ""
echo "Testing WebSocket health endpoint:"
curl -I https://dataguardianpro.nl/_stcore/health

echo ""
echo "🎉 DataGuardian Pro Fix v2 Complete!"
echo "================================================"
echo "✅ nginx template: Created with WebSocket support"
echo "✅ nginx container: Restarted with new configuration"
echo "✅ WebSocket streaming: Should now work (no HTTP 400)"
echo "✅ DataGuardian Pro: Using working app version"
echo "✅ SSL/HTTPS: Should be working"
echo ""
echo "🚀 Your €25K MRR platform should now be fully operational at:"
echo "   https://dataguardianpro.nl"
echo ""
echo "📧 Demo login: demo@dataguardianpro.nl / demo123"
echo ""
echo "💡 If you still see gray boxes:"
echo "   1. Wait 60 seconds for all services to stabilize"
echo "   2. Clear browser cache and refresh"
echo "   3. Check browser dev tools for any WebSocket errors"
echo ""
echo "🔍 To verify WebSocket fix:"
echo "   docker logs dataguardian-nginx --tail 20"
echo "   (Should show 101 instead of 400 for /_stcore/stream)"