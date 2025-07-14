# Docker Desktop Setup Guide for DataGuardian Pro

## Prerequisites
- Windows 10/11 Pro, Enterprise, or Education (64-bit)
- Docker Desktop for Windows
- WSL 2 (Windows Subsystem for Linux 2)
- 8GB+ RAM recommended

## Installation Steps

### 1. Install Docker Desktop
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the setup wizard
3. Enable WSL 2 integration when prompted
4. Restart your computer

### 2. Configure Docker Desktop
1. Open Docker Desktop
2. Go to Settings → General
3. Ensure "Use WSL 2 based engine" is checked
4. Go to Settings → Resources → WSL Integration
5. Enable integration with your default WSL distro

### 3. Deploy DataGuardian Pro
1. Extract the Docker package to a folder
2. Open PowerShell or Command Prompt as Administrator
3. Navigate to the extracted folder
4. Run: `docker-compose -f docker-compose.windows.yml up -d`
5. Wait for services to start (2-5 minutes)
6. Open browser to http://localhost:5000

### 4. Management Commands
- **Start**: `docker-compose -f docker-compose.windows.yml up -d`
- **Stop**: `docker-compose -f docker-compose.windows.yml down`
- **Restart**: `docker-compose -f docker-compose.windows.yml restart`
- **View logs**: `docker-compose -f docker-compose.windows.yml logs -f`
- **Update**: `docker-compose -f docker-compose.windows.yml pull && docker-compose -f docker-compose.windows.yml up -d`

## Troubleshooting

### Common Issues
- **Docker not starting**: Enable virtualization in BIOS
- **WSL 2 errors**: Run `wsl --update` in PowerShell
- **Port conflicts**: Change port 5000 to another port in docker-compose.yml
- **Performance issues**: Allocate more RAM to Docker in Settings → Resources

### Performance Optimization
- Allocate 4GB+ RAM to Docker Desktop
- Enable file sharing for better performance
- Use SSD storage for Docker data
- Close unnecessary applications

## Data Management
- **Data Location**: Docker volumes store data persistently
- **Backup**: Use `docker-compose exec postgres pg_dump dataguardian > backup.sql`
- **Restore**: Use `docker-compose exec -i postgres psql dataguardian < backup.sql`
- **Reset**: Remove volumes with `docker-compose down -v`