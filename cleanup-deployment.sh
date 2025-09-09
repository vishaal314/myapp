#!/bin/bash

# DataGuardian Pro Server Cleanup Script
# Run this when you need to free up disk space on your server

echo "🧹 Starting DataGuardian Pro server cleanup..."

# Stop services gracefully
echo "Stopping services..."
cd /opt/dataguardian-pro
docker-compose -f docker-compose.prod.yml down || echo "Services already stopped"

# Clean up Docker resources
echo "Cleaning up Docker resources..."
docker system prune -af --volumes
docker builder prune -af

# Clean up old backups (keep last 3 days only)
echo "Cleaning up old backups..."
find /opt/dataguardian-pro/backups -name "backup_*.sql" -mtime +3 -delete 2>/dev/null || echo "No old backups found"

# Clean up old logs (keep last 7 days only)
echo "Cleaning up old logs..."
find /opt/dataguardian-pro/logs -name "*.log" -mtime +7 -delete 2>/dev/null || echo "No old logs found"

# Clean up system packages
echo "Cleaning up system packages..."
apt autoremove -y
apt autoclean

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -rf /tmp/*
rm -rf /var/tmp/*

# Show final disk usage
echo "Final disk usage:"
df -h

echo "✅ Cleanup completed! You can now restart your services with:"
echo "cd /opt/dataguardian-pro && docker-compose -f docker-compose.prod.yml up -d"