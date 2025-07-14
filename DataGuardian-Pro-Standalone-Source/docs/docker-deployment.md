# Docker Deployment Guide for DataGuardian Pro

This document provides detailed instructions for deploying DataGuardian Pro using Docker and Docker Compose.

## Prerequisites

- Docker Engine v20.10.0 or higher
- Docker Compose v2.0.0 or higher
- Git (for cloning the repository)
- 4GB RAM minimum (8GB recommended)
- 20GB disk space minimum

## Quick Start

The easiest way to deploy DataGuardian Pro is using the provided deployment script:

```bash
git clone [repository-url]
cd dataguardian-pro
./deploy.sh
```

The script will:
1. Check for Docker and Docker Compose
2. Create default config files if needed
3. Build and start the containers
4. Provide access URLs when ready

## Manual Deployment Steps

### 1. Clone the Repository

```bash
git clone [repository-url]
cd dataguardian-pro
```

### 2. Configure Environment Variables

Create a `.env` file based on the provided example:

```bash
cp .env.example .env
```

Edit the `.env` file to set:
- Database credentials (strongly recommended to change from defaults)
- Application port if 5000 is already in use
- API keys for external services if needed
- Other configuration options

### 3. Build the Containers

```bash
docker-compose build
```

This will build the DataGuardian Pro application container using the provided Dockerfile.

### 4. Start the Services

```bash
docker-compose up -d
```

The `-d` flag runs containers in the background (detached mode).

### 5. Verify Deployment

Check that the containers are running:

```bash
docker-compose ps
```

You should see both services (`app` and `db`) with status "Up".

### 6. Access the Application

Open your browser and navigate to:
- http://localhost:5000 (or your configured port)

## Configuration Options

### Database

The PostgreSQL database is configured in `docker-compose.yml` with these defaults:
- **User**: dataguardian
- **Password**: dataguardian (change this in .env!)
- **Database**: dataguardian
- **Port**: 5432 (internal), mapped to host port in .env

For production, change these values in the `.env` file.

### Application

Application configuration in `.env` includes:
- **APP_PORT**: The port to access the web interface (default: 5000)
- **DEBUG**: Set to "true" for verbose logging (default: false)
- **ENVIRONMENT**: "production" or "development" (default: production)

### Persistent Data

The following directories persist data between container restarts:
- `./reports`: Stores generated reports
- `./uploads`: Temporary storage for uploaded files
- PostgreSQL data is stored in a named volume: `postgres_data`

## Maintenance

### Viewing Logs

```bash
docker-compose logs -f
```

Use `Ctrl+C` to exit log viewing.

To view logs for a specific service:

```bash
docker-compose logs -f app
docker-compose logs -f db
```

### Stopping the Services

```bash
docker-compose down
```

This stops and removes the containers but preserves volumes and data.

### Removing All Data

```bash
docker-compose down -v
```

Warning: The `-v` flag removes all volumes, including the database data.

### Updating

To update to a new version:

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

## Customization

### Custom Database Initialization

The database is initialized using `database/postgres-init.sql`. You can modify this file to:
- Add custom tables
- Change default users
- Add initial data

If you've already started the containers, you'll need to reset the database:

```bash
docker-compose down -v
docker-compose up -d
```

### Using External PostgreSQL

To use an existing PostgreSQL server instead of the containerized one:

1. Edit `docker-compose.yml` to remove the `db` service
2. Update `.env` to point to your external database

## Troubleshooting

### Container Won't Start

Check the logs:

```bash
docker-compose logs app
```

Common issues:
- Database connection problems
- Port conflicts
- Insufficient memory

### Database Connection Issues

Verify database service is running:

```bash
docker-compose ps db
```

Check database logs:

```bash
docker-compose logs db
```

### Permission Issues

If you encounter permission issues with volumes:

```bash
sudo chown -R $USER:$USER ./reports ./uploads
```

## Security Considerations

For production deployments:

1. **Change default passwords** in `.env` file
2. Consider implementing a reverse proxy (like Nginx or Traefik) with SSL
3. Use Docker secrets for sensitive information rather than environment variables
4. Limit container capabilities using security options in docker-compose.yml
5. Regularly update the base images and dependencies
6. Use a non-root user in the container (already configured)

## Scaling

For high-availability deployments:

1. Use an external PostgreSQL database with replication
2. Deploy multiple app containers behind a load balancer
3. Use Docker Swarm or Kubernetes instead of Docker Compose
4. Consider deploying scanners as separate microservices

## Support

For issues with Docker deployment, please contact support at [support-email].