#!/bin/bash

# DataGuardian Pro - Restore Script for Hetzner Deployment
# Restore from backup archives created by backup.sh

set -e

# Configuration
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/dataguardian"
DB_NAME="dataguardian_prod"
DB_USER="dataguardian"

echo "🔄 DataGuardian Pro Restore Script"
echo "=================================="

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# List available backups
echo "📁 Available backups:"
ls -lh $BACKUP_DIR/dataguardian_backup_*_complete.tar.gz 2>/dev/null | nl

if [ $? -ne 0 ]; then
    echo "❌ No backup files found"
    exit 1
fi

# Get backup selection from user
echo ""
read -p "🔢 Enter backup number to restore (or 'latest' for most recent): " BACKUP_CHOICE

if [ "$BACKUP_CHOICE" = "latest" ]; then
    BACKUP_FILE=$(ls -t $BACKUP_DIR/dataguardian_backup_*_complete.tar.gz | head -1)
    echo "📂 Selected latest backup: $(basename $BACKUP_FILE)"
else
    BACKUP_FILE=$(ls -t $BACKUP_DIR/dataguardian_backup_*_complete.tar.gz | sed -n "${BACKUP_CHOICE}p")
    if [ -z "$BACKUP_FILE" ]; then
        echo "❌ Invalid backup number"
        exit 1
    fi
    echo "📂 Selected backup: $(basename $BACKUP_FILE)"
fi

# Confirmation
echo ""
echo "⚠️  WARNING: This will restore DataGuardian Pro from backup"
echo "   This will OVERWRITE current data and configuration"
echo "   Backup file: $BACKUP_FILE"
echo "   Size: $(du -h $BACKUP_FILE | cut -f1)"
read -p "   Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Create temporary restore directory
RESTORE_DIR="/tmp/dataguardian_restore_$$"
mkdir -p $RESTORE_DIR

echo "🔄 Starting restore process..."

# Extract backup archive
echo "📦 Extracting backup archive..."
cd $RESTORE_DIR
tar -xzf $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo "❌ Failed to extract backup archive"
    rm -rf $RESTORE_DIR
    exit 1
fi

# Stop application services
echo "⏹️ Stopping DataGuardian Pro services..."
cd $APP_DIR
docker-compose down

# Backup current state (safety measure)
SAFETY_BACKUP="/tmp/safety_backup_$(date +%Y%m%d_%H%M%S)"
echo "💾 Creating safety backup of current state..."
mkdir -p $SAFETY_BACKUP
cp -r $APP_DIR $SAFETY_BACKUP/
sudo -u postgres pg_dump $DB_NAME > $SAFETY_BACKUP/current_database.sql 2>/dev/null || echo "⚠️ Could not backup current database"

# Restore database
echo "🗄️ Restoring database..."
if [ -f "$RESTORE_DIR/dataguardian_backup_*_database.sql" ]; then
    DB_BACKUP_FILE=$(ls $RESTORE_DIR/dataguardian_backup_*_database.sql)
    
    # Drop and recreate database
    sudo -u postgres dropdb $DB_NAME 2>/dev/null || echo "Database didn't exist"
    sudo -u postgres createdb $DB_NAME --owner=$DB_USER
    
    # Restore database
    sudo -u postgres psql $DB_NAME < $DB_BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        echo "✅ Database restored successfully"
    else
        echo "❌ Database restore failed"
        echo "🔄 Restoring from safety backup..."
        sudo -u postgres dropdb $DB_NAME
        sudo -u postgres createdb $DB_NAME --owner=$DB_USER
        sudo -u postgres psql $DB_NAME < $SAFETY_BACKUP/current_database.sql
        exit 1
    fi
else
    echo "❌ Database backup file not found in archive"
    exit 1
fi

# Restore application files
echo "📁 Restoring application files..."
if [ -f "$RESTORE_DIR/dataguardian_backup_*_app.tar.gz" ]; then
    APP_BACKUP_FILE=$(ls $RESTORE_DIR/dataguardian_backup_*_app.tar.gz)
    
    # Backup and clear current application directory
    rm -rf $APP_DIR.old 2>/dev/null || true
    mv $APP_DIR $APP_DIR.old
    mkdir -p $APP_DIR
    
    # Extract application files
    cd /opt
    tar -xzf $APP_BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        echo "✅ Application files restored"
    else
        echo "❌ Application files restore failed"
        mv $APP_DIR.old $APP_DIR
        exit 1
    fi
else
    echo "❌ Application backup file not found in archive"
    exit 1
fi

# Restore environment configuration
echo "⚙️ Restoring environment configuration..."
if [ -f "$RESTORE_DIR/dataguardian_backup_*_env.txt" ]; then
    ENV_BACKUP_FILE=$(ls $RESTORE_DIR/dataguardian_backup_*_env.txt)
    cp $ENV_BACKUP_FILE $APP_DIR/.env
    echo "✅ Environment configuration restored"
else
    echo "⚠️ Environment file not found, keeping current .env"
fi

# Restore Docker configuration
echo "🐳 Restoring Docker configuration..."
if [ -f "$RESTORE_DIR/dataguardian_backup_*_docker-compose.yml" ]; then
    DOCKER_BACKUP_FILE=$(ls $RESTORE_DIR/dataguardian_backup_*_docker-compose.yml)
    cp $DOCKER_BACKUP_FILE $APP_DIR/docker-compose.yml
    echo "✅ Docker configuration restored"
else
    echo "⚠️ Docker compose file not found in backup"
fi

# Restore system configuration
echo "🔧 Restoring system configuration..."
if [ -f "$RESTORE_DIR/dataguardian_backup_*_system.tar.gz" ]; then
    SYSTEM_BACKUP_FILE=$(ls $RESTORE_DIR/dataguardian_backup_*_system.tar.gz)
    cd /
    tar -xzf $SYSTEM_BACKUP_FILE 2>/dev/null
    echo "✅ System configuration restored"
    
    # Reload nginx configuration
    nginx -t && systemctl reload nginx
else
    echo "⚠️ System configuration not found in backup"
fi

# Set proper permissions
echo "🔐 Setting proper permissions..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Start services
echo "🚀 Starting DataGuardian Pro services..."
cd $APP_DIR

# Rebuild Docker image if needed
docker-compose build --no-cache

# Start services
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Verify restoration
echo "🔍 Verifying restoration..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200"; then
    echo "✅ Application is responding"
else
    echo "⚠️ Application may not be fully started yet"
fi

# Test database connection
if sudo -u postgres psql $DB_NAME -c "SELECT 1;" &>/dev/null; then
    echo "✅ Database connection verified"
    TABLE_COUNT=$(sudo -u postgres psql $DB_NAME -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
    echo "   Tables restored: $TABLE_COUNT"
else
    echo "❌ Database connection failed"
fi

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf $RESTORE_DIR

echo ""
echo "✅ Restore process completed!"
echo "📁 Safety backup of previous state saved in: $SAFETY_BACKUP"
echo "🌐 Application should be available at: http://$(curl -s ifconfig.me)"
echo ""
echo "📋 Post-restore checklist:"
echo "   1. Test application login"
echo "   2. Verify scanner functionality"
echo "   3. Check SSL certificate (if using domain)"
echo "   4. Review logs: docker-compose logs -f dataguardian"
echo "   5. Remove safety backup when satisfied: rm -rf $SAFETY_BACKUP"
echo ""
echo "🆘 If issues occur, you can restore from safety backup manually"