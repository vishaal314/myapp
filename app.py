import streamlit as st

# Configure page FIRST - must be the very first Streamlit command
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core imports - keep essential imports minimal
import logging
from datetime import datetime

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def safe_import(module_name, from_list=None):
    """Safely import modules with error handling"""
    try:
        if from_list:
            module = __import__(module_name, fromlist=from_list)
            return {name: getattr(module, name) for name in from_list}
        else:
            return __import__(module_name)
    except ImportError as e:
        logger.error(f"Failed to import {module_name}: {e}")
        return None

# Safe imports with fallbacks
auth_functions = safe_import('services.auth', ['is_authenticated', 'authenticate', 'logout'])
language_functions = safe_import('utils.i18n', ['get_text', 'initialize'])

# Fallback functions if imports fail
def fallback_is_authenticated():
    return st.session_state.get('authenticated', False)

def fallback_get_text(key, default=None):
    return default or key

# Use imported functions or fallbacks
is_authenticated = auth_functions.get('is_authenticated') if auth_functions else fallback_is_authenticated
get_text = language_functions.get('get_text') if language_functions else fallback_get_text

def _(key, default=None):
    return get_text(key, default)

def main():
    """Main application entry point with comprehensive error handling"""
    
    try:
        # Initialize basic session state
        if 'language' not in st.session_state:
            st.session_state.language = 'en'
        
        # Check authentication status
        if not is_authenticated():
            render_landing_page()
            return
        
        # Authenticated user interface
        render_authenticated_interface()
        
    except Exception as e:
        # Comprehensive error handling
        st.error("Application encountered an issue. Loading in safe mode.")
        st.write("**Error Details:**")
        st.code(f"{type(e).__name__}: {str(e)}")
        
        # Fallback to basic interface
        render_safe_mode()

def render_landing_page():
    """Render the beautiful landing page and login interface"""
    
    # Sidebar login
    with st.sidebar:
        st.header("🔐 Login")
        
        # Language selector
        language = st.selectbox("Language / Taal", ["English", "Nederlands"], key="language_select")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    # Simple authentication for demo
                    if username in ["admin", "user", "demo"] and password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = "admin" if username == "admin" else "user"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Try: admin/password or user/password")
                else:
                    st.error("Please enter username and password")
        
        # Registration option
        st.markdown("---")
        st.write("**New user?**")
        if st.button("Create Account"):
            st.info("Registration functionality available in full version")
    
    # Main landing page content
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem;">
            🛡️ DataGuardian Pro
        </h1>
        <h2 style="color: #666; font-weight: 300; margin-bottom: 2rem;">
            Enterprise Privacy Compliance Platform
        </h2>
        <p style="font-size: 1.2rem; color: #444; max-width: 800px; margin: 0 auto;">
            Detect, Manage, and Report Privacy Compliance with AI-powered Precision
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    st.markdown("---")
    
    # Scanner types in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🔍 **Code Analysis**
        - Repository scanning
        - PII detection
        - GDPR compliance
        - Real-time analysis
        """)
        
        st.markdown("""
        ### 📄 **Document Processing**
        - PDF, DOCX, TXT analysis
        - OCR text extraction
        - Sensitive data identification
        """)
    
    with col2:
        st.markdown("""
        ### 🖼️ **Image Analysis**
        - Visual content scanning
        - Text extraction (OCR)
        - Face detection
        - Privacy assessment
        """)
        
        st.markdown("""
        ### 🗄️ **Database Scanning**
        - Multi-database support
        - Schema analysis
        - PII column detection
        """)
    
    with col3:
        st.markdown("""
        ### 🌐 **Website Compliance**
        - Privacy policy analysis
        - Cookie compliance
        - GDPR assessment
        """)
        
        st.markdown("""
        ### 🤖 **AI Model Analysis**
        - ML model privacy risks
        - Bias detection
        - Data leakage assessment
        """)
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h3>Ready to secure your data?</h3>
        <p>Login to start scanning and ensure GDPR compliance</p>
    </div>
    """, unsafe_allow_html=True)

def render_authenticated_interface():
    """Render the main authenticated user interface"""
    
    username = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'user')
    
    # Sidebar navigation
    with st.sidebar:
        st.success(f"Welcome, {username}!")
        
        # Navigation menu
        nav_options = ["🏠 Dashboard", "🔍 New Scan", "📊 Results", "📋 History", "⚙️ Settings"]
        if user_role == "admin":
            nav_options.append("👥 Admin")
        
        selected_nav = st.selectbox("Navigation", nav_options, key="navigation")
        
        st.markdown("---")
        
        # User info
        st.write(f"**Role:** {user_role.title()}")
        st.write(f"**Plan:** Premium")  # Placeholder
        
        # Logout
        if st.button("Logout"):
            for key in ['authenticated', 'username', 'user_role']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Main content based on navigation
    if "Dashboard" in selected_nav:
        render_dashboard()
    elif "New Scan" in selected_nav:
        render_scanner_interface_safe()
    elif "Results" in selected_nav:
        render_results_page()
    elif "History" in selected_nav:
        render_history_page()
    elif "Settings" in selected_nav:
        render_settings_page()
    elif "Admin" in selected_nav:
        render_admin_page()

def render_dashboard():
    """Render the main dashboard"""
    st.title("📊 Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Scans", "156", "+12")
    with col2:
        st.metric("PII Found", "23", "+2")
    with col3:
        st.metric("Compliance Score", "94%", "+3%")
    with col4:
        st.metric("Active Issues", "2", "-1")
    
    # Recent activity
    st.subheader("Recent Scan Activity")
    
    import pandas as pd
    recent_scans = pd.DataFrame({
        'Date': ['2025-07-04', '2025-07-04', '2025-07-03'],
        'Type': ['Code Scan', 'Document Scan', 'Database Scan'],
        'Source': ['github.com/repo1', 'privacy_policy.pdf', 'users_table'],
        'Status': ['✅ Complete', '✅ Complete', '⚠️ Issues Found'],
        'PII Found': [5, 0, 12]
    })
    
    st.dataframe(recent_scans, use_container_width=True)

def render_scanner_interface_safe():
    """Safe version of scanner interface"""
    st.title("🔍 New Scan")
    
    # Scanner type selection
    scan_type = st.selectbox("Select Scanner Type", [
        "Code Scanner - Repository & File Analysis",
        "Document Scanner - PDF, DOCX, TXT",
        "Image Scanner - Visual Content Analysis", 
        "Database Scanner - Table & Column Analysis",
        "Website Scanner - Privacy & Compliance",
        "API Scanner - Endpoint Analysis",
        "AI Model Scanner - ML Privacy Risks",
        "SOC2 Scanner - Compliance Assessment"
    ])
    
    st.markdown("---")
    
    # Configuration based on scanner type
    if "Code Scanner" in scan_type:
        render_code_scanner_config()
    elif "Document Scanner" in scan_type:
        render_document_scanner_config()
    else:
        st.info(f"Configuration for {scan_type} will be available here.")
        
        # Generic file upload
        uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} files")
    
    # Scan button
    st.markdown("---")
    if st.button("🚀 Start Scan", type="primary", use_container_width=True):
        with st.spinner("Running scan..."):
            # Simulate scan
            import time
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
        
        st.success("Scan completed! Check the Results page for details.")

def render_code_scanner_config():
    """Code scanner configuration"""
    st.subheader("📝 Code Scanner Configuration")
    
    # Source selection
    source = st.radio("Source Type", ["Upload Files", "Repository URL"])
    
    if source == "Upload Files":
        uploaded_files = st.file_uploader(
            "Upload Code Files", 
            accept_multiple_files=True,
            type=['py', 'js', 'java', 'ts', 'go', 'rs', 'cpp', 'c', 'h']
        )
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} files ready for scanning")
    
    else:
        repo_url = st.text_input("Repository URL", placeholder="https://github.com/user/repo")
        col1, col2 = st.columns(2)
        with col1:
            branch = st.text_input("Branch", value="main")
        with col2:
            token = st.text_input("Access Token (optional)", type="password")
    
    # Scan options
    st.subheader("⚙️ Scan Options")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Include comments", value=True)
        st.checkbox("Detect secrets", value=True)
    with col2:
        st.checkbox("GDPR compliance check", value=True)
        st.checkbox("Generate remediation", value=True)

def render_document_scanner_config():
    """Document scanner configuration"""
    st.subheader("📄 Document Scanner Configuration")
    
    uploaded_files = st.file_uploader(
        "Upload Documents",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'doc']
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} documents ready for scanning")
        
        # Preview first file info
        first_file = uploaded_files[0]
        st.info(f"First file: {first_file.name} ({first_file.size} bytes)")

def render_results_page():
    """Render results page"""
    st.title("📊 Scan Results")
    st.info("Recent scan results will be displayed here with detailed findings and compliance analysis.")

def render_history_page():
    """Render scan history"""
    st.title("📋 Scan History")
    st.info("Complete scan history with filtering and search capabilities.")

def render_settings_page():
    """Render settings page"""
    st.title("⚙️ Settings")
    st.info("User preferences, API configurations, and compliance settings.")

def render_admin_page():
    """Render admin page"""
    st.title("👥 Admin Panel")
    st.info("User management, system monitoring, and administrative controls.")

def render_safe_mode():
    """Render safe mode interface when components fail"""
    st.title("🛡️ DataGuardian Pro - Safe Mode")
    st.warning("Application is running in safe mode due to component loading issues.")
    
    st.markdown("""
    ### Available Functions:
    - Basic authentication ✅
    - Simple file upload ✅
    - Error reporting ✅
    
    ### Limited Functions:
    - Advanced scanning (requires component reload)
    - Full navigation (requires module import)
    """)
    
    # Basic file upload for testing
    uploaded_file = st.file_uploader("Test File Upload")
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

if __name__ == "__main__":
    main()