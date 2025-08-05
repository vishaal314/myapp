#!/bin/bash

# DataGuardian Pro - Monitoring and Maintenance Script
# Run this script daily to monitor your Hetzner deployment

echo "🔍 DataGuardian Pro - System Health Check"
echo "=========================================="

# Check system resources
echo "💾 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%\n", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# Check Docker containers
echo "🐳 Docker Status:"
docker-compose -f /opt/dataguardian/docker-compose.yml ps
echo ""

# Check application health
echo "🚀 Application Health:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200"; then
    echo "✅ Application: Healthy"
else
    echo "❌ Application: Unhealthy"
fi

# Check database connection
echo "🗄️ Database Health:"
if sudo -u postgres psql dataguardian_prod -c "SELECT 1;" &>/dev/null; then
    echo "✅ Database: Connected"
    DB_SIZE=$(sudo -u postgres psql dataguardian_prod -t -c "SELECT pg_size_pretty(pg_database_size('dataguardian_prod'));")
    echo "   Database Size: $DB_SIZE"
else
    echo "❌ Database: Connection failed"
fi

# Check SSL certificate
echo "🔒 SSL Certificate:"
if command -v certbot &> /dev/null; then
    CERT_DAYS=$(certbot certificates 2>/dev/null | grep "VALID" | awk '{print $6}' | head -1)
    if [ ! -z "$CERT_DAYS" ]; then
        echo "✅ SSL Certificate: Valid ($CERT_DAYS days remaining)"
    else
        echo "⚠️ SSL Certificate: Check needed"
    fi
else
    echo "ℹ️ SSL Certificate: Certbot not installed"
fi

# Check disk space
echo "💽 Storage Status:"
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ Disk Usage: $DISK_USAGE% (Warning: >80%)"
else
    echo "✅ Disk Usage: $DISK_USAGE%"
fi

# Check recent errors in logs
echo "📝 Recent Errors:"
ERROR_COUNT=$(docker-compose -f /opt/dataguardian/docker-compose.yml logs --since="24h" dataguardian 2>&1 | grep -i error | wc -l)
if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️ Found $ERROR_COUNT errors in last 24 hours"
    echo "Recent errors:"
    docker-compose -f /opt/dataguardian/docker-compose.yml logs --since="24h" dataguardian 2>&1 | grep -i error | tail -3
else
    echo "✅ No errors in last 24 hours"
fi

# Check backup status
echo "💾 Backup Status:"
if [ -d "/opt/backups" ]; then
    LATEST_BACKUP=$(ls -t /opt/backups/db_backup_*.sql 2>/dev/null | head -1)
    if [ ! -z "$LATEST_BACKUP" ]; then
        BACKUP_DATE=$(stat -c %y "$LATEST_BACKUP" | cut -d' ' -f1)
        echo "✅ Latest backup: $BACKUP_DATE"
    else
        echo "⚠️ No backups found"
    fi
else
    echo "⚠️ Backup directory not found"
fi

echo ""
echo "📊 Quick Stats:"
echo "Uptime: $(uptime -p)"
echo "Users logged in: $(who | wc -l)"
echo "Running processes: $(ps aux | wc -l)"
echo ""

# Performance recommendations
if [ $DISK_USAGE -gt 80 ]; then
    echo "🔧 Recommendations:"
    echo "- Clean old logs: docker system prune -f"
    echo "- Remove old backups: find /opt/backups -mtime +30 -delete"
fi

if [ $ERROR_COUNT -gt 10 ]; then
    echo "🔧 Recommendations:"
    echo "- Check application logs: docker-compose logs dataguardian"
    echo "- Restart application: docker-compose restart dataguardian"
fi

echo "=========================================="
echo "✅ Health check completed - $(date)"