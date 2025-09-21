#!/bin/bash
# Complete Production Fix and Restart Script

echo "🚀 DataGuardian Pro - Complete Production Fix"
echo "============================================="

# Stop service first
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Run comprehensive Python fix
echo "🔧 Running comprehensive syntax fix..."
python3 /opt/comprehensive_production_fix.py

if [ $? -eq 0 ]; then
    echo "✅ Syntax fix completed successfully!"
    
    # Start the service
    echo "🚀 Starting DataGuardian service..."
    systemctl start dataguardian
    
    # Wait for startup
    sleep 10
    
    # Check status
    if systemctl is-active --quiet dataguardian; then
        echo "✅ DataGuardian service is running!"
        
        # Test HTTP response
        echo "🌐 Testing HTTP response..."
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo "✅ SUCCESS! Application is responding!"
            echo ""
            echo "🎉 DataGuardian Pro is fully operational!"
            echo "🔒 Access: https://dataguardianpro.nl" 
            echo "👤 Login with: vishaal314"
            echo ""
            echo "✅ All issues resolved:"
            echo "   - Syntax errors fixed"
            echo "   - Service running properly"
            echo "   - HTTP responses working"
            echo "   - 502 Bad Gateway resolved"
        else
            echo "⚠️  Service running but HTTP response: $HTTP_CODE"
            echo "🔧 Check logs: journalctl -u dataguardian -n 10"
        fi
        
        # Show service status
        echo ""
        echo "📊 Service Status:"
        systemctl status dataguardian --no-pager -l
        
    else
        echo "❌ Service failed to start"
        echo "📋 Service logs:"
        journalctl -u dataguardian --no-pager -n 20
        exit 1
    fi
    
else
    echo "❌ Syntax fix failed"
    echo "🔧 Manual intervention required"
    exit 1
fi