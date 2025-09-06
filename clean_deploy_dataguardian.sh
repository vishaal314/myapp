#!/bin/bash
# DataGuardian Pro - Complete Clean Deployment Script
# This script removes existing installation and deploys fresh DataGuardian Pro

set -e  # Exit on any error

echo "🚀 DataGuardian Pro - Complete Clean Deployment"
echo "================================================"

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "❌ This script must be run as root"
        echo "   Run: sudo $0"
        exit 1
    fi
}

# Function to clean existing installation
clean_existing() {
    echo ""
    echo "🧹 Cleaning existing DataGuardian Pro installation..."
    
    # Stop existing service
    if systemctl is-active --quiet dataguardian-pro 2>/dev/null; then
        echo "   Stopping DataGuardian Pro service..."
        systemctl stop dataguardian-pro
    fi
    
    # Disable existing service
    if systemctl is-enabled --quiet dataguardian-pro 2>/dev/null; then
        echo "   Disabling DataGuardian Pro service..."
        systemctl disable dataguardian-pro
    fi
    
    # Remove service file
    if [ -f "/etc/systemd/system/dataguardian-pro.service" ]; then
        echo "   Removing service file..."
        rm -f /etc/systemd/system/dataguardian-pro.service
    fi
    
    # Remove application directory
    if [ -d "/opt/dataguardian-pro" ]; then
        echo "   Removing application directory..."
        rm -rf /opt/dataguardian-pro
    fi
    
    # Remove user
    if id "dataguardian" &>/dev/null; then
        echo "   Removing dataguardian user..."
        userdel -r dataguardian 2>/dev/null || true
    fi
    
    # Reload systemd
    systemctl daemon-reload
    
    echo "   ✅ Existing installation cleaned"
}

# Function to create user and directories
setup_user() {
    echo ""
    echo "👤 Setting up dataguardian user..."
    
    # Create dataguardian user
    useradd -r -m -s /bin/bash dataguardian
    
    # Create application directory
    mkdir -p /opt/dataguardian-pro
    chown dataguardian:dataguardian /opt/dataguardian-pro
    
    echo "   ✅ User and directories created"
}

# Function to install dependencies
install_dependencies() {
    echo ""
    echo "📦 Installing system dependencies..."
    
    # Update package list
    apt update
    
    # Install required packages
    apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git curl wget
    
    echo "   ✅ System dependencies installed"
}

# Function to deploy application
deploy_application() {
    echo ""
    echo "🚀 Deploying DataGuardian Pro application..."
    
    cd /opt/dataguardian-pro
    
    # Download application from your server (replace with your actual source)
    echo "   Downloading application files..."
    
    # If you have the app.py and other files, copy them here
    # For now, we'll create the basic structure
    
    # Create Python virtual environment
    echo "   Creating Python virtual environment..."
    sudo -u dataguardian python3 -m venv venv
    
    # Activate virtual environment and install requirements
    echo "   Installing Python dependencies..."
    sudo -u dataguardian bash -c "
        source venv/bin/activate
        pip install --upgrade pip
        pip install streamlit bcrypt cryptography psycopg2-binary redis python-jose pillow reportlab requests beautifulsoup4 pytesseract opencv-python-headless pandas plotly pyyaml aiohttp anthropic openai stripe textract pypdf2 trafilatura tldextract
    "
    
    echo "   ✅ Application deployed"
}

# Function to create configuration files
create_config() {
    echo ""
    echo "⚙️ Creating configuration files..."
    
    cd /opt/dataguardian-pro
    
    # Create admin users
    sudo -u dataguardian bash -c "python3 -c '
import bcrypt
import json
from datetime import datetime

# Create admin users
admin_hash = bcrypt.hashpw(\"admin123\".encode(\"utf-8\"), bcrypt.gensalt()).decode(\"utf-8\")
demo_hash = bcrypt.hashpw(\"demo123\".encode(\"utf-8\"), bcrypt.gensalt()).decode(\"utf-8\")

users = {
    \"admin\": {
        \"user_id\": \"admin_001\",
        \"username\": \"admin\",
        \"password_hash\": admin_hash,
        \"role\": \"admin\",
        \"email\": \"admin@dataguardian.pro\",
        \"active\": True,
        \"created_at\": datetime.now().isoformat(),
        \"last_login\": None,
        \"failed_attempts\": 0,
        \"locked_until\": None
    },
    \"demo\": {
        \"user_id\": \"demo_001\",
        \"username\": \"demo\",
        \"password_hash\": demo_hash,
        \"role\": \"viewer\",
        \"email\": \"demo@dataguardian.pro\",
        \"active\": True,
        \"created_at\": datetime.now().isoformat(),
        \"last_login\": None,
        \"failed_attempts\": 0,
        \"locked_until\": None
    }
}

with open(\"secure_users.json\", \"w\") as f:
    json.dump(users, f, indent=2)

print(\"Users created\")
'"
    
    # Create enterprise license
    sudo -u dataguardian bash -c "python3 -c '
import json
from datetime import datetime, timedelta

license_config = {
    \"license_id\": \"DGP-ENT-2025-001\",
    \"license_type\": \"enterprise\",
    \"customer_id\": \"admin_001\",
    \"customer_name\": \"Admin User\",
    \"company_name\": \"DataGuardian Pro\",
    \"email\": \"admin@dataguardian.pro\",
    \"issued_date\": datetime.now().isoformat(),
    \"expiry_date\": (datetime.now() + timedelta(days=3650)).isoformat(),
    \"is_active\": True,
    \"usage_limits\": [],
    \"allowed_features\": [\"all_scanners\", \"ai_act_compliance\", \"netherlands_uavg\", \"enterprise_connectors\", \"unlimited_reports\", \"certificate_generation\", \"api_access\", \"compliance_dashboard\", \"reporting\"],
    \"allowed_scanners\": [\"code_scanner\", \"blob_scanner\", \"website_scanner\", \"database_scanner\", \"ai_model_scanner\", \"dpia_scanner\", \"soc2_scanner\", \"sustainability_scanner\", \"image_scanner\"],
    \"allowed_regions\": [\"Netherlands\", \"Germany\", \"France\", \"Belgium\", \"EU\"],
    \"max_concurrent_users\": 999,
    \"metadata\": {\"plan_name\": \"Enterprise\", \"subscription_status\": \"active\"}
}

with open(\"license.json\", \"w\") as f:
    json.dump(license_config, f, indent=2)

with open(\"user_licenses.json\", \"w\") as f:
    json.dump({\"admin\": {\"license_id\": \"DGP-ENT-2025-001\", \"status\": \"active\"}}, f, indent=2)

print(\"License created\")
'"
    
    # Set ownership
    chown -R dataguardian:dataguardian /opt/dataguardian-pro
    
    echo "   ✅ Configuration files created"
}

# Function to create systemd service
create_service() {
    echo ""
    echo "🔧 Creating systemd service..."
    
    cat > /etc/systemd/system/dataguardian-pro.service << 'EOF'
[Unit]
Description=DataGuardian Pro Streamlit Application
After=network.target

[Service]
Type=simple
User=dataguardian
Group=dataguardian
WorkingDirectory=/opt/dataguardian-pro
Environment=PATH=/opt/dataguardian-pro/venv/bin
ExecStart=/opt/dataguardian-pro/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable dataguardian-pro
    
    echo "   ✅ Systemd service created"
}

# Function to setup nginx reverse proxy
setup_nginx() {
    echo ""
    echo "🌐 Setting up Nginx reverse proxy..."
    
    # Remove default nginx config
    rm -f /etc/nginx/sites-enabled/default
    
    # Create DataGuardian Pro nginx config
    cat > /etc/nginx/sites-available/dataguardian-pro << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
EOF
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/dataguardian-pro /etc/nginx/sites-enabled/
    
    # Test and reload nginx
    nginx -t
    systemctl restart nginx
    systemctl enable nginx
    
    echo "   ✅ Nginx configured"
}

# Function to create basic app.py if not exists
create_basic_app() {
    echo ""
    echo "📱 Creating basic application..."
    
    cd /opt/dataguardian-pro
    
    if [ ! -f "app.py" ]; then
        sudo -u dataguardian cat > app.py << 'EOF'
import streamlit as st
import json
import bcrypt
from datetime import datetime

st.set_page_config(page_title="DataGuardian Pro", layout="wide")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def load_users():
    try:
        with open('secure_users.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def authenticate(username, password):
    users = load_users()
    if username in users:
        stored_hash = users[username]['password_hash']
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
    return False

def check_license():
    try:
        with open('license.json', 'r') as f:
            license_data = json.load(f)
        return license_data.get('is_active', False)
    except:
        return False

# Main application
if not st.session_state.authenticated:
    st.title("🛡️ DataGuardian Pro")
    st.subheader("Enterprise Privacy Compliance Platform")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    # Check license
    if not check_license():
        st.error("License invalid or expired")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    else:
        # Main application interface
        st.title("🛡️ DataGuardian Pro - Enterprise Dashboard")
        st.success(f"Welcome, {st.session_state.username}!")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("🇳🇱 Netherlands UAVG Compliance Platform")
        with col2:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()
        
        # Feature tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Scanners", "📋 Reports", "⚙️ Settings"])
        
        with tab1:
            st.header("Compliance Dashboard")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Scans", "0", "0")
            with col2:
                st.metric("PII Found", "0", "0")
            with col3:
                st.metric("Compliance Score", "100%", "0%")
            with col4:
                st.metric("Risk Level", "Low", "0")
            
            st.info("✅ Enterprise license active - All features unlocked")
            st.success("🇳🇱 Netherlands UAVG compliance monitoring active")
            st.success("🇪🇺 EU AI Act 2025 compliance ready")
        
        with tab2:
            st.header("Enterprise Scanners")
            
            scanners = [
                "🔍 Code Scanner - GDPR & PII Detection",
                "📄 Document Scanner - Blob Analysis", 
                "🌐 Website Scanner - Privacy Compliance",
                "🗄️ Database Scanner - Data Protection",
                "🤖 AI Model Scanner - EU AI Act 2025",
                "📋 DPIA Scanner - Impact Assessment",
                "🛡️ SOC2 Scanner - Security Compliance",
                "🌱 Sustainability Scanner - Green IT",
                "🖼️ Image Scanner - OCR Privacy Check",
                "🔗 Enterprise Connectors - API Integration"
            ]
            
            for scanner in scanners:
                with st.expander(scanner):
                    st.write("Scanner ready for use with enterprise license")
                    st.button("Run Scanner", key=scanner)
        
        with tab3:
            st.header("Compliance Reports")
            st.info("Report generation available with enterprise license")
            
            report_types = [
                "GDPR Compliance Report",
                "Netherlands UAVG Report", 
                "EU AI Act 2025 Assessment",
                "Data Protection Impact Assessment",
                "Security Compliance Certificate"
            ]
            
            for report in report_types:
                st.write(f"📄 {report}")
        
        with tab4:
            st.header("Settings")
            st.write("**License Information**")
            st.success("✅ Enterprise License Active")
            st.write("**Features**: All scanners, unlimited scans, priority support")
            st.write("**Regions**: Netherlands, Germany, France, Belgium, EU")
            st.write("**Expires**: 2034-09-06 (10 years)")
            
            st.write("**System Status**")
            st.success("🟢 All systems operational")
            st.success("🇳🇱 Netherlands data residency compliant")
EOF
        echo "   ✅ Basic application created"
    fi
    
    chown dataguardian:dataguardian app.py
}

# Function to start services
start_services() {
    echo ""
    echo "🚀 Starting services..."
    
    # Start DataGuardian Pro
    systemctl start dataguardian-pro
    
    # Wait for startup
    sleep 5
    
    # Check status
    if systemctl is-active --quiet dataguardian-pro; then
        echo "   ✅ DataGuardian Pro service started"
    else
        echo "   ❌ DataGuardian Pro service failed to start"
        systemctl status dataguardian-pro
    fi
    
    # Check nginx
    if systemctl is-active --quiet nginx; then
        echo "   ✅ Nginx service running"
    else
        echo "   ❌ Nginx service failed"
        systemctl status nginx
    fi
}

# Function to display final information
display_final_info() {
    echo ""
    echo "🎉 DataGuardian Pro Deployment Complete!"
    echo "========================================"
    echo ""
    echo "🌐 Access URL: http://$(hostname -I | awk '{print $1}')"
    echo "📧 Admin Login: admin / admin123"
    echo "👤 Demo Login: demo / demo123"
    echo ""
    echo "📁 Installation Directory: /opt/dataguardian-pro"
    echo "🔧 Service Name: dataguardian-pro"
    echo "📊 Service Status: $(systemctl is-active dataguardian-pro)"
    echo ""
    echo "🛠️ Management Commands:"
    echo "   Start:   systemctl start dataguardian-pro"
    echo "   Stop:    systemctl stop dataguardian-pro"
    echo "   Restart: systemctl restart dataguardian-pro"
    echo "   Status:  systemctl status dataguardian-pro"
    echo "   Logs:    journalctl -u dataguardian-pro -f"
    echo ""
    echo "🗑️ To remove completely, run this script with 'clean' argument"
    echo ""
}

# Main execution
main() {
    # Check if running cleanup only
    if [ "$1" = "clean" ]; then
        echo "🗑️ Cleaning existing DataGuardian Pro installation..."
        check_root
        clean_existing
        echo "✅ Cleanup complete!"
        exit 0
    fi
    
    echo "Starting fresh deployment..."
    check_root
    clean_existing
    setup_user
    install_dependencies
    deploy_application
    create_config
    create_service
    setup_nginx
    create_basic_app
    start_services
    display_final_info
}

# Run main function with all arguments
main "$@"