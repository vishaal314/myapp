# SQL Server Database Scanner Testing Guide

## ⚠️ Docker Not Available in Replit

Docker isn't available in this Replit environment. Here are **2 options** to test SQL Server:

---

## **Option 1: Azure SQL Database (FREE - Recommended)**

### **Setup Time:** 10 minutes  
### **Cost:** €0 (12 months free)

### **Step 1: Create Azure Account**
1. Go to: https://azure.microsoft.com/free/
2. Click "Start free"
3. Sign up (requires credit card but won't charge)

### **Step 2: Create SQL Database**
1. Go to Azure Portal: https://portal.azure.com
2. Click "+ Create a resource" → Search "SQL Database" → Create
3. Fill in:
   ```
   Resource Group: Create new → "DataGuardianTest"
   Database name: ComplianceTest
   Server: Create new
     Server name: dataguardian-test (must be unique)
     Location: West Europe
     Admin login: sqladmin
     Password: DataGuard!2024Azure
   Compute + storage: Basic (free tier)
   ```
4. **Networking tab:**
   - Connectivity: Public endpoint
   - ✅ Allow Azure services
   - ✅ Add current client IP
5. Click "Review + create" → Create (wait 5 min)

### **Step 3: Get Connection String**
After deployment:
```
Server: dataguardian-test.database.windows.net
Database: ComplianceTest
Username: sqladmin
Password: DataGuard!2024Azure
```

### **Step 4: Run Setup Script**
```bash
# Install driver
pip install pyodbc

# Run setup (creates tables with Dutch PII)
python setup_azure_sqlserver_test.py

# Run tests
python test_azure_sqlserver_scanner.py
```

---

## **Option 2: Local Machine with Docker**

If you have Docker on your **local machine** (not Replit), run these commands:

### **Quick Setup (2 minutes)**
```bash
# 1. Start SQL Server
docker run -d \
  --name sqlserver-test \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=DataGuard!2024" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

# 2. Wait 30 seconds
sleep 30

# 3. Create test data
python setup_local_sqlserver_test.py

# 4. Run tests
python test_sqlserver_scanner.py
```

### **Cleanup**
```bash
docker stop sqlserver-test
docker rm sqlserver-test
```

---

## **Scripts Provided**

I've created these scripts for you:
1. `setup_azure_sqlserver_test.py` - Azure SQL Database setup
2. `test_sqlserver_scanner.py` - Complete scanner tests
3. `setup_local_sqlserver_test.py` - Local Docker setup

---

## **Recommendation**

✅ **Use Azure SQL Database (Option 1)**
- No Docker required
- Works from Replit
- Free for 12 months
- 10-minute setup

Run this next:
```bash
pip install pyodbc
python setup_azure_sqlserver_test.py
```
