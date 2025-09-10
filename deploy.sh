 2>&1; then
            ((failed_checks++))
        fi
    done
    
    if [[ $failed_checks -eq ${#health_endpoints[@]} ]]; then
        log_alert "All application health checks failed"
        cd "$PROJECT_DIR"
        docker compose -f docker-compose.prod.yml restart dataguardian-pro
        log_monitor "Restarted application due to health check failures"
    fi
}

# Check SSL certificate expiration
check_ssl_expiry() {
    if [[ -f "$PROJECT_DIR/ssl/live/$(grep DOMAIN $PROJECT_DIR/.env | cut -d'=' -f2)/fullchain.pem" ]]; then
        local domain=$(grep DOMAIN "$PROJECT_DIR/.env" | cut -d'=' -f2)
        local expiry_date=$(openssl x509 -enddate -noout -in "$PROJECT_DIR/ssl/live/$domain/fullchain.pem" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s)
        local current_epoch=$(date +%s)
        local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [[ $days_until_expiry -lt 30 ]]; then
            log_alert "SSL certificate expires in $days_until_expiry days"
        fi
    fi
}

# Main monitoring execution
log_monitor "Starting monitoring checks..."
check_services
check_disk_space
check_memory
check_health
check_ssl_expiry

# Cleanup old logs (keep 30 days)
find "$PROJECT_DIR/logs" -name "*.log" -mtime +30 -delete

log_monitor "Monitoring checks completed"
EOF

    chmod +x "$PROJECT_DIR/monitor.sh"
    
    # Schedule monitoring every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/monitor.sh") | crontab -
    
    log "System monitoring configured successfully"
}

# Setup automated backups
setup_backups() {
    log "Setting up automated backup system..."
    
    cat > "$PROJECT_DIR/backup.sh" << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/dataguardian-pro"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/logs/backup.log"

# Function to log backup messages
log_backup() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_backup "Starting backup process..."

# Database backup
if docker ps -q -f name=dataguardian-postgres; then
    log_backup "Creating database backup..."
    if docker exec dataguardian-postgres pg_dump -U dataguardian_pro dataguardian_pro | gzip > "$BACKUP_DIR/database/backup_${TIMESTAMP}.sql.gz"; then
        log_backup "Database backup completed successfully"
    else
        log_backup "ERROR: Database backup failed"
    fi
else
    log_backup "WARNING: PostgreSQL container not running, skipping database backup"
fi

# Application data backup
log_backup "Creating application data backup..."
if tar -czf "$BACKUP_DIR/files/data_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" data reports cache 2>/dev/null; then
    log_backup "Application data backup completed successfully"
else
    log_backup "WARNING: Application data backup failed or no data to backup"
fi

# Configuration backup
log_backup "Creating configuration backup..."
if tar -czf "$BACKUP_DIR/files/config_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" .env docker-compose.prod.yml 2>/dev/null; then
    log_backup "Configuration backup completed successfully"
else
    log_backup "WARNING: Configuration backup failed"
fi

# SSL certificates backup (if exists)
if [[ -d "$PROJECT_DIR/ssl/live" ]]; then
    log_backup "Creating SSL certificates backup..."
    if tar -czf "$BACKUP_DIR/files/ssl_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" ssl 2>/dev/null; then
        log_backup "SSL certificates backup completed successfully"
    else
        log_backup "WARNING: SSL certificates backup failed"
    fi
fi

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR/database" -name "backup_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR/files" -name "*_backup_*.tar.gz" -mtime +7 -delete

log_backup "Backup process completed successfully"
EOF

    chmod +x "$PROJECT_DIR/backup.sh"
    
    # Schedule daily backups at 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh >/dev/null 2>&1") | crontab -
    
    log "Automated backup system configured successfully"
}

# Build and deploy application
deploy() {
    log "Building and deploying DataGuardian Pro..."
    
    cd "$PROJECT_DIR"
    
    # Backup before deployment
    backup_database
    
    # Generate secrets and create environment file
    generate_secrets
    create_env_file
    
    # Validate application code exists
    validate_application_code
    
    # Build Docker image if Dockerfile exists
    if [[ -f "Dockerfile" ]]; then
        log "Building Docker image..."
        docker build -t dataguardian-pro:latest .
    else
        warning "Dockerfile not found. Using basic configuration."
    fi
    
    # Start services
    log "Starting application services..."
    docker compose -f docker-compose.prod.yml up -d
    
    # Wait for services to start
    log "Waiting for services to initialize..."
    sleep 60
    
    # Health check
    log "Performing health checks..."
    local retries=0
    local max_retries=12
    
    while [[ $retries -lt $max_retries ]]; do
        if curl -f http://localhost:5000/_stcore/health &>/dev/null || curl -f http://localhost:5000 &>/dev/null; then
            log "✅ Application is healthy and running!"
            break
        else
            retries=$((retries + 1))
            log "Health check $retries/$max_retries - waiting for application..."
            sleep 10
        fi
    done
    
    if [[ $retries -eq $max_retries ]]; then
        warning "Application health check failed. Check logs with: docker compose -f $PROJECT_DIR/docker-compose.prod.yml logs"
    fi
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    cat > /etc/logrotate.d/dataguardian-pro << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart dataguardian-pro >/dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker exec dataguardian-nginx nginx -s reload >/dev/null 2>&1 || true
    endscript
}
EOF

    log "Log rotation configured successfully"
}

# Show deployment summary
show_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              DataGuardian Pro Deployment Complete           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}🌐 Application URLs:${NC}"
    echo "   Primary: https://$DOMAIN"
    echo "   Health Check: https://$DOMAIN/health"
    echo ""
    
    echo -e "${BLUE}📁 Important Paths:${NC}"
    echo "   Installation: $PROJECT_DIR"
    echo "   Logs: $PROJECT_DIR/logs/"
    echo "   Backups: $PROJECT_DIR/backups/"
    echo "   Configuration: $PROJECT_DIR/.env"
    echo ""
    
    echo -e "${BLUE}🐳 Docker Services:${NC}"
    docker compose -f "$PROJECT_DIR/docker-compose.prod.yml" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Services starting..."
    echo ""
    
    echo -e "${BLUE}🔐 Security Features:${NC}"
    echo "   ✅ SSL/TLS certificates (Let's Encrypt)"
    echo "   ✅ Firewall configured (UFW)"
    echo "   ✅ Intrusion detection (Fail2ban)"
    echo "   ✅ Secure database passwords"
    echo ""
    
    echo -e "${BLUE}⚙️ Management Commands:${NC}"
    echo "   View logs: docker compose -f $PROJECT_DIR/docker-compose.prod.yml logs -f"
    echo "   Restart services: docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart"
    echo "   Update application: cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml up -d --build"
    echo "   Manual backup: $PROJECT_DIR/backup.sh"
    echo ""
    
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo "   1. Update API keys in $PROJECT_DIR/.env:"
    echo "      - OPENAI_API_KEY=your_actual_openai_key"
    echo "      - STRIPE_SECRET_KEY=your_actual_stripe_key"
    echo ""
    echo "   2. Restart services after updating API keys:"
    echo "      docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart dataguardian-pro"
    echo ""
    echo "   3. Access your application at: https://$DOMAIN"
    echo ""
    
    echo -e "${GREEN}🎉 DataGuardian Pro is now running successfully!${NC}"
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."
    
    # Stop any temporary containers
    docker stop temp-nginx 2>/dev/null || true
    docker rm temp-nginx 2>/dev/null || true
    
    # Clean up temporary files
    rm -f /tmp/nginx-ssl-setup.conf
    
    log "Cleanup completed"
}

# Signal handlers
trap cleanup EXIT
trap 'error "Deployment interrupted by user"' INT TERM

# Main execution
main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 DataGuardian Pro Deployment                 ║${NC}"
    echo -e "${BLUE}║              Netherlands UAVG Compliance Platform           ║${NC}"
    echo -e "${BLUE}║                      Version 2025.1                         ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_root
    get_user_input
    check_port_conflicts
    
    log "=== DataGuardian Pro Deployment Started ==="
    
    create_directories
    update_system
    install_docker
    setup_firewall
    setup_fail2ban
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        setup_ssl
        setup_ssl_renewal
    else
        warning "Skipping SSL setup for non-production environment"
    fi
    
    deploy
    setup_log_rotation
    setup_backups
    setup_monitoring
    
    log "=== DataGuardian Pro Deployment Completed Successfully ==="
    
    show_summary
}

# Run main function with all arguments
main "$@"