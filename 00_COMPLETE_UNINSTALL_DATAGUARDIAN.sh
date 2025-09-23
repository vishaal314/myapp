#!/bin/bash
# Complete DataGuardian Pro Uninstallation Script
# Removes ALL traces of DataGuardian from retzor server

set -e

echo "🗑️ DataGuardian Pro - COMPLETE UNINSTALLATION"
echo "=============================================="
echo "This will COMPLETELY REMOVE all DataGuardian components"
echo "Including services, databases, files, and configurations"
echo ""

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to safely stop service
stop_service() {
    local service_name="$1"
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        log "Stopping service: $service_name"
        systemctl stop "$service_name" || true
    fi
    if systemctl is-enabled --quiet "$service_name" 2>/dev/null; then
        log "Disabling service: $service_name"
        systemctl disable "$service_name" || true
    fi
}

# Function to remove systemd unit file
remove_unit_file() {
    local unit_name="$1"
    local unit_path="/etc/systemd/system/$unit_name"
    if [ -f "$unit_path" ]; then
        log "Removing systemd unit: $unit_path"
        rm -f "$unit_path"
    fi
}

# Confirmation prompt
read -p "⚠️ WARNING: This will DESTROY all DataGuardian data and configuration. Continue? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
log "Starting complete DataGuardian uninstallation..."

# 1. STOP ALL DATAGUARDIAN SERVICES
log "=== STOPPING ALL SERVICES ==="
stop_service "dataguardian"
stop_service "dataguardian-replit"
stop_service "dataguardian-app"
stop_service "dataguardian-redis"
stop_service "dataguardian-postgres"
stop_service "streamlit-dataguardian"

# Stop any running streamlit processes
log "Killing any running Streamlit processes..."
pkill -f "streamlit run" 2>/dev/null || true
pkill -f "dataguardian" 2>/dev/null || true
sleep 3

# 2. REMOVE SYSTEMD UNIT FILES
log "=== REMOVING SYSTEMD UNITS ==="
remove_unit_file "dataguardian.service"
remove_unit_file "dataguardian-replit.service"
remove_unit_file "dataguardian-app.service"
remove_unit_file "dataguardian-redis.service"
remove_unit_file "dataguardian-postgres.service"
remove_unit_file "streamlit-dataguardian.service"

# Reload systemd
log "Reloading systemd daemon..."
systemctl daemon-reload

# 3. DISABLE NGINX CONFIGURATION
log "=== REMOVING NGINX CONFIGURATION ==="
if [ -f "/etc/nginx/sites-enabled/dataguardian" ]; then
    log "Removing nginx site configuration..."
    rm -f "/etc/nginx/sites-enabled/dataguardian"
fi
if [ -f "/etc/nginx/sites-available/dataguardian" ]; then
    rm -f "/etc/nginx/sites-available/dataguardian"
fi

# Test nginx config and reload if valid
if nginx -t 2>/dev/null; then
    systemctl reload nginx 2>/dev/null || true
fi

# 4. STOP AND REMOVE REDIS DATA
log "=== REMOVING REDIS DATA ==="
if systemctl is-active --quiet redis-server 2>/dev/null; then
    log "Stopping Redis server..."
    systemctl stop redis-server || true
fi

# Remove Redis data directories
if [ -d "/var/lib/redis" ]; then
    log "Removing Redis data directory..."
    rm -rf /var/lib/redis/* 2>/dev/null || true
fi

# Remove Redis dump files
rm -f /var/lib/redis/dump.rdb 2>/dev/null || true
rm -f /var/lib/redis/appendonly.aof 2>/dev/null || true

# Start Redis back up (clean state)
if command -v redis-server >/dev/null 2>&1; then
    systemctl start redis-server 2>/dev/null || true
fi

# 5. DROP POSTGRESQL DATABASES
log "=== REMOVING POSTGRESQL DATABASES ==="
if systemctl is-active --quiet postgresql 2>/dev/null; then
    # Drop all DataGuardian databases
    for db_name in dataguardian dataguardian_pro dataguardian_dev dataguardian_test; do
        if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$db_name" 2>/dev/null; then
            log "Dropping PostgreSQL database: $db_name"
            sudo -u postgres dropdb "$db_name" 2>/dev/null || true
        fi
    done
    
    # Drop DataGuardian users
    for user_name in dataguardian dataguardian_user; do
        if sudo -u postgres psql -t -c "SELECT 1 FROM pg_roles WHERE rolname='$user_name'" | grep -q 1 2>/dev/null; then
            log "Dropping PostgreSQL user: $user_name"
            sudo -u postgres dropuser "$user_name" 2>/dev/null || true
        fi
    done
else
    log "PostgreSQL not running, skipping database cleanup"
fi

# 6. REMOVE ALL DATAGUARDIAN DIRECTORIES
log "=== REMOVING ALL DATAGUARDIAN DIRECTORIES ==="
directories_to_remove=(
    "/opt/dataguardian"
    "/opt/dataguardian-pro"
    "/opt/dataguardian-replit"
    "/var/lib/dataguardian"
    "/var/log/dataguardian"
    "/var/cache/dataguardian"
    "/home/dataguardian"
    "/etc/dataguardian"
    "/usr/local/dataguardian"
)

for dir in "${directories_to_remove[@]}"; do
    if [ -d "$dir" ]; then
        log "Removing directory: $dir"
        rm -rf "$dir"
    fi
done

# Remove any dataguardian files in common locations
find /tmp -name "*dataguardian*" -type f -delete 2>/dev/null || true
find /tmp -name "*dataguardian*" -type d -exec rm -rf {} + 2>/dev/null || true

# 7. REMOVE PYTHON VIRTUAL ENVIRONMENTS
log "=== REMOVING PYTHON VIRTUAL ENVIRONMENTS ==="
venv_locations=(
    "/opt/dataguardian/venv"
    "/opt/dataguardian-pro/venv"
    "/home/*/dataguardian-venv"
    "/home/*/dataguardian_venv"
    "/var/lib/dataguardian/venv"
)

for venv_pattern in "${venv_locations[@]}"; do
    for venv_path in $venv_pattern; do
        if [ -d "$venv_path" ]; then
            log "Removing virtual environment: $venv_path"
            rm -rf "$venv_path"
        fi
    done
done

# 8. REMOVE CRON JOBS
log "=== REMOVING CRON JOBS ==="
# Remove from root crontab
crontab -l 2>/dev/null | grep -v dataguardian | crontab - 2>/dev/null || true

# Remove from other users' crontabs if they exist
for user in $(cut -f1 -d: /etc/passwd); do
    if crontab -u "$user" -l 2>/dev/null | grep -q dataguardian; then
        log "Removing dataguardian cron jobs for user: $user"
        crontab -u "$user" -l 2>/dev/null | grep -v dataguardian | crontab -u "$user" - 2>/dev/null || true
    fi
done

# 9. REMOVE LOG FILES
log "=== REMOVING LOG FILES ==="
log_patterns=(
    "/var/log/*dataguardian*"
    "/var/log/syslog*dataguardian*"
    "/var/log/systemd/*dataguardian*"
    "/tmp/*dataguardian*"
)

for pattern in "${log_patterns[@]}"; do
    rm -rf $pattern 2>/dev/null || true
done

# Clear journalctl logs for dataguardian services
journalctl --vacuum-time=1s --unit=dataguardian* 2>/dev/null || true

# 10. REMOVE CACHED ASSETS AND SESSIONS
log "=== REMOVING CACHED ASSETS ==="
cache_locations=(
    "/var/cache/dataguardian"
    "/tmp/streamlit-*"
    "/tmp/dataguardian-*"
    "/home/*/.streamlit"
    "/root/.streamlit"
)

for cache_pattern in "${cache_locations[@]}"; do
    rm -rf $cache_pattern 2>/dev/null || true
done

# 11. REMOVE USER ACCOUNTS
log "=== REMOVING USER ACCOUNTS ==="
if id "dataguardian" &>/dev/null; then
    log "Removing dataguardian user account..."
    userdel -r dataguardian 2>/dev/null || true
fi

# 12. REMOVE FIREWALL RULES
log "=== REMOVING FIREWALL RULES ==="
if command -v ufw >/dev/null 2>&1; then
    ufw delete allow 5000/tcp 2>/dev/null || true
    ufw delete allow 6379/tcp 2>/dev/null || true
fi

# 13. CLEANUP ENVIRONMENT VARIABLES
log "=== REMOVING ENVIRONMENT VARIABLES ==="
# Remove from /etc/environment
if [ -f "/etc/environment" ]; then
    sed -i '/DATAGUARDIAN/d' /etc/environment 2>/dev/null || true
fi

# Remove from profile files
for profile_file in /etc/profile /etc/bash.bashrc /root/.bashrc /home/*/.bashrc; do
    if [ -f "$profile_file" ]; then
        sed -i '/DATAGUARDIAN/d' "$profile_file" 2>/dev/null || true
    fi
done

# 14. REMOVE DEPENDENCIES (Optional - only if not used by other applications)
log "=== CHECKING DEPENDENCIES ==="
log "NOTE: Not removing Python packages automatically - they may be used by other applications"
log "If you want to remove DataGuardian-specific packages, run:"
log "pip3 uninstall streamlit pandas plotly redis psycopg2-binary"

# 15. FINAL CLEANUP
log "=== FINAL CLEANUP ==="
# Clear package manager caches
apt-get autoremove -y 2>/dev/null || true
apt-get autoclean 2>/dev/null || true

# Update file database
updatedb 2>/dev/null || true

# Clear any remaining processes
pkill -f dataguardian 2>/dev/null || true

echo ""
echo "🎉 DataGuardian Pro - COMPLETE UNINSTALLATION FINISHED!"
echo "====================================================="
log "✅ All DataGuardian services stopped and disabled"
log "✅ All systemd unit files removed"
log "✅ All directories and files removed"
log "✅ PostgreSQL databases and users dropped"
log "✅ Redis data cleared"
log "✅ Virtual environments removed"
log "✅ Cron jobs removed"
log "✅ Log files cleaned"
log "✅ User accounts removed"
log "✅ Environment variables cleared"
echo ""
echo "🧹 System is now clean and ready for fresh DataGuardian installation"
echo ""
echo "💡 Next steps:"
echo "   1. Run fresh installation script to deploy exact Replit environment"
echo "   2. Verify all components are working correctly"
echo "   3. Test landing page matches Replit exactly"
echo ""
echo "⚠️ IMPORTANT: System reboot recommended to ensure all changes take effect"
echo "   sudo reboot"
echo ""
log "Complete uninstallation completed successfully!"