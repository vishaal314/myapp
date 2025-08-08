# DataGuardian Pro - Docker Standalone Deployment

## Quick Start

Deploy DataGuardian Pro as a standalone Docker container for enterprise environments.

### Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### 1. One-Command Deployment

```bash
# Download and start
curl -sSL https://github.com/your-org/dataguardian-pro/raw/main/deployment/standalone/docker/quick-deploy.sh | bash
```

### 2. Manual Deployment

```bash
# Clone repository
git clone https://github.com/your-org/dataguardian-pro.git
cd dataguardian-pro/deployment/standalone/docker

# Start with SQLite (simple)
docker-compose up -d

# Start with PostgreSQL (enterprise)
docker-compose --profile enterprise up -d
```

### 3. Access Application

- **URL**: http://localhost:8501
- **Default login**: Admin/admin (change on first login)
- **License**: 30-day demo included

## Configuration

### Environment Variables

```bash
# Create .env file
cat > .env << EOF
POSTGRES_PASSWORD=your_secure_password
OPENAI_API_KEY=your_openai_key
STRIPE_SECRET_KEY=your_stripe_key
DEFAULT_REGION=Netherlands
COMPLIANCE_MODE=UAVG
EOF
```

### Volume Mapping

- `/app/data` - Database and user data
- `/app/reports` - Generated reports
- `/app/licenses` - License files
- `/app/config` - Custom configuration

## Enterprise Features

### PostgreSQL Database

```bash
# Start with PostgreSQL
docker-compose --profile enterprise up -d

# Connect to database
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian
```

### License Management

```bash
# Add license file
mkdir -p ./licenses
echo "YOUR_LICENSE_KEY" > ./licenses/license.key

# Restart container
docker-compose restart dataguardian-standalone
```

### Backup & Restore

```bash
# Backup data
docker run --rm -v dataguardian_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data

# Restore data
docker run --rm -v dataguardian_data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz
```

## Monitoring

### Health Checks

```bash
# Check container health
docker-compose ps

# View logs
docker-compose logs -f dataguardian-standalone

# Monitor resources
docker stats dataguardian-pro-standalone
```

### Metrics

Available at: http://localhost:8501/_stcore/health

## Scaling

### Single Instance
- **Users**: 1-50 concurrent
- **Resources**: 2 CPU, 4GB RAM
- **Storage**: 20GB

### High Availability
- **Users**: 50-200 concurrent
- **Resources**: 4 CPU, 8GB RAM
- **Storage**: 100GB
- **Setup**: Load balancer + multiple containers

## Security

### Network Security

```bash
# Custom network
docker network create dataguardian-secure

# Run with custom network
docker-compose -f docker-compose.secure.yml up -d
```

### SSL/TLS

```bash
# Add SSL certificates
mkdir -p ./ssl
# Copy your SSL files to ./ssl/

# Update docker-compose.yml
volumes:
  - ./ssl:/app/ssl:ro
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs dataguardian-pro-standalone

# Check port conflicts
netstat -tulpn | grep 8501
```

**Database connection issues:**
```bash
# Test database connection
docker exec dataguardian-postgres pg_isready -U dataguardian

# Reset database
docker-compose down -v
docker-compose up -d
```

**Permission issues:**
```bash
# Fix permissions
sudo chown -R 1000:1000 ./data ./reports ./licenses
```

## Support

- **Documentation**: Full docs at `/docs` endpoint
- **Logs**: Available in container logs
- **Health**: Monitor at `/_stcore/health`
- **Enterprise Support**: Contact your account manager

## License Tiers

| Feature | Demo | Professional | Enterprise |
|---------|------|--------------|------------|
| Users | 5 | 50 | Unlimited |
| Scans/Month | 100 | 10,000 | Unlimited |
| Support | Community | Email | Phone + Dedicated |
| Price | Free | €999/year | €2,999/year |

## Upgrade Path

1. **Demo → Professional**: Add license key
2. **Professional → Enterprise**: Upgrade license + PostgreSQL
3. **Scale**: Add load balancer + multiple containers

Your DataGuardian Pro standalone deployment is ready for enterprise use!