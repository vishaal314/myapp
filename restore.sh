#!/bin/bash

# DataGuardian Pro Restore Script
# Restore from backup files

set -e

BACKUP_DIR="/opt/dataguardian-pro/backups"
PROJECT_DIR="/opt/dataguardian-pro"

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

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# List available backups
list_backups() {
    log "Available backups:"
    echo ""
    echo "Database backups:"
    ls -la "${BACKUP_DIR}/database/"*.sql.gz 2>/dev/null | awk '{print $9 " (" $5 " bytes, " $6 " " $7 " " $8 ")"}'
    echo ""
    echo "Files backups:"
    ls -la "${BACKUP_DIR}/files/"*.tar.gz 2>/dev/null | awk '{print $9 " (" $5 " bytes, " $6 " " $7 " " $8 ")"}'
    echo ""
    echo "Configuration backups:"
    ls -la "${BACKUP_DIR}/config/"*.tar.gz 2>/dev/null | awk '{print $9 " (" $5 " bytes, " $6 " " $7 " " $8 ")"}'
    echo ""
}

# Restore database
restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        error "Please specify database backup file"
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "Database backup file not found: $backup_file"
    fi
    
    log "Restoring database from: $backup_file"
    
    # Stop application
    docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" stop dataguardian-pro
    
    # Create new database backup before restore
    log "Creating safety backup before restore..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker exec dataguardian-postgres pg_dump -U dataguardian_pro -d dataguardian_pro > "${BACKUP_DIR}/database/safety_backup_${timestamp}.sql"
    
    # Drop and recreate database
    docker exec dataguardian-postgres dropdb -U dataguardian_pro dataguardian_pro
    docker exec dataguardian-postgres createdb -U dataguardian_pro dataguardian_pro
    
    # Restore from backup
    gunzip -c "$backup_file" | docker exec -i dataguardian-postgres psql -U dataguardian_pro -d dataguardian_pro
    
    # Start application
    docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" start dataguardian-pro
    
    log "✅ Database restored successfully"
}

# Restore files
restore_files() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        error "Please specify files backup file"
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "Files backup file not found: $backup_file"
    fi
    
    log "Restoring files from: $backup_file"
    
    # Create safety backup
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "${BACKUP_DIR}/files/safety_files_backup_${timestamp}.tar.gz" -C "$PROJECT_DIR" data reports cache 2>/dev/null || true
    
    # Restore files
    tar -xzf "$backup_file" -C "$PROJECT_DIR"
    
    # Fix permissions
    chown -R root:root "$PROJECT_DIR"/{data,reports,cache}
    
    log "✅ Files restored successfully"
}

# Restore configuration
restore_config() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        error "Please specify configuration backup file"
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "Configuration backup file not found: $backup_file"
    fi
    
    log "Restoring configuration from: $backup_file"
    
    # Create safety backup
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "${BACKUP_DIR}/config/safety_config_backup_${timestamp}.tar.gz" -C "$PROJECT_DIR" docker-compose.prod.yml nginx.conf .env 2>/dev/null || true
    
    # Restore configuration
    tar -xzf "$backup_file" -C "$PROJECT_DIR"
    
    log "✅ Configuration restored successfully"
    warning "Please restart services manually: docker-compose -f $PROJECT_DIR/docker-compose.prod.yml restart"
}

# Interactive restore
interactive_restore() {
    echo "DataGuardian Pro Interactive Restore"
    echo "====================================="
    
    list_backups
    
    echo "What would you like to restore?"
    echo "1) Database"
    echo "2) Files"
    echo "3) Configuration"
    echo "4) All (Database + Files + Configuration)"
    echo "5) Exit"
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            echo "Enter full path to database backup file:"
            read -p "> " db_file
            restore_database "$db_file"
            ;;
        2)
            echo "Enter full path to files backup file:"
            read -p "> " files_file
            restore_files "$files_file"
            ;;
        3)
            echo "Enter full path to configuration backup file:"
            read -p "> " config_file
            restore_config "$config_file"
            ;;
        4)
            echo "Enter timestamp for backups (format: YYYYMMDD_HHMMSS):"
            read -p "> " timestamp
            restore_database "${BACKUP_DIR}/database/dataguardian_db_${timestamp}.sql.gz"
            restore_files "${BACKUP_DIR}/files/dataguardian_files_${timestamp}.tar.gz"
            restore_config "${BACKUP_DIR}/config/dataguardian_config_${timestamp}.tar.gz"
            ;;
        5)
            log "Restore cancelled"
            exit 0
            ;;
        *)
            error "Invalid choice"
            ;;
    esac
}

# Main function
main() {
    log "=== DataGuardian Pro Restore Tool ==="
    
    if [ $# -eq 0 ]; then
        interactive_restore
    else
        case "$1" in
            "list")
                list_backups
                ;;
            "database")
                restore_database "$2"
                ;;
            "files")
                restore_files "$2"
                ;;
            "config")
                restore_config "$2"
                ;;
            *)
                echo "Usage: $0 [list|database|files|config] [backup_file]"
                echo "       $0  (interactive mode)"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"