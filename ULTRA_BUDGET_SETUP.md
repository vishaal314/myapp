# Ultra Budget Netherlands Hosting: €2.50-5/month
## Complete Setup Guide for Cheapest Options

Here are the absolute cheapest ways to host DataGuardian Pro in the Netherlands while maintaining GDPR compliance:

## 🥇 **Cheapest: INIZ.com (€2.50/month)**

**Perfect for:** Small-scale testing and personal use
**Specs:** 1 vCPU, 1GB RAM, 20GB SSD
**Location:** Netherlands datacenters
**Company:** Dutch company

### Complete INIZ Setup:

1. **Order VPS**
   - Go to [iniz.com](https://iniz.com)
   - Select "VPS Basic" (€2.50/month)
   - Choose Netherlands location
   - OS: Ubuntu 22.04

2. **Lightweight Configuration**
   ```bash
   # SSH to your VPS
   ssh root@your-iniz-ip
   
   # Install minimal Docker
   apt update
   apt install docker.io postgresql-client -y
   
   # Create lightweight database
   docker run -d --name postgres \
     -e POSTGRES_PASSWORD=secure123 \
     -e POSTGRES_USER=dpia \
     -e POSTGRES_DB=dataguardian \
     -p 5432:5432 \
     --restart unless-stopped \
     postgres:15-alpine
   ```

3. **Memory-Optimized Deployment**
   ```bash
   # Clone your app
   git clone https://github.com/YOUR_USERNAME/dataguardian-pro.git
   cd dataguardian-pro
   
   # Create minimal environment
   cat > .env << EOF
   DATABASE_URL=postgresql://dpia:secure123@localhost:5432/dataguardian
   PGHOST=localhost
   PGUSER=dpia
   PGPASSWORD=secure123
   PGDATABASE=dataguardian
   PGPORT=5432
   PORT=5000
   EOF
   
   # Build lightweight image
   docker build -t dataguardian-lite .
   docker run -d --name app \
     --env-file .env \
     --network host \
     --memory=800m \
     --restart unless-stopped \
     dataguardian-lite
   ```

## 🥈 **Best Value: Time4VPS (€2.99/month)**

**Perfect for:** Production use with good performance
**Specs:** 1 vCPU, 2GB RAM, 20GB SSD
**Location:** Amsterdam
**Benefits:** Double the RAM for small price increase

### Time4VPS Setup:

1. **Order VPS**
   - Go to [time4vps.com](https://time4vps.com)
   - Select "Linux 2" plan (€2.99/month)
   - Location: Amsterdam
   - OS: Ubuntu 22.04

2. **Full Docker Compose Setup**
   ```bash
   # Install Docker Compose
   apt update
   apt install docker-compose -y
   
   # Use your existing docker-compose.yml
   docker-compose up -d
   ```

## 🥉 **Alternative: VPS.nl (€2.99/month)**

**Perfect for:** True Dutch hosting
**Specs:** 1 vCPU, 1GB RAM, 25GB SSD
**Location:** Netherlands only
**Benefits:** 100% Dutch company

### VPS.nl Quick Setup:

```bash
# Order at vps.nl
# SSH and install
apt update && apt install docker.io -y

# Single container with database
docker run -d --name dataguardian-all \
  -e DATABASE_URL=sqlite:///app/data.db \
  -p 5000:5000 \
  --restart unless-stopped \
  your-app-image
```

## 💾 **SQLite Option for Ultra Budget**

For the absolute cheapest hosting, use SQLite instead of PostgreSQL:

### Modified app.py for SQLite:
```python
# Add to your app.py
import sqlite3
import os

def init_sqlite_db():
    """Initialize SQLite database for budget hosting"""
    db_path = os.path.join(os.getcwd(), 'data', 'dataguardian.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Create tables (convert from PostgreSQL schema)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            region TEXT NOT NULL,
            file_count INTEGER NOT NULL,
            total_pii_found INTEGER NOT NULL,
            high_risk_count INTEGER NOT NULL,
            result_json TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Call during app startup
if __name__ == "__main__":
    init_sqlite_db()
```

### Environment for SQLite:
```bash
# Ultra minimal environment
DATABASE_URL=sqlite:///app/data/dataguardian.db
PORT=5000
PYTHONUNBUFFERED=1
DATA_RESIDENCY=Netherlands
ULTRA_BUDGET_MODE=true
```

## 🔧 **Memory Optimization for 1GB RAM**

### Streamlit Configuration:
```toml
# .streamlit/config.toml for low memory
[server]
headless = true
address = "0.0.0.0"
port = 5000
maxUploadSize = 10
maxMessageSize = 10

[global]
developmentMode = false
```

### Python Memory Optimization:
```python
# Add to your app.py
import gc
import streamlit as st

# Memory management
def cleanup_memory():
    gc.collect()
    
# Run cleanup after heavy operations
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_scan_data():
    # Your data loading logic
    cleanup_memory()
    return data
```

## 📊 **Ultra Budget Cost Breakdown**

| Provider | Monthly | Annual | Setup | Domain | Total Year |
|----------|---------|--------|--------|--------|------------|
| INIZ.com | €2.50 | €30 | €0 | €12 | €42 |
| Time4VPS | €2.99 | €36 | €0 | €12 | €48 |
| VPS.nl | €2.99 | €36 | €0 | €12 | €48 |
| HostHatch | €3.20 | €38 | €0 | €12 | €50 |

## ⚠️ **Budget Limitations**

**What you get:**
- ✅ Netherlands/EU hosting
- ✅ GDPR compliance
- ✅ Basic performance
- ✅ SSL certificates
- ✅ Docker support

**What you sacrifice:**
- ❌ Limited concurrent users (5-10)
- ❌ No managed backups
- ❌ Basic support only
- ❌ Manual scaling required
- ❌ No high availability

## 🎯 **Recommended Ultra Budget Path**

1. **Start with Time4VPS (€2.99/month)**
   - Best specs for the price
   - Amsterdam location
   - 2GB RAM allows PostgreSQL

2. **Use SQLite initially**
   - No separate database costs
   - Easier to manage
   - Sufficient for small scale

3. **Upgrade path ready**
   - Switch to PostgreSQL when needed
   - Easy migration to larger VPS
   - Keep same provider

**Total first year cost: €48 including domain**

This gives you a functional DataGuardian Pro deployment in the Netherlands for under €50 per year, perfect for testing, small businesses, or personal use while maintaining full GDPR compliance.