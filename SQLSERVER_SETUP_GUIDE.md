# SQL SERVER SETUP GUIDE
## Testing DataGuardian Pro Patent #2 with Microsoft SQL Server

## 🎯 Overview
This guide helps you set up a **FREE** SQL Server database to test DataGuardian Pro's multi-database scanning capabilities.

---

## 🆓 OPTION 1: Azure SQL Database (FREE TIER) - **RECOMMENDED**

### Benefits
- ✅ **100% FREE** (32 GB storage, 100K vCore seconds/month)
- ✅ Full Microsoft SQL Server compatibility
- ✅ Cloud-hosted, no local installation
- ✅ Automated backups, patching, monitoring
- ✅ Production-grade infrastructure

### Setup Steps

#### 1. Create Azure Account (Free)
```bash
# Go to: https://azure.microsoft.com/free/
# Sign up with email (no credit card required for free tier)
```

#### 2. Create Azure SQL Database
```bash
# Login to Azure Portal: https://portal.azure.com

# Create Resource > Databases > SQL Database

# Configuration:
Subscription: Free Trial
Resource Group: Create new "dataguardian-test"
Database Name: testdb
Server: Create new
  - Server name: dataguardian-sqlserver (must be globally unique)
  - Location: West Europe (Netherlands region)
  - Authentication: SQL authentication
  - Login: sqladmin
  - Password: YourSecurePassword123!

Compute + Storage: 
  - Select "Configure database"
  - Choose "Serverless" (FREE TIER)
  - Max vCores: 1
  - Storage: 32 GB (free limit)

Networking:
  - Public endpoint: YES
  - Allow Azure services: YES
  - Add current IP: YES

# Click "Review + Create" → "Create"
```

#### 3. Configure Firewall
```bash
# In Azure Portal:
# Go to SQL Database → Networking → Firewall rules
# Add rule: "Replit" → IP: 0.0.0.0-255.255.255.255 (allow all for testing)
# Production: Use specific IP ranges
```

#### 4. Get Connection String
```bash
# In Azure Portal:
# SQL Database → Connection strings → ADO.NET

# Example format:
Server=dataguardian-sqlserver.database.windows.net,1433;
Database=testdb;
User ID=sqladmin;
Password=YourSecurePassword123!;
Encrypt=yes;
TrustServerCertificate=no;
```

#### 5. Test Connection
```bash
# Set environment variables
export SQLSERVER_HOST="dataguardian-sqlserver.database.windows.net"
export SQLSERVER_PORT="1433"
export SQLSERVER_USER="sqladmin"
export SQLSERVER_PASSWORD="YourSecurePassword123!"
export SQLSERVER_DATABASE="testdb"

# Run test
python test_sqlserver_netherlands_pii.py
```

---

## 🖥️ OPTION 2: SQL Server Express (LOCAL) - **ADVANCED**

### Benefits
- ✅ Free (10 GB database limit)
- ✅ Full SQL Server features
- ⚠️ Requires local installation

### Setup Steps

#### 1. Download SQL Server Express
```bash
# Windows/Linux/macOS:
# https://www.microsoft.com/en-us/sql-server/sql-server-downloads

# Select: Express edition (FREE)
```

#### 2. Install SQL Server
```bash
# Windows:
# Run installer → Basic installation → Accept defaults

# Linux (Ubuntu/Debian):
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/20.04/mssql-server-2022.list)"
sudo apt-get update
sudo apt-get install -y mssql-server
sudo /opt/mssql/bin/mssql-conf setup

# macOS:
# Use Docker: docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123!" \
#   -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
```

#### 3. Configure Connection
```bash
export SQLSERVER_HOST="localhost"
export SQLSERVER_PORT="1433"
export SQLSERVER_USER="sa"
export SQLSERVER_PASSWORD="YourPassword123!"
export SQLSERVER_DATABASE="master"

# Run test
python test_sqlserver_netherlands_pii.py
```

---

## 🔧 OPTION 3: Cloud Clusters (7-DAY FREE TRIAL)

### Benefits
- ✅ 7 days FREE (no credit card)
- ✅ SQL Server 2022
- ✅ Quick setup

### Setup Steps
```bash
# 1. Go to: https://www.msclusters.com/
# 2. Sign up for 7-day free trial
# 3. Deploy SQL Server 2022 instance
# 4. Get connection credentials
# 5. Run test with provided credentials
```

---

## 📦 Prerequisites

### Install ODBC Driver (REQUIRED)

#### Windows
```bash
# Download from Microsoft:
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Install: ODBC Driver 17 or 18 for SQL Server
```

#### Linux (Ubuntu/Debian)
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Verify installation
odbcinst -q -d -n "ODBC Driver 17 for SQL Server"
```

#### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17
```

### Install Python Package
```bash
pip install pyodbc
```

---

## 🧪 Running the Test

```bash
# Set credentials (Azure example)
export SQLSERVER_HOST="dataguardian-sqlserver.database.windows.net"
export SQLSERVER_PORT="1433"
export SQLSERVER_USER="sqladmin"
export SQLSERVER_PASSWORD="YourSecurePassword123!"
export SQLSERVER_DATABASE="testdb"

# Run Netherlands PII test
python test_sqlserver_netherlands_pii.py

# Expected output:
# ✅ Created netherlands_pii_test table with 12 records
# ✅ Connected successfully
# 📊 Total findings: 30+ PII instances
# ✅ All validation checks passed!
```

---

## 🎯 Test Coverage

The test validates:

| PII Type | Count | Description |
|----------|-------|-------------|
| **BSN** | 12 | Netherlands social security numbers (11-proef validation) |
| **Email** | 12 | .nl domain emails |
| **Phone** | 12 | +31 and 06 format numbers |
| **Postcode** | 12 | Dutch postcode format (#### XX) |
| **IBAN** | 12 | Dutch bank account numbers (NL##) |
| **Name** | 12 | Personal identifiers |
| **Address** | 12 | Location data |

**Total Expected Findings:** 30-84 PII instances

---

## 📊 Performance Benchmarks

Expected performance (3 scan modes):

| Mode | Duration | Findings | Notes |
|------|----------|----------|-------|
| FAST | 2-5s | 30-50 | Quick column-based scan |
| SMART | 3-8s | 50-70 | Intelligent sampling |
| DEEP | 4-10s | 70-84 | Full table scan |

---

## 🔍 Troubleshooting

### Error: "ODBC Driver not found"
```bash
# Install ODBC Driver (see Prerequisites above)
# Verify: odbcinst -q -d
```

### Error: "Login failed for user"
```bash
# Check credentials in Azure Portal
# Verify firewall allows your IP
```

### Error: "SSL Provider: Certificate chain not trusted"
```bash
# Azure requires TLS 1.2+
# Add to connection string: TrustServerCertificate=yes (testing only!)
```

### Error: "Timeout expired"
```bash
# Increase connection timeout
# Check network/firewall settings
```

---

## 💰 Cost Breakdown

| Option | Cost | Storage | Duration |
|--------|------|---------|----------|
| **Azure Free Tier** | €0 | 32 GB | 12 months + forever free tier |
| **SQL Express** | €0 | 10 GB | Forever |
| **Cloud Clusters** | €0 | Varies | 7 days free trial |

**Recommendation:** Use **Azure SQL Database FREE tier** for best testing experience.

---

## 🚀 Next Steps

After successful testing:

1. ✅ **Verify 3-database support** (PostgreSQL, MySQL, SQL Server)
2. ✅ **Document performance metrics** for patent filing
3. ✅ **Update Patent #2 claims** with SQL Server validation
4. ✅ **Test additional enterprise features** (Azure AD auth, encryption)

---

## 📞 Support Resources

- **Azure SQL Documentation:** https://learn.microsoft.com/azure/sql-database/
- **ODBC Driver Docs:** https://learn.microsoft.com/sql/connect/odbc/
- **SQL Server Express:** https://www.microsoft.com/sql-server/sql-server-downloads
- **DataGuardian Support:** Check replit.md for project details

---

**Ready to test? Run:**
```bash
python test_sqlserver_netherlands_pii.py
```
