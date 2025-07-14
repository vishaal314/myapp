# Ultra Budget Windows Setup - DataGuardian Pro

## Free & Ultra-Budget Windows Deployment Options

### Option 1: Python + Local SQLite (€0 - Completely Free)
**Best for**: Personal use, small businesses, testing

**Requirements**:
- Windows 10/11 (any edition)
- Python 3.11 (free from python.org)
- No additional software needed

**Installation Steps**:
```batch
# 1. Download Python 3.11 from python.org (free)
# 2. Clone or download DataGuardian Pro
git clone https://github.com/yourusername/dataguardian-pro.git
cd dataguardian-pro

# 3. Install dependencies
pip install -e .

# 4. Run with SQLite (no PostgreSQL needed)
set DATABASE_URL=sqlite:///dataguardian.db
streamlit run app.py --server.port 5000
```

**Performance**: Good for 1-5 users, basic scanning

---

### Option 2: Portable USB Version (€0 - Completely Portable)
**Best for**: Consultants, auditors, temporary assessments

**Setup**:
1. Download Python 3.11 Portable from [python.org](https://www.python.org/downloads/windows/)
2. Extract to USB drive (e.g., `D:\DataGuardian-Pro\`)
3. Create portable launcher:

```batch
# portable_launcher.bat
@echo off
set PYTHONPATH=%~dp0python
set PATH=%~dp0python;%~dp0python\Scripts;%PATH%
cd /d %~dp0
echo Starting DataGuardian Pro (Portable)...
python -m streamlit run app.py --server.port 5000
```

**Advantages**: No installation required, works on any Windows PC

---

### Option 3: Windows Subsystem for Linux (WSL) - €0
**Best for**: Developers, better performance than pure Windows

**Setup**:
```batch
# Enable WSL
wsl --install

# Install Ubuntu (free)
wsl --install -d Ubuntu

# Inside WSL
sudo apt update && sudo apt install python3 python3-pip
git clone https://github.com/yourusername/dataguardian-pro.git
cd dataguardian-pro
pip3 install -e .
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

**Access**: Open browser to http://localhost:5000

---

### Option 4: Free Cloud Hosting (€0 - Cloud Deployment)
**Best for**: Small teams, remote access

**Options**:
1. **GitHub Codespaces** (60 hours/month free)
2. **Gitpod** (50 hours/month free)
3. **Replit** (Free tier available)

**Setup for Replit**:
1. Fork DataGuardian Pro to GitHub
2. Import to Replit
3. Run: `streamlit run app.py --server.port 5000`
4. Access via provided URL

---

### Option 5: Home Server Setup (€50-100 one-time)
**Best for**: Small businesses, permanent installation

**Hardware**: Raspberry Pi 4 (8GB) or old PC
**Software**: Ubuntu Server (free)

**Setup**:
```bash
# Install Ubuntu Server
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git postgresql nginx -y

# Setup DataGuardian Pro
git clone https://github.com/yourusername/dataguardian-pro.git
cd dataguardian-pro
pip3 install -e .

# Setup PostgreSQL
sudo -u postgres createdb dataguardian
sudo -u postgres createuser dataguardian -P

# Run as service
sudo systemctl enable dataguardian
sudo systemctl start dataguardian
```

**Access**: Local network IP:5000 or configure domain

---

### Option 6: Windows Task Scheduler Auto-Start (€0)
**Best for**: Automatic startup, service-like behavior

**Setup**:
1. Create batch file: `auto_start_dataguardian.bat`
```batch
@echo off
cd /d "C:\DataGuardian-Pro"
python -m streamlit run app.py --server.port 5000 --server.headless true
```

2. Open Task Scheduler
3. Create Basic Task → "DataGuardian Pro Auto Start"
4. Trigger: "When computer starts"
5. Action: Start program → `auto_start_dataguardian.bat`

**Result**: DataGuardian Pro starts automatically with Windows

---

### Option 7: Virtual Machine Setup (€0 with free VM)
**Best for**: Isolated environment, testing

**Requirements**:
- VirtualBox (free)
- Ubuntu ISO (free)
- 4GB RAM allocated

**Setup**:
1. Create Ubuntu VM in VirtualBox
2. Install DataGuardian Pro in VM
3. Configure port forwarding (5000 → 5000)
4. Take snapshot for easy reset

**Access**: http://localhost:5000 from host machine

---

### Option 8: Android/Mobile Access (€0)
**Best for**: Mobile compliance checks, field audits

**Setup**:
1. Install Termux on Android (free)
2. In Termux:
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/yourusername/dataguardian-pro.git
cd dataguardian-pro
pip install -e .
streamlit run app.py --server.port 8501
```

**Access**: Browser to http://localhost:8501

---

## Feature Comparison by Budget Option

| Feature | SQLite | Portable | WSL | Cloud | Home Server | VM |
|---------|--------|----------|-----|-------|-------------|-----|
| **Cost** | €0 | €0 | €0 | €0 | €50-100 | €0 |
| **Users** | 1-5 | 1-3 | 1-10 | 1-50 | 1-100 | 1-10 |
| **Performance** | Good | Basic | Great | Good | Excellent | Good |
| **Portability** | Medium | High | Low | High | Low | Medium |
| **Reliability** | Good | Basic | Great | Good | Excellent | Good |
| **Scalability** | Low | Low | Medium | High | High | Low |

---

## Recommended Setup by Use Case

### Personal Use (1 user)
**Best Option**: SQLite + Portable USB
- Zero cost
- No installation required
- Easy to use anywhere

### Small Business (2-10 users)
**Best Option**: WSL + PostgreSQL
- Free and reliable
- Good performance
- Professional features

### Consultant/Auditor
**Best Option**: Portable USB + Cloud backup
- Works on any client computer
- No installation permissions needed
- Professional appearance

### Growing Business (10-50 users)
**Best Option**: Home Server + Domain
- One-time cost
- Scalable solution
- Full control

### Remote Team
**Best Option**: Cloud hosting
- Accessible anywhere
- No maintenance required
- Pay-as-you-grow

---

## Quick Start Commands

### Windows SQLite (Fastest Start)
```batch
# Download from GitHub
# Extract to folder
cd dataguardian-pro
pip install -e .
set DATABASE_URL=sqlite:///dataguardian.db
streamlit run app.py --server.port 5000
```

### Windows + PostgreSQL (Production Ready)
```batch
# Install PostgreSQL from postgresql.org
# Create database
psql -U postgres -c "CREATE DATABASE dataguardian;"
# Set connection
set DATABASE_URL=postgresql://postgres:password@localhost/dataguardian
streamlit run app.py --server.port 5000
```

### Linux/WSL (Best Performance)
```bash
sudo apt install postgresql python3-pip
sudo -u postgres createdb dataguardian
pip3 install -e .
export DATABASE_URL=postgresql://postgres:password@localhost/dataguardian
streamlit run app.py --server.port 5000
```

---

## Troubleshooting Ultra-Budget Setup

### Common Issues
1. **"Python not found"** → Add Python to PATH during installation
2. **"pip not found"** → Install Python with "Add to PATH" checked
3. **Database errors** → Use SQLite for simplest setup
4. **Port 5000 busy** → Change to `--server.port 8501`
5. **Permission errors** → Run as administrator or use different folder

### Performance Tips
- Use SSD storage for better performance
- Close unnecessary programs
- Allocate 4GB+ RAM if possible
- Use Chrome/Edge for best web interface experience

### Memory-Optimized Settings
```python
# Add to .env file for low-memory systems
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=50
```

---

## Support for Budget Users

### Free Resources
- GitHub Issues for bug reports
- Community Discord for help
- YouTube tutorials for setup
- Documentation wiki

### Cost-Saving Tips
- Use SQLite instead of PostgreSQL
- Disable Redis caching for lower memory usage
- Run only needed scanners
- Use batch processing for large scans

### Upgrade Path
1. **Start Free**: SQLite + basic features
2. **Add Database**: PostgreSQL for better performance
3. **Add Caching**: Redis for speed
4. **Add Hosting**: Move to cloud or dedicated server
5. **Add Features**: Premium scanners and reports

---

**Bottom Line**: DataGuardian Pro works perfectly on free/budget setups. Start with SQLite and upgrade as needed. Total cost can be €0 for personal use or €50-100 for small business setup.

All features work in budget mode - you just trade some performance and scalability for zero cost. Perfect for getting started and proving value before investing in infrastructure.