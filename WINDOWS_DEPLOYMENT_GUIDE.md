# DataGuardian Pro Windows Deployment Guide

## Overview
DataGuardian Pro can be deployed on Windows using multiple approaches, from simple local development to enterprise-grade production deployments. This guide covers all Windows deployment options with step-by-step instructions.

## Deployment Options

### 1. Local Development Deployment (Recommended for Testing)

#### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.11 or higher
- Git for Windows
- PostgreSQL 15+ (or Docker Desktop)

#### Step-by-Step Installation

##### Option A: Native Python Installation
```powershell
# Install Python 3.11 from python.org
# Verify installation
python --version

# Clone repository
git clone https://github.com/your-org/dataguardian-pro.git
cd dataguardian-pro

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional Windows-specific dependencies
pip install psycopg2-binary
pip install python-dotenv
```

##### Database Setup
```powershell
# Option 1: Install PostgreSQL natively
# Download from https://www.postgresql.org/download/windows/
# Default installation with user 'postgres'

# Option 2: Use Docker Desktop
docker run --name dataguardian-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dataguardian -p 5432:5432 -d postgres:15

# Create .env file
echo DATABASE_URL=postgresql://postgres:password@localhost:5432/dataguardian > .env
echo STRIPE_SECRET_KEY=your_stripe_key >> .env
echo STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key >> .env
```

##### Run Application
```powershell
# Activate virtual environment
venv\Scripts\activate

# Run DataGuardian Pro
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true

# Application will be available at http://localhost:5000
```

### 2. Docker Desktop Deployment (Recommended for Production-like Testing)

#### Prerequisites
- Docker Desktop for Windows
- Windows 10/11 with WSL2 enabled
- 8GB+ RAM recommended

#### Docker Compose Deployment
```yaml
# docker-compose.windows.yml
version: '3.8'

services:
  dataguardian:
    image: dataguardian/dataguardian-pro:latest
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./temp_files:/app/temp_files
      - ./logs:/app/logs

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=dataguardian
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Build and Run
```powershell
# Clone repository
git clone https://github.com/your-org/dataguardian-pro.git
cd dataguardian-pro

# Create .env file
echo STRIPE_SECRET_KEY=your_stripe_key > .env
echo STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key >> .env

# Build and run
docker-compose -f docker-compose.windows.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs dataguardian
```

### 3. Windows Server Deployment (Enterprise Production)

#### Prerequisites
- Windows Server 2019/2022
- IIS with URL Rewrite Module
- PostgreSQL Server
- SSL Certificate
- Domain name

#### IIS Deployment with Reverse Proxy

##### Step 1: Install IIS and Dependencies
```powershell
# Enable IIS
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpRedirect, IIS-ApplicationDevelopment, IIS-NetFxExtensibility45, IIS-HealthAndDiagnostics, IIS-HttpLogging, IIS-Security, IIS-RequestFiltering, IIS-Performance, IIS-WebServerManagementTools, IIS-ManagementConsole, IIS-IIS6ManagementCompatibility, IIS-Metabase

# Install URL Rewrite Module
# Download from https://www.iis.net/downloads/microsoft/url-rewrite

# Install Python 3.11
# Download from https://www.python.org/downloads/windows/
```

##### Step 2: Application Setup
```powershell
# Create application directory
mkdir C:\inetpub\wwwroot\dataguardian
cd C:\inetpub\wwwroot\dataguardian

# Clone and setup application
git clone https://github.com/your-org/dataguardian-pro.git .
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create startup script
echo @echo off > start_app.bat
echo cd /d C:\inetpub\wwwroot\dataguardian >> start_app.bat
echo call venv\Scripts\activate >> start_app.bat
echo streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true >> start_app.bat
```

##### Step 3: IIS Configuration
```xml
<!-- web.config -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="DataGuardian Pro" stopProcessing="true">
          <match url=".*" />
          <conditions>
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="http://127.0.0.1:8501/{R:0}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

##### Step 4: Windows Service Setup
```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from https://nssm.cc/download

# Create Windows service
nssm install "DataGuardian Pro" "C:\inetpub\wwwroot\dataguardian\start_app.bat"
nssm set "DataGuardian Pro" AppDirectory "C:\inetpub\wwwroot\dataguardian"
nssm set "DataGuardian Pro" DisplayName "DataGuardian Pro Compliance Platform"
nssm set "DataGuardian Pro" Description "Enterprise Privacy Compliance Platform"
nssm set "DataGuardian Pro" Start SERVICE_AUTO_START

# Start service
nssm start "DataGuardian Pro"
```

### 4. Azure Windows VM Deployment

#### Prerequisites
- Azure subscription
- Windows Server 2022 VM
- Azure Database for PostgreSQL
- Azure Redis Cache
- Application Gateway with SSL

#### Azure Resource Template
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "vmName": {
      "type": "string",
      "defaultValue": "dataguardian-vm"
    },
    "adminUsername": {
      "type": "string",
      "defaultValue": "azureuser"
    },
    "adminPassword": {
      "type": "securestring"
    }
  },
  "resources": [
    {
      "type": "Microsoft.Compute/virtualMachines",
      "apiVersion": "2021-07-01",
      "name": "[parameters('vmName')]",
      "location": "[resourceGroup().location]",
      "properties": {
        "hardwareProfile": {
          "vmSize": "Standard_D4s_v4"
        },
        "osProfile": {
          "computerName": "[parameters('vmName')]",
          "adminUsername": "[parameters('adminUsername')]",
          "adminPassword": "[parameters('adminPassword')]"
        },
        "storageProfile": {
          "imageReference": {
            "publisher": "MicrosoftWindowsServer",
            "offer": "WindowsServer",
            "sku": "2022-datacenter",
            "version": "latest"
          },
          "osDisk": {
            "createOption": "FromImage",
            "managedDisk": {
              "storageAccountType": "Premium_LRS"
            }
          }
        },
        "networkProfile": {
          "networkInterfaces": [
            {
              "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('vmName'), '-nic'))]"
            }
          ]
        }
      }
    }
  ]
}
```

#### Azure Deployment Script
```powershell
# Deploy to Azure
az group create --name dataguardian-rg --location "West Europe"

# Deploy VM
az deployment group create \
  --resource-group dataguardian-rg \
  --template-file azure-template.json \
  --parameters vmName=dataguardian-vm adminUsername=azureuser adminPassword='YourSecurePassword123!'

# Create PostgreSQL database
az postgres flexible-server create \
  --resource-group dataguardian-rg \
  --name dataguardian-postgres \
  --location "West Europe" \
  --admin-user dbadmin \
  --admin-password 'YourDbPassword123!' \
  --sku-name Standard_D2s_v3 \
  --storage-size 128 \
  --version 15

# Create Redis cache
az redis create \
  --resource-group dataguardian-rg \
  --name dataguardian-redis \
  --location "West Europe" \
  --sku Standard \
  --vm-size C1
```

### 5. AWS EC2 Windows Deployment

#### Prerequisites
- AWS account with EC2 access
- Windows Server 2022 AMI
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- Application Load Balancer

#### EC2 User Data Script
```powershell
<powershell>
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install required software
choco install -y python --version=3.11.0
choco install -y git
choco install -y postgresql15

# Create application directory
mkdir C:\dataguardian
cd C:\dataguardian

# Clone repository
git clone https://github.com/your-org/dataguardian-pro.git .

# Install Python dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create environment configuration
$env:DATABASE_URL = "postgresql://dbuser:dbpass@your-rds-endpoint:5432/dataguardian"
$env:REDIS_URL = "redis://your-elasticache-endpoint:6379"
$env:STRIPE_SECRET_KEY = "your-stripe-secret"

# Create startup script
@"
@echo off
cd /d C:\dataguardian
call venv\Scripts\activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
"@ | Out-File -FilePath "C:\dataguardian\start.bat" -Encoding ASCII

# Install as Windows service
# Download and install NSSM
Invoke-WebRequest -Uri "https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip" -OutFile "nssm.zip"
Expand-Archive -Path "nssm.zip" -DestinationPath "C:\nssm"
$env:PATH += ";C:\nssm\nssm-2.24-101-g897c7ad\win64"

# Create and start service
nssm install "DataGuardian Pro" "C:\dataguardian\start.bat"
nssm set "DataGuardian Pro" AppDirectory "C:\dataguardian"
nssm start "DataGuardian Pro"

# Configure Windows Firewall
New-NetFirewallRule -DisplayName "DataGuardian Pro" -Direction Inbound -Protocol TCP -LocalPort 8501 -Action Allow
</powershell>
```

## Security Considerations

### SSL/TLS Configuration
```powershell
# Generate self-signed certificate for testing
$cert = New-SelfSignedCertificate -DnsName "dataguardian.local" -CertStoreLocation "cert:\LocalMachine\My"
$thumb = $cert.Thumbprint

# Bind certificate to IIS
netsh http add sslcert ipport=0.0.0.0:443 certhash=$thumb appid="{00000000-0000-0000-0000-000000000000}"
```

### Windows Firewall Rules
```powershell
# Allow HTTP/HTTPS traffic
New-NetFirewallRule -DisplayName "DataGuardian HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "DataGuardian HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "DataGuardian Streamlit" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## Performance Optimization

### Windows-Specific Optimizations
```powershell
# Increase virtual memory
$cs = Get-WmiObject -Class Win32_ComputerSystem
$cs.AutomaticManagedPagefile = $false
$cs.Put()

# Set custom page file size
$pf = Get-WmiObject -Class Win32_PageFileSetting
$pf.InitialSize = 4096
$pf.MaximumSize = 8192
$pf.Put()

# Optimize for background services
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" -Name "Win32PrioritySeparation" -Value 24
```

### Resource Monitoring
```powershell
# Monitor system resources
Get-Counter -Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 10
Get-Counter -Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 10
Get-Counter -Counter "\Network Interface(*)\Bytes Total/sec" -SampleInterval 1 -MaxSamples 10
```

## Backup and Recovery

### Database Backup
```powershell
# PostgreSQL backup script
$backupPath = "C:\Backups\dataguardian_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".sql"
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -h localhost -U postgres -d dataguardian -f $backupPath
```

### Application Backup
```powershell
# Backup application and configuration
$backupDir = "C:\Backups\dataguardian_app_" + (Get-Date -Format "yyyyMMdd_HHmmss")
Copy-Item -Path "C:\inetpub\wwwroot\dataguardian" -Destination $backupDir -Recurse
```

## Monitoring and Logging

### Windows Event Log Integration
```python
# Add to app.py for Windows Event Log integration
import logging
import logging.handlers

# Configure Windows Event Log
logger = logging.getLogger('DataGuardian')
handler = logging.handlers.NTEventLogHandler('DataGuardian Pro')
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Performance Counters
```powershell
# Create custom performance counters
$counterCategory = "DataGuardian Pro"
$counters = @(
    "Scans Per Second",
    "Active Users",
    "Database Connections",
    "Memory Usage MB"
)

# Create performance counter category
New-PerformanceCounterCategory -CategoryName $counterCategory -CategoryType MultiInstance -Counters $counters
```

## Troubleshooting

### Common Issues and Solutions

#### Port Conflicts
```powershell
# Check port usage
netstat -ano | findstr :5000
netstat -ano | findstr :8501

# Kill process using port
taskkill /PID [PID_NUMBER] /F
```

#### Python Path Issues
```powershell
# Fix Python path
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311"
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\Scripts"
```

#### PostgreSQL Connection Issues
```powershell
# Test PostgreSQL connection
psql -h localhost -U postgres -d dataguardian -c "SELECT version();"

# Check PostgreSQL service
Get-Service -Name "postgresql*"
Start-Service -Name "postgresql-x64-15"
```

## Deployment Summary

### Recommended Deployment Path
1. **Development**: Local Python installation with PostgreSQL
2. **Testing**: Docker Desktop with Docker Compose
3. **Production**: Windows Server with IIS reverse proxy
4. **Enterprise**: Azure/AWS cloud deployment with managed services

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 50GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 100GB SSD
- **Enterprise**: 16GB RAM, 8 CPU cores, 200GB SSD

### Security Best Practices
- Use HTTPS with valid SSL certificates
- Implement proper firewall rules
- Regular security updates
- Database encryption at rest
- Secure API key management
- Regular backup and disaster recovery testing

This comprehensive Windows deployment guide provides multiple deployment options suitable for different use cases, from development to enterprise production environments.