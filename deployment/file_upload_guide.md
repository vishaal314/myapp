# File Upload Guide for DataGuardian Pro VPS Deployment

## Server Information
- **Server**: vishaalnoord7.retzor.com
- **IP**: 45.81.35.202
- **User**: root
- **Password**: 9q54IQq0S4l3
- **Application Path**: `/opt/dataguardian-pro/`

## Upload Methods

### Method 1: SCP (Secure Copy) - RECOMMENDED
```bash
# Upload entire project directory
scp -r /path/to/dataguardian-pro/* root@45.81.35.202:/opt/dataguardian-pro/

# Upload specific files
scp app.py root@45.81.35.202:/opt/dataguardian-pro/
scp -r services/ root@45.81.35.202:/opt/dataguardian-pro/
scp -r utils/ root@45.81.35.202:/opt/dataguardian-pro/
scp -r components/ root@45.81.35.202:/opt/dataguardian-pro/
```

### Method 2: SFTP (Secure File Transfer)
```bash
# Connect via SFTP
sftp root@45.81.35.202

# Navigate to application directory
cd /opt/dataguardian-pro

# Upload files
put app.py
put -r services/
put -r utils/
put -r components/
put -r config/
```

### Method 3: Git Repository (BEST PRACTICE)
```bash
# On your VPS, clone from your repository
ssh root@45.81.35.202
cd /opt/dataguardian-pro
git clone https://github.com/yourusername/dataguardian-pro.git .

# Set up deployment key for future updates
ssh-keygen -t ed25519 -C "dataguardian-deploy@vishaalnoord7.retzor.com"
# Add public key to your GitHub/GitLab repository deploy keys
```

### Method 4: Using VSCode with Remote SSH
1. Install "Remote - SSH" extension in VSCode
2. Connect to `root@45.81.35.202`
3. Navigate to `/opt/dataguardian-pro/`
4. Upload files directly through VSCode interface

## Required File Structure
```
/opt/dataguardian-pro/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── services/                       # Scanner services
│   ├── code_scanner.py
│   ├── blob_scanner.py
│   ├── image_scanner.py
│   ├── website_scanner.py
│   ├── database_scanner.py
│   ├── dpia_scanner.py
│   ├── ai_model_scanner.py
│   ├── soc2_scanner.py
│   ├── sustainability_scanner.py
│   └── enterprise_connector_scanner.py
├── utils/                          # Utility modules
│   ├── comprehensive_gdpr_validator.py
│   ├── eu_ai_act_compliance.py
│   ├── netherlands_uavg_compliance.py
│   ├── real_time_compliance_monitor.py
│   ├── database_optimizer.py
│   ├── redis_cache.py
│   ├── session_optimizer.py
│   └── code_profiler.py
├── components/                     # UI components
│   ├── pricing_display.py
│   └── language_selector.py
├── config/                        # Configuration
│   ├── pricing_config.py
│   └── translations.py
├── patent_proofs/                 # Patent documentation
│   ├── technical_backing_proof.md
│   ├── patent_portfolio_summary.md
│   └── test_results_validation.md
└── static/                        # Static assets (if any)
```

## File Permissions Setup
After uploading files, run these commands on your VPS:

```bash
# Set correct ownership
chown -R dataguardian:dataguardian /opt/dataguardian-pro/

# Set correct permissions
chmod 755 /opt/dataguardian-pro/
chmod 644 /opt/dataguardian-pro/*.py
chmod 755 /opt/dataguardian-pro/deploy.sh

# Make sure virtual environment has correct permissions
chown -R dataguardian:dataguardian /opt/dataguardian-pro/venv/
```

## Environment Variables Setup
Create `.env` file in `/opt/dataguardian-pro/`:

```bash
# Database
DATABASE_URL=postgresql://dataguardian_user:SecureDbPassword2025!@localhost:5432/dataguardian_pro

# Application settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=127.0.0.1
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Netherlands compliance
REGION=Netherlands
GDPR_JURISDICTION=EU
DATA_RESIDENCY=Netherlands

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
BCRYPT_ROUNDS=12

# API Keys (add as needed)
OPENAI_API_KEY=your-openai-key
STRIPE_SECRET_KEY=your-stripe-key

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0
```

## Upload Commands Summary

### Complete Upload Process
```bash
# 1. Upload all files
scp -r . root@45.81.35.202:/opt/dataguardian-pro/

# 2. SSH into server
ssh root@45.81.35.202

# 3. Set permissions
chown -R dataguardian:dataguardian /opt/dataguardian-pro/
chmod +x /opt/dataguardian-pro/deploy.sh

# 4. Install dependencies
sudo -u dataguardian bash
cd /opt/dataguardian-pro
source venv/bin/activate
pip install -r requirements.txt

# 5. Start the application
sudo systemctl start dataguardian-pro
sudo systemctl status dataguardian-pro
```

### Quick Update Process
```bash
# For future updates
scp -r services/ utils/ components/ app.py root@45.81.35.202:/opt/dataguardian-pro/
ssh root@45.81.35.202 "cd /opt/dataguardian-pro && ./deploy.sh"
```

## Verification Steps
After uploading:

1. **Check file structure**: `ls -la /opt/dataguardian-pro/`
2. **Verify permissions**: `ls -la /opt/dataguardian-pro/`
3. **Test application**: `sudo systemctl status dataguardian-pro`
4. **Check logs**: `sudo journalctl -u dataguardian-pro -f`
5. **Test website**: `curl http://localhost:8501`
6. **Test domain**: `curl https://vishaalnoord7.retzor.com`

## Troubleshooting
- **Permission denied**: Run `chown -R dataguardian:dataguardian /opt/dataguardian-pro/`
- **Module not found**: Run `pip install -r requirements.txt` in virtual environment
- **Service won't start**: Check logs with `sudo journalctl -u dataguardian-pro -f`
- **502 Bad Gateway**: Check if Streamlit is running on port 8501

Your DataGuardian Pro application will be live at **https://vishaalnoord7.retzor.com** once uploaded and configured!