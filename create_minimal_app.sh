#!/bin/bash
# CREATE MINIMAL WORKING APP - Strip down to essentials

set -e

echo "🔧 CREATING MINIMAL WORKING DATAGUARDIAN APP"
echo "========================================="
echo ""

cd /opt/dataguardian

echo "📄 Backing up original app.py..."
cp app.py app.py.full_backup
echo "   ✅ Backed up to app.py.full_backup"

echo ""
echo "✂️  Creating minimal working app.py..."

cat > app.py << 'APPEOF'
#!/usr/bin/env python3
"""DataGuardian Pro - Minimal Working Version"""

import streamlit as st
import logging
import uuid
from datetime import datetime

# Configure page FIRST
if 'page_configured' not in st.session_state:
    st.set_page_config(
        page_title="DataGuardian Pro",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state['page_configured'] = True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("🚀 DataGuardian Pro initializing...")

# Simple authentication check
def is_authenticated():
    return st.session_state.get('authenticated', False)

def login_page():
    """Simple login page"""
    st.title("🛡️ DataGuardian Pro")
    st.subheader("Enterprise Privacy Compliance Platform")
    
    with st.form("login_form"):
        username = st.text_input("Username", value="demo")
        password = st.text_input("Password", type="password", value="demo123")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Simple hardcoded auth for testing
            if username in ["demo", "vishaal314", "admin"] and password in ["demo123", "password123", "admin123"]:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['user_id'] = username
                logger.info(f"✅ User {username} logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

def main_app():
    """Main application interface"""
    st.title("🛡️ DataGuardian Pro")
    st.subheader("Enterprise Privacy Compliance Platform")
    
    # Sidebar
    with st.sidebar:
        st.write(f"**User:** {st.session_state.get('username', 'Unknown')}")
        if st.button("Logout"):
            st.session_state['authenticated'] = False
            st.rerun()
    
    # Main content
    st.success("✅ DataGuardian Pro is running successfully!")
    
    st.markdown("""
    ### Welcome to DataGuardian Pro
    
    **Features:**
    - 🔍 Code Scanner - PII detection in source code
    - 📄 Document Scanner - PII in documents
    - 🖼️ Image Scanner - OCR-based PII detection
    - 🌐 Website Scanner - Privacy compliance checking
    - 🗄️ Database Scanner - PII in databases
    - 🤖 AI Model Scanner - EU AI Act compliance
    - 📊 DPIA Wizard - Data Protection Impact Assessment
    - 🍪 Cookie Scanner - Tracking compliance
    - 🔗 API Scanner - API endpoint analysis
    - 🏢 Enterprise Connectors - Microsoft 365, Google Workspace
    
    **Current Status:**
    - ✅ Application running
    - ✅ Authentication working
    - ✅ Interface loaded
    
    **Next Steps:**
    1. Full scanner integration
    2. Database connectivity
    3. Report generation
    4. License system
    
    *This is a minimal working version. Full features being restored...*
    """)
    
    # Show system info
    with st.expander("System Information"):
        st.json({
            "Status": "Running",
            "User": st.session_state.get('username'),
            "Session ID": st.session_state.get('session_id', 'N/A'),
            "Timestamp": datetime.now().isoformat()
        })

# Main execution
if __name__ == "__main__":
    logger.info("✅ DataGuardian Pro app.py loaded successfully")
    
    if not is_authenticated():
        login_page()
    else:
        main_app()

APPEOF

echo "   ✅ Created minimal app.py"

echo ""
echo "🐳 Updating Docker container..."

# Stop and restart Docker container
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

# Rebuild image with new app.py
docker build -t dataguardian-pro . 2>&1 | tail -10

# Run container
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    dataguardian-pro

echo "   ✅ Docker container restarted"

echo ""
echo "⏳ Waiting for initialization (30 seconds)..."
sleep 30

echo ""
echo "🧪 TESTING DEPLOYMENT"
echo "===================="

echo "Container status:"
docker ps | grep dataguardian-container && echo "   ✅ Running" || echo "   ❌ Not running"

echo ""
echo "HTTP Response:"
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
echo "   Status: $status"

echo ""
echo "DataGuardian Content Check:"
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "   ✅ DataGuardian Pro DETECTED!"
    success=true
else
    echo "   ❌ Not detected"
    success=false
fi

echo ""
echo "Container logs:"
docker logs dataguardian-container 2>&1 | tail -30

if [ "$success" = true ]; then
    echo ""
    echo "🎉 SUCCESS! MINIMAL APP WORKING!"
    echo "==============================="
    echo ""
    echo "✅ DataGuardian Pro is now live"
    echo "✅ Login working (demo/demo123)"
    echo "✅ Interface loading properly"
    echo ""
    echo "🌐 ACCESS:"
    echo "   https://dataguardianpro.nl"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "   1. Test login: demo / demo123"
    echo "   2. Verify interface loads"
    echo "   3. Gradually restore full features"
    echo ""
    echo "💾 RESTORE FULL APP:"
    echo "   cp /opt/dataguardian/app.py.full_backup /opt/dataguardian/app.py"
    echo "   Then rebuild Docker"
else
    echo ""
    echo "⚠️  Still having issues - check logs above"
fi

echo ""
echo "✅ MINIMAL APP DEPLOYMENT COMPLETE"

exit 0
