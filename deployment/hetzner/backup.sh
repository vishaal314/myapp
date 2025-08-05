#!/bin/bash

# DataGuardian Pro - Backup Script for Hetzner Deployment
# Automated backup solution for database and application files

set -e

# Configuration
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/dataguardian"
DB_NAME="dataguardian_prod"
DB_USER="dataguardian"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Get current date for backup filename
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dataguardian_backup_$DATE"

echo "🔄 Starting DataGuardian Pro backup - $(date)"

# Database backup
echo "📁 Backing up PostgreSQL database..."
sudo -u postgres pg_dump $DB_NAME > "${BACKUP_FILE}_database.sql"

if [ $? -eq 0 ]; then
    echo "✅ Database backup completed"
    DB_SIZE=$(du -h "${BACKUP_FILE}_database.sql" | cut -f1)
    echo "   Database backup size: $DB_SIZE"
else
    echo "❌ Database backup failed"
    exit 1
fi

# Application files backup (excluding temp files)
echo "📦 Backing up application files..."
tar -czf "${BACKUP_FILE}_app.tar.gz" \
    --exclude="$APP_DIR/temp/*" \
    --exclude="$APP_DIR/logs/*" \
    --exclude="$APP_DIR/__pycache__" \
    --exclude="$APP_DIR/.git" \
    -C /opt dataguardian

if [ $? -eq 0 ]; then
    echo "✅ Application backup completed"
    APP_SIZE=$(du -h "${BACKUP_FILE}_app.tar.gz" | cut -f1)
    echo "   Application backup size: $APP_SIZE"
else
    echo "❌ Application backup failed"
    exit 1
fi

# Environment backup (sensitive data)
echo "🔐 Backing up environment configuration..."
cp "$APP_DIR/.env" "${BACKUP_FILE}_env.txt"

# Docker configuration backup
echo "🐳 Backing up Docker configuration..."
cp "$APP_DIR/docker-compose.yml" "${BACKUP_FILE}_docker-compose.yml"

# System configuration backup
echo "⚙️ Backing up system configuration..."
tar -czf "${BACKUP_FILE}_system.tar.gz" \
    /etc/nginx/sites-available/dataguardian \
    /etc/postgresql/*/main/postgresql.conf \
    /etc/postgresql/*/main/pg_hba.conf \
    2>/dev/null || echo "Some system files skipped"

# Compress everything into single archive
echo "📦 Creating complete backup archive..."
tar -czf "${BACKUP_FILE}_complete.tar.gz" \
    "${BACKUP_FILE}_database.sql" \
    "${BACKUP_FILE}_app.tar.gz" \
    "${BACKUP_FILE}_env.txt" \
    "${BACKUP_FILE}_docker-compose.yml" \
    "${BACKUP_FILE}_system.tar.gz"

# Clean up individual files
rm -f "${BACKUP_FILE}_database.sql" \
      "${BACKUP_FILE}_app.tar.gz" \
      "${BACKUP_FILE}_env.txt" \
      "${BACKUP_FILE}_docker-compose.yml" \
      "${BACKUP_FILE}_system.tar.gz"

COMPLETE_SIZE=$(du -h "${BACKUP_FILE}_complete.tar.gz" | cut -f1)
echo "✅ Complete backup created: $COMPLETE_SIZE"

# Clean old backups
echo "🧹 Cleaning old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "dataguardian_backup_*" -mtime +$RETENTION_DAYS -delete
REMAINING_BACKUPS=$(ls -1 $BACKUP_DIR/dataguardian_backup_* 2>/dev/null | wc -l)
echo "   Remaining backups: $REMAINING_BACKUPS"

# Backup verification
echo "🔍 Verifying backup integrity..."
if tar -tzf "${BACKUP_FILE}_complete.tar.gz" >/dev/null 2>&1; then
    echo "✅ Backup integrity verified"
else
    echo "❌ Backup integrity check failed"
    exit 1
fi

# Create backup report
REPORT_FILE="$BACKUP_DIR/backup_report_$DATE.txt"
cat > $REPORT_FILE << EOF
DataGuardian Pro Backup Report
==============================
Date: $(date)
Backup File: ${BACKUP_FILE}_complete.tar.gz
Size: $COMPLETE_SIZE

Components Backed Up:
✅ PostgreSQL Database ($DB_NAME)
✅ Application Files
✅ Environment Configuration
✅ Docker Configuration
✅ System Configuration

Backup Location: $BACKUP_DIR
Retention: $RETENTION_DAYS days
Remaining Backups: $REMAINING_BACKUPS

Status: SUCCESS
EOF

echo "📋 Backup report created: $REPORT_FILE"

# Optional: Upload to cloud storage (uncomment and configure as needed)
# echo "☁️ Uploading to cloud storage..."
# aws s3 cp "${BACKUP_FILE}_complete.tar.gz" s3://your-bucket/dataguardian-backups/
# echo "✅ Cloud upload completed"

echo "✅ Backup process completed successfully - $(date)"
echo "📁 Backup saved as: ${BACKUP_FILE}_complete.tar.gz"

# Display storage usage
echo ""
echo "💽 Backup Storage Summary:"
echo "Total backup size: $(du -sh $BACKUP_DIR | cut -f1)"
echo "Available disk space: $(df -h $BACKUP_DIR | awk 'NR==2{print $4}')"