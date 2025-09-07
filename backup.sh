#!/bin/bash

# DataGuardian Pro Backup Script
# Automated backup solution for database, files, and configuration

set -e

BACKUP_DIR="/opt/dataguardian-pro/backups"
PROJECT_DIR="/opt/dataguardian-pro"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Create backup directories
create_backup_dirs() {
    mkdir -p "${BACKUP_DIR}"/{database,files,config}
    log "Backup directories created"
}

# Backup PostgreSQL database
backup_database() {
    log "Starting database backup..."
    
    if docker ps -q -f name=dataguardian-postgres; then
        # Create database dump
        docker exec dataguardian-postgres pg_dump -U dataguardian_pro -d dataguardian_pro > "${BACKUP_DIR}/database/dataguardian_db_${TIMESTAMP}.sql"
        
        # Compress the backup
        gzip "${BACKUP_DIR}/database/dataguardian_db_${TIMESTAMP}.sql"
        
        log "Database backup completed: dataguardian_db_${TIMESTAMP}.sql.gz"
    else
        error "PostgreSQL container is not running"
    fi
}

# Backup application files
backup_files() {
    log "Starting files backup..."
    
    # Backup reports, data, and logs
    tar -czf "${BACKUP_DIR}/files/dataguardian_files_${TIMESTAMP}.tar.gz" \
        -C "$PROJECT_DIR" \
        --exclude='backups' \
        --exclude='*.log' \
        data reports cache ssl 2>/dev/null || log "Some files may not exist, continuing..."
    
    log "Files backup completed: dataguardian_files_${TIMESTAMP}.tar.gz"
}

# Backup configuration
backup_config() {
    log "Starting configuration backup..."
    
    # Backup Docker Compose and configuration files
    tar -czf "${BACKUP_DIR}/config/dataguardian_config_${TIMESTAMP}.tar.gz" \
        -C "$PROJECT_DIR" \
        docker-compose.prod.yml nginx.conf .env deploy.sh backup.sh 2>/dev/null || log "Some config files may not exist, continuing..."
    
    log "Configuration backup completed: dataguardian_config_${TIMESTAMP}.tar.gz"
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    find "${BACKUP_DIR}/database" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "${BACKUP_DIR}/files" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "${BACKUP_DIR}/config" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    log "Cleanup completed"
}

# Create backup summary
create_backup_summary() {
    SUMMARY_FILE="${BACKUP_DIR}/backup_summary_${TIMESTAMP}.txt"
    
    cat > "$SUMMARY_FILE" << EOF
DataGuardian Pro Backup Summary
Generated: $(date)
Backup Directory: $BACKUP_DIR

Database Backup:
- File: dataguardian_db_${TIMESTAMP}.sql.gz
- Size: $(du -h "${BACKUP_DIR}/database/dataguardian_db_${TIMESTAMP}.sql.gz" 2>/dev/null | cut -f1 || echo "N/A")

Files Backup:
- File: dataguardian_files_${TIMESTAMP}.tar.gz
- Size: $(du -h "${BACKUP_DIR}/files/dataguardian_files_${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1 || echo "N/A")

Configuration Backup:
- File: dataguardian_config_${TIMESTAMP}.tar.gz
- Size: $(du -h "${BACKUP_DIR}/config/dataguardian_config_${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1 || echo "N/A")

Total Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)
EOF

    log "Backup summary created: backup_summary_${TIMESTAMP}.txt"
}

# Test backup integrity
test_backup_integrity() {
    log "Testing backup integrity..."
    
    # Test database backup
    if [ -f "${BACKUP_DIR}/database/dataguardian_db_${TIMESTAMP}.sql.gz" ]; then
        if gzip -t "${BACKUP_DIR}/database/dataguardian_db_${TIMESTAMP}.sql.gz"; then
            log "✅ Database backup integrity OK"
        else
            error "❌ Database backup integrity check failed"
        fi
    fi
    
    # Test file backup
    if [ -f "${BACKUP_DIR}/files/dataguardian_files_${TIMESTAMP}.tar.gz" ]; then
        if tar -tzf "${BACKUP_DIR}/files/dataguardian_files_${TIMESTAMP}.tar.gz" >/dev/null; then
            log "✅ Files backup integrity OK"
        else
            error "❌ Files backup integrity check failed"
        fi
    fi
    
    # Test config backup
    if [ -f "${BACKUP_DIR}/config/dataguardian_config_${TIMESTAMP}.tar.gz" ]; then
        if tar -tzf "${BACKUP_DIR}/config/dataguardian_config_${TIMESTAMP}.tar.gz" >/dev/null; then
            log "✅ Configuration backup integrity OK"
        else
            error "❌ Configuration backup integrity check failed"
        fi
    fi
}

# Main backup function
main() {
    log "=== DataGuardian Pro Backup Started ==="
    
    create_backup_dirs
    backup_database
    backup_files
    backup_config
    test_backup_integrity
    create_backup_summary
    cleanup_old_backups
    
    log "=== Backup Process Complete ==="
    log "📁 Backups stored in: $BACKUP_DIR"
    log "📊 Total backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
}

# Run main function
main "$@"