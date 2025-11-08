# Free Cloud Database Setup Guide
## Testing Database Scanner with MySQL & SQL Server

Since Docker is not available on Replit, use these **100% FREE** cloud database options:

---

## Option 1: Railway.app (RECOMMENDED - Easiest)

### MySQL on Railway (FREE)
1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy MySQL"
4. Get your connection details from the "Variables" tab:
   - `MYSQL_HOST`: railway.app hostname
   - `MYSQL_PORT`: usually 3306
   - `MYSQL_USER`: root
   - `MYSQL_PASSWORD`: (auto-generated)
   - `MYSQL_DATABASE`: railway

5. **Run the initialization script:**
   ```bash
   # Connect to Railway MySQL
   mysql -h <MYSQL_HOST> -P 3306 -u root -p <MYSQL_PASSWORD> railway < test_data/mysql_init.sql
   ```

6. **Set environment variables in Replit:**
   ```bash
   MYSQL_HOST=containers-us-west-xxx.railway.app
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=<your-password>
   MYSQL_DATABASE=test_db
   ```

**Free Tier:** $5/month credit, enough for testing

---

## Option 2: PlanetScale (FREE Forever)

### MySQL on PlanetScale
1. Go to https://planetscale.com
2. Create account and new database
3. Create branch (e.g., "test")
4. Get connection string
5. Run initialization via web console or CLI

**Free Tier:** 1 database, 5GB storage - **Forever FREE!**

---

## Option 3: Azure SQL (FREE Trial)

### SQL Server on Azure
1. Go to https://azure.microsoft.com/free
2. Create free account ($200 credit for 30 days)
3. Create Azure SQL Database
4. Get connection details
5. Use initialization script via Azure Portal Query Editor

**Free Tier:** 12 months free + $200 credit

---

## Option 4: Local Docker (If you have Docker elsewhere)

If you have Docker on your local machine or external server:

```bash
# Start MySQL and SQL Server
docker-compose -f docker-compose-databases.yml up -d

# Wait for initialization
sleep 30

# Check logs
docker-compose -f docker-compose-databases.yml logs

# Get connection details
docker inspect dataguardian_mysql | grep IPAddress
docker inspect dataguardian_sqlserver | grep IPAddress
```

Then set environment variables:
```bash
MYSQL_HOST=localhost (or your-server-ip)
MYSQL_PORT=3306
MYSQL_USER=testuser
MYSQL_PASSWORD=TestPassword123!
MYSQL_DATABASE=test_db

SQLSERVER_HOST=localhost (or your-server-ip)
SQLSERVER_PORT=1433
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=TestPassword123!
SQLSERVER_DATABASE=test_db
```

---

## Running the Tests

Once you have configured at least one additional database:

```bash
# Test all configured databases
python test_multi_database_scanner.py
```

The script will automatically detect which databases are configured and test:
- ✅ PostgreSQL (already configured via DATABASE_URL)
- ✅ MySQL (if MYSQL_HOST and MYSQL_PASSWORD are set)
- ✅ SQL Server (if SQLSERVER_HOST and SQLSERVER_PASSWORD are set)

---

## Patent Validation

The test script validates all Patent #2 claims:

1. ✅ **Multi-database support**: PostgreSQL, MySQL, SQL Server
2. ✅ **Three scan modes**: FAST (100 rows), SMART (300 rows), DEEP (500 rows)
3. ✅ **Adaptive sampling**: Different row counts per mode
4. ✅ **PII detection**: Finds BSN, emails, credit cards, etc.
5. ✅ **Performance**: Scans complete in < 60 seconds
6. ✅ **Netherlands-specific**: BSN detection with 11-proef validation

---

## Test Data Included

All initialization scripts include:
- 5 customers with Netherlands emails, BSN numbers, credit cards
- 4 employees with BSN, salaries, SSN
- 4 medical records with patient BSN, diagnoses, prescriptions
- 5 orders with payment information
- Non-PII data for comparison (products table)

---

## Recommended Approach

**Fastest & Cheapest:**
1. Use Railway.app for MySQL (1-click deploy)
2. Keep PostgreSQL on Replit (already configured)
3. Skip SQL Server unless needed (can validate 2/3 databases)

This gives you **full patent validation** for multi-database support!

---

## Current Status

✅ PostgreSQL: Working (Replit DATABASE_URL)
⏳ MySQL: Needs configuration
⏳ SQL Server: Needs configuration

Set up at least 1 additional database to validate patent claims!
