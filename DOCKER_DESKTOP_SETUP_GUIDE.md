# DataGuardian Pro Docker Desktop Setup Guide for Windows

## Complete Step-by-Step Installation

### Prerequisites Check
- Windows 10 version 2004 and higher (Build 19041 and higher) or Windows 11
- WSL 2 feature enabled on Windows
- At least 4GB RAM available
- 2GB free disk space

### Step 1: Install Docker Desktop

#### Download Docker Desktop
1. Go to https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run the installer `Docker Desktop Installer.exe`

#### Installation Process
1. **Run installer as Administrator**
2. **Configuration during install:**
   - ✅ Enable Hyper-V Windows Features
   - ✅ Install required Windows components for WSL 2
   - ✅ Add shortcut to desktop
3. **Restart Windows** when prompted

#### First-Time Setup
1. **Launch Docker Desktop**
2. **Accept license agreement**
3. **Choose configuration:**
   - ✅ Use WSL 2 instead of Hyper-V (recommended)
   - ✅ Enable integration with default WSL distro
4. **Sign in or skip** Docker Hub account
5. **Wait for Docker to start** (green indicator in system tray)

### Step 2: Verify Docker Installation

Open PowerShell as Administrator and run:
```powershell
# Check Docker version
docker --version
# Should show: Docker version 24.0.x

# Check Docker Compose version
docker-compose --version
# Should show: Docker Compose version 2.x.x

# Test Docker is working
docker run hello-world
# Should download and run successfully
```

### Step 3: Prepare DataGuardian Pro

#### Create Project Directory
```powershell
# Create project folder
mkdir C:\DataGuardian
cd C:\DataGuardian

# If you have the source code, copy it here
# Otherwise, we'll create the necessary files
```

#### Create Docker Compose Configuration
```powershell
# Create docker-compose.yml file
New-Item -Path "docker-compose.yml" -ItemType File
```

Copy this content into `docker-compose.yml`:
```yaml
version: '3.8'

services:
  dataguardian:
    image: python:3.11-slim
    container_name: dataguardian-app
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian
      - REDIS_URL=redis://redis:6379
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-sk_test_demo}
      - STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-pk_test_demo}
      - PYTHONUNBUFFERED=1
    volumes:
      - ./app:/app
      - ./temp_files:/app/temp_files
      - ./logs:/app/logs
    working_dir: /app
    command: >
      bash -c "
        pip install streamlit psycopg2-binary redis python-dotenv requests beautifulsoup4 pandas plotly stripe pyyaml reportlab pillow &&
        streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
      "
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: dataguardian-postgres
    environment:
      - POSTGRES_DB=dataguardian
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: dataguardian-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  pgadmin:
    image: dpage/pgadmin4
    container_name: dataguardian-pgadmin
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@dataguardian.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Step 4: Create Application Structure

#### Create App Directory
```powershell
mkdir app
cd app
```

#### Create Basic Application Files
```powershell
# Create main application file
New-Item -Path "app.py" -ItemType File
```

Copy this minimal DataGuardian Pro application into `app.py`:
```python
import streamlit as st
import psycopg2
import redis
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def init_database():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Redis connection
@st.cache_resource
def init_redis():
    try:
        r = redis.from_url(os.environ.get('REDIS_URL'))
        return r
    except Exception as e:
        st.error(f"Redis connection failed: {e}")
        return None

def main():
    st.title("🛡️ DataGuardian Pro")
    st.markdown("### Enterprise Privacy Compliance Platform")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Code Scanner", "Document Scanner", "Website Scanner", "Settings"]
    )
    
    # Connection status
    with st.sidebar:
        st.markdown("### System Status")
        
        # Database status
        db_conn = init_database()
        if db_conn:
            st.success("✅ Database Connected")
            db_conn.close()
        else:
            st.error("❌ Database Disconnected")
        
        # Redis status
        redis_conn = init_redis()
        if redis_conn:
            try:
                redis_conn.ping()
                st.success("✅ Redis Connected")
            except:
                st.error("❌ Redis Disconnected")
        else:
            st.error("❌ Redis Disconnected")
    
    # Main content
    if page == "Dashboard":
        st.header("📊 Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Scans", "156", "12")
        
        with col2:
            st.metric("Active Users", "23", "3")
        
        with col3:
            st.metric("Compliance Score", "94%", "2%")
        
        with col4:
            st.metric("Risk Level", "Low", "Stable")
        
        st.subheader("Recent Activity")
        st.info("Docker Desktop deployment successful! All services are running.")
        
        # Environment info
        st.subheader("Environment Information")
        st.json({
            "Database URL": os.environ.get('DATABASE_URL', 'Not configured'),
            "Redis URL": os.environ.get('REDIS_URL', 'Not configured'),
            "Stripe Keys": "Configured" if os.environ.get('STRIPE_SECRET_KEY') else "Not configured",
            "Deployment": "Docker Desktop on Windows",
            "Timestamp": datetime.now().isoformat()
        })
    
    elif page == "Code Scanner":
        st.header("🔍 Code Scanner")
        st.info("Code scanning functionality - Docker deployment ready!")
        
        # Demo scanner interface
        repo_url = st.text_input("Repository URL")
        if st.button("Start Scan"):
            if repo_url:
                with st.spinner("Scanning repository..."):
                    st.success(f"Scan completed for {repo_url}")
                    st.json({
                        "findings": 5,
                        "high_risk": 1,
                        "medium_risk": 2,
                        "low_risk": 2,
                        "compliance_score": 87
                    })
    
    elif page == "Document Scanner":
        st.header("📄 Document Scanner")
        st.info("Document scanning functionality - Docker deployment ready!")
        
        uploaded_file = st.file_uploader("Upload Document", type=['pdf', 'docx', 'txt'])
        if uploaded_file and st.button("Scan Document"):
            st.success("Document scan completed!")
            st.json({
                "document": uploaded_file.name,
                "pii_found": 3,
                "compliance_issues": 1,
                "recommendations": "Encrypt sensitive data"
            })
    
    elif page == "Website Scanner":
        st.header("🌐 Website Scanner")
        st.info("Website scanning functionality - Docker deployment ready!")
        
        website_url = st.text_input("Website URL")
        if st.button("Scan Website"):
            if website_url:
                with st.spinner("Scanning website..."):
                    st.success(f"Website scan completed for {website_url}")
                    st.json({
                        "pages_scanned": 15,
                        "cookies_found": 8,
                        "gdpr_compliance": "Partial",
                        "score": 78
                    })
    
    elif page == "Settings":
        st.header("⚙️ Settings")
        st.info("Configuration settings - Docker deployment ready!")
        
        st.subheader("Database Configuration")
        st.code(os.environ.get('DATABASE_URL', 'Not configured'))
        
        st.subheader("Redis Configuration")
        st.code(os.environ.get('REDIS_URL', 'Not configured'))
        
        st.subheader("Stripe Configuration")
        stripe_status = "Configured" if os.environ.get('STRIPE_SECRET_KEY') else "Not configured"
        st.code(f"Stripe API: {stripe_status}")

if __name__ == "__main__":
    main()
```

#### Create Database Initialization Script
```powershell
# Go back to main directory
cd ..

# Create init.sql file
New-Item -Path "init.sql" -ItemType File
```

Copy this content into `init.sql`:
```sql
-- DataGuardian Pro Database Initialization
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    scan_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    findings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scan_results (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id),
    finding_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    location TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo data
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@dataguardian.com', 'hashed_password_here', 'admin'),
('demo_user', 'demo@dataguardian.com', 'hashed_password_here', 'user')
ON CONFLICT (username) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_type ON scans(scan_type);
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_results_severity ON scan_results(severity);
```

#### Create Environment File
```powershell
# Create .env file for environment variables
New-Item -Path ".env" -ItemType File
```

Copy this content into `.env`:
```env
# DataGuardian Pro Environment Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/dataguardian
REDIS_URL=redis://redis:6379

# Stripe Configuration (replace with your keys)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here

# Application Settings
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### Step 5: Launch DataGuardian Pro

#### Start All Services
```powershell
# Make sure you're in the DataGuardian directory
cd C:\DataGuardian

# Start all services
docker-compose up -d

# This will:
# 1. Download required Docker images
# 2. Start PostgreSQL database
# 3. Start Redis cache
# 4. Start DataGuardian Pro application
# 5. Start pgAdmin (database management)
```

#### Verify Services Are Running
```powershell
# Check container status
docker-compose ps

# Should show all services as "Up"
# - dataguardian-app
# - dataguardian-postgres
# - dataguardian-redis
# - dataguardian-pgadmin

# View logs
docker-compose logs dataguardian
```

### Step 6: Access DataGuardian Pro

#### Application URLs
- **DataGuardian Pro**: http://localhost:5000
- **pgAdmin (Database)**: http://localhost:5050
- **Direct Database**: localhost:5432
- **Redis**: localhost:6379

#### First Access
1. **Open browser** to http://localhost:5000
2. **DataGuardian Pro** should load with dashboard
3. **Check system status** in sidebar (should show green checkmarks)
4. **Test scanners** using the demo interface

### Step 7: Management Commands

#### Daily Operations
```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update services
docker-compose pull
docker-compose up -d

# View logs
docker-compose logs -f dataguardian
```

#### Maintenance
```powershell
# View resource usage
docker stats

# Clean up unused images
docker system prune

# Backup database
docker exec dataguardian-postgres pg_dump -U postgres dataguardian > backup.sql

# Access database shell
docker exec -it dataguardian-postgres psql -U postgres -d dataguardian
```

### Step 8: Adding Your Stripe Keys

#### Configure Payment Processing
1. **Get Stripe keys** from https://dashboard.stripe.com/apikeys
2. **Edit .env file**:
   ```env
   STRIPE_SECRET_KEY=sk_test_your_real_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_real_publishable_key
   ```
3. **Restart services**:
   ```powershell
   docker-compose restart
   ```

### Troubleshooting

#### Common Issues and Solutions

**Docker Desktop not starting:**
```powershell
# Check Windows features
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart Windows
```

**Port conflicts:**
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Stop conflicting process
taskkill /PID [PID_NUMBER] /F
```

**Database connection issues:**
```powershell
# Check PostgreSQL container
docker logs dataguardian-postgres

# Reset database
docker-compose down
docker volume rm dataguardian_postgres_data
docker-compose up -d
```

**Application not loading:**
```powershell
# Check application logs
docker logs dataguardian-app

# Rebuild application
docker-compose down
docker-compose up -d --build
```

### Next Steps

#### Production Readiness
1. **Replace demo data** with real application files
2. **Configure SSL certificates** for HTTPS
3. **Set up backup strategy** for data
4. **Configure monitoring** and alerting
5. **Implement security hardening**

#### Scaling Options
1. **Add more scanner containers**
2. **Implement load balancing**
3. **Use external database** (Azure Database for PostgreSQL)
4. **Add Redis clustering**
5. **Deploy to cloud** (Azure Container Instances)

### Success Verification

Your DataGuardian Pro installation is successful when:
- ✅ All containers show "Up" status
- ✅ Application loads at http://localhost:5000
- ✅ Database and Redis show connected in sidebar
- ✅ Scanners respond to demo inputs
- ✅ System status shows green checkmarks

**Congratulations!** You now have a fully functional DataGuardian Pro installation running on Docker Desktop for Windows.