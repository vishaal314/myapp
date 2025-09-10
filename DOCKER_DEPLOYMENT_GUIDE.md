# DataGuardian Pro Docker Deployment Guide

## 🐳 Docker-Based Deployment Options

### Option 1: Using Existing Production Setup

#### Prerequisites
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Quick Production Deployment
```bash
# Option A: Use automated setup script (RECOMMENDED)
bash deploy-setup.sh

# Option B: Manual setup
# 1. Create deployment directory
mkdir -p /opt/dataguardian-pro
cd /opt/dataguardian-pro

# 2. Upload or clone your application files
# Make sure you have:
# - docker-compose.prod.yml
# - nginx.conf.template
# - production.env.template
# - Dockerfile
# - app.py and all Python files

# 3. Configure environment using template
cp production.env.template .env

# Generate secure passwords and keys
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Update .env with generated values
sed -i "s/generate_secure_password_here/$DB_PASSWORD/g" .env
sed -i "s/generate_32_char_secret_key_here/$SECRET_KEY/g" .env

# IMPORTANT: Edit .env to set your domain and API keys
nano .env
# Set: DOMAIN=your-domain.com, CERTBOT_EMAIL=your@email.com, API keys

# 4. Create required directories
mkdir -p {data,logs,cache,reports,backups,ssl,certbot-var}
mkdir -p ssl/{live,archive}
sudo mkdir -p /var/www/html

# 5. Build and start services
docker build -t dataguardian-pro:latest .
docker-compose -f docker-compose.prod.yml up -d

# 6. Generate SSL certificates (after configuring domain in .env)
docker-compose -f docker-compose.prod.yml run --rm certbot
docker-compose -f docker-compose.prod.yml restart nginx

# 7. Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl -f https://your-domain.com
```

### Option 2: Simplified Docker Compose

#### Create Simple docker-compose.yml
```yaml
version: '3.8'

services:
  dataguardian-pro:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:dataguardian2025@db:5432/dataguardian_pro
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./reports:/app/reports
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: dataguardian_pro
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: dataguardian2025
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - dataguardian-pro
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### Deploy with Simple Setup
```bash
# Create project directory
mkdir ~/dataguardian-pro-docker
cd ~/dataguardian-pro-docker

# Save the docker-compose.yml above

# Create basic nginx config
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream app {
        server dataguardian-pro:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF

# Set environment variables
export OPENAI_API_KEY="your_openai_key"
export STRIPE_SECRET_KEY="your_stripe_key"

# Deploy
docker-compose up -d --build
```

### Option 3: Single Docker Container

#### Build and Run Single Container
```bash
# Build the image
docker build -t dataguardian-pro:latest .

# Run with external services
docker run -d \
  --name dataguardian-pro \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://user:pass@external-db:5432/dataguardian_pro" \
  -e REDIS_URL="redis://external-redis:6379/0" \
  -e OPENAI_API_KEY="your_openai_key" \
  -e STRIPE_SECRET_KEY="your_stripe_key" \
  -e ENVIRONMENT="production" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  dataguardian-pro:latest

# Or run with Docker network
docker network create dataguardian-network

# Start PostgreSQL
docker run -d \
  --name postgres \
  --network dataguardian-network \
  -e POSTGRES_DB=dataguardian_pro \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=dataguardian2025 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16

# Start Redis
docker run -d \
  --name redis \
  --network dataguardian-network \
  -v redis_data:/data \
  redis:7-alpine redis-server --appendonly yes

# Start DataGuardian Pro
docker run -d \
  --name dataguardian-pro \
  --network dataguardian-network \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://postgres:dataguardian2025@postgres:5432/dataguardian_pro" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e OPENAI_API_KEY="your_openai_key" \
  -e STRIPE_SECRET_KEY="your_stripe_key" \
  -e ENVIRONMENT="production" \
  dataguardian-pro:latest
```

### Option 4: Docker Swarm (Multi-Node)

#### Initialize Swarm
```bash
# Initialize Docker Swarm
docker swarm init

# Create docker-compose-swarm.yml
cat > docker-compose-swarm.yml << 'EOF'
version: '3.8'

services:
  dataguardian-pro:
    image: dataguardian-pro:latest
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:dataguardian2025@db:5432/dataguardian_pro
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - dataguardian_data:/app/data
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: dataguardian_pro
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: dataguardian2025
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1

volumes:
  postgres_data:
  redis_data:
  dataguardian_data:
EOF

# Deploy to swarm
docker stack deploy -c docker-compose-swarm.yml dataguardian-stack
```

### Option 5: Kubernetes Deployment

#### Create Kubernetes manifests
```yaml
# dataguardian-k8s.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dataguardian-pro
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dataguardian-pro
  template:
    metadata:
      labels:
        app: dataguardian-pro
    spec:
      containers:
      - name: dataguardian-pro
        image: dataguardian-pro:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:dataguardian2025@postgres-service:5432/dataguardian_pro"
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        - name: ENVIRONMENT
          value: "production"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: dataguardian-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: dataguardian-service
spec:
  selector:
    app: dataguardian-pro
  ports:
  - port: 5000
    targetPort: 5000
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dataguardian-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f dataguardian-k8s.yml

# Check status
kubectl get pods
kubectl get services

# Access application
kubectl port-forward service/dataguardian-service 5000:5000
```

## 🔧 Docker Management Commands

### Essential Commands
```bash
# Build image
docker build -t dataguardian-pro:latest .

# View images
docker images

# Run container
docker run -d --name dataguardian-pro -p 5000:5000 dataguardian-pro:latest

# View containers
docker ps -a

# View logs
docker logs dataguardian-pro -f

# Execute commands in container
docker exec -it dataguardian-pro bash

# Stop container
docker stop dataguardian-pro

# Remove container
docker rm dataguardian-pro

# Remove image
docker rmi dataguardian-pro:latest
```

### Docker Compose Commands
```bash
# Start services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Scale services
docker-compose up -d --scale dataguardian-pro=3
```

### Maintenance
```bash
# Clean up unused containers
docker container prune

# Clean up unused images
docker image prune -a

# Clean up volumes
docker volume prune

# Clean up networks
docker network prune

# Clean up everything
docker system prune -a --volumes
```

## 🚀 Production Optimizations

### Multi-Stage Dockerfile
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY production_requirements.txt .
RUN pip install --user -r production_requirements.txt

# Production stage
FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash dataguardian
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/dataguardian/.local
COPY --chown=dataguardian:dataguardian . .

USER dataguardian
ENV PATH=/home/dataguardian/.local/bin:$PATH

EXPOSE 5000
CMD ["streamlit", "run", "app.py", "--server.port", "5000"]
```

### Health Checks
```bash
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Resource Limits
```yaml
# In docker-compose.yml
services:
  dataguardian-pro:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## 📊 Monitoring

### Container Stats
```bash
# View resource usage
docker stats

# Monitor specific container
docker stats dataguardian-pro

# View detailed info
docker inspect dataguardian-pro
```

### Log Management
```bash
# Configure log rotation in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

**Deployment Time:** 15-30 minutes
**Best For:** Containerized environments, cloud deployments
**Recommended:** Use docker-compose.prod.yml for production