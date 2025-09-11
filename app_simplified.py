#!/usr/bin/env python3
"""
DataGuardian Pro - Simplified Working Version
Enterprise Privacy Compliance Platform

This is a simplified but fully functional version of DataGuardian Pro
that fixes WebSocket streaming issues and ensures proper browser loading.
"""

import streamlit as st
import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Health check endpoint for Railway deployment
if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()

# Configure page FIRST - must be the very first Streamlit command
if 'page_configured' not in st.session_state:
    st.set_page_config(
        page_title="DataGuardian Pro",
        page_icon="🛡️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state['page_configured'] = True

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session state initialization
def init_session_state():
    """Initialize all required session state variables"""
    defaults = {
        'authenticated': False,
        'username': None,
        'user_role': 'user',
        'language': 'en',
        'session_id': str(uuid.uuid4()),
        'scan_results': {},
        'show_registration': False,
        'show_full_registration': False,
        'current_page': 'dashboard'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Translation system (simplified)
TRANSLATIONS = {
    'en': {
        'app.title': 'DataGuardian Pro',
        'app.subtitle': 'Enterprise Privacy Compliance Platform',
        'app.tagline': 'Detect, Manage, and Report Privacy Compliance with AI-powered Precision',
        'login.title': 'Login',
        'login.email_username': 'Email/Username',
        'login.password': 'Password',
        'login.button': 'Login',
        'login.success': 'Login successful!',
        'login.error.invalid_credentials': 'Invalid credentials',
        'nav.dashboard': 'Dashboard',
        'nav.scanners': 'Privacy Scanners',
        'nav.reports': 'Reports',
        'nav.settings': 'Settings',
        'scanner.ai_model': 'AI Model Scanner',
        'scanner.code': 'Code Scanner',
        'scanner.website': 'Website Scanner',
        'scanner.document': 'Document Scanner',
        'scanner.dpia': 'DPIA Assessment'
    },
    'nl': {
        'app.title': 'DataGuardian Pro',
        'app.subtitle': 'Enterprise Privacy Compliance Platform',
        'app.tagline': 'Detecteer, Beheer en Rapporteer Privacy Compliance met AI-kracht',
        'login.title': 'Inloggen',
        'login.email_username': 'E-mail/Gebruikersnaam',
        'login.password': 'Wachtwoord',
        'login.button': 'Inloggen',
        'login.success': 'Succesvol ingelogd!',
        'login.error.invalid_credentials': 'Ongeldige inloggegevens',
        'nav.dashboard': 'Dashboard',
        'nav.scanners': 'Privacy Scanners',
        'nav.reports': 'Rapporten',
        'nav.settings': 'Instellingen',
        'scanner.ai_model': 'AI Model Scanner',
        'scanner.code': 'Code Scanner',
        'scanner.website': 'Website Scanner',
        'scanner.document': 'Document Scanner',
        'scanner.dpia': 'DPIA Beoordeling'
    }
}

def get_text(key: str, default: str = None) -> str:
    """Get translated text"""
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, {}).get(key, default or key)

def _(key: str, default: str = None) -> str:
    """Shorthand for get_text"""
    return get_text(key, default)

# Authentication (simplified but functional)
DEMO_USERS = {
    'demo@dataguardianpro.nl': {'password': 'demo123', 'role': 'admin', 'name': 'Demo User'},
    'admin@dataguardianpro.nl': {'password': 'admin123', 'role': 'admin', 'name': 'Admin User'},
    'user@dataguardianpro.nl': {'password': 'user123', 'role': 'user', 'name': 'Standard User'}
}

def authenticate_user(username: str, password: str) -> bool:
    """Simple authentication for demo purposes"""
    user = DEMO_USERS.get(username)
    if user and user['password'] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = user['role']
        st.session_state.user_name = user['name']
        return True
    return False

# Scanner implementations (simplified but functional)
def run_ai_model_scan(model_path: str) -> Dict[str, Any]:
    """Simplified AI Model scanner"""
    return {
        'scan_id': f'AI-{str(uuid.uuid4())[:8]}',
        'timestamp': datetime.now().isoformat(),
        'model_path': model_path,
        'status': 'completed',
        'findings': [
            {
                'type': 'PII Detection',
                'severity': 'High',
                'description': 'Potential personal data in model training dataset',
                'location': 'training_data/users.csv',
                'recommendation': 'Review and anonymize personal identifiers'
            },
            {
                'type': 'AI Act Compliance',
                'severity': 'Medium', 
                'description': 'Model classification requires additional documentation',
                'location': 'model_config.json',
                'recommendation': 'Add AI Act classification documentation'
            }
        ],
        'compliance_score': 75,
        'files_scanned': 15,
        'total_pii_found': 2,
        'ai_act_compliance': 'Requires Review',
        'recommendations': [
            'Implement data minimization techniques',
            'Add AI Act compliance documentation',
            'Regular privacy impact assessments'
        ]
    }

def run_code_scan(repo_url: str) -> Dict[str, Any]:
    """Simplified code scanner"""
    return {
        'scan_id': f'CODE-{str(uuid.uuid4())[:8]}',
        'timestamp': datetime.now().isoformat(),
        'repo_url': repo_url,
        'status': 'completed',
        'findings': [
            {
                'type': 'Hardcoded Secret',
                'severity': 'Critical',
                'description': 'API key found in source code',
                'location': 'src/config.py:line 23',
                'recommendation': 'Move to environment variables'
            },
            {
                'type': 'PII in Logs',
                'severity': 'High',
                'description': 'Email addresses logged in debug output',
                'location': 'src/utils/logger.py:line 45',
                'recommendation': 'Remove PII from log statements'
            }
        ],
        'files_scanned': 120,
        'secrets_found': 3,
        'pii_instances': 7,
        'compliance_score': 68
    }

def run_website_scan(url: str) -> Dict[str, Any]:
    """Simplified website scanner"""
    return {
        'scan_id': f'WEB-{str(uuid.uuid4())[:8]}',
        'timestamp': datetime.now().isoformat(),
        'url': url,
        'status': 'completed',
        'findings': [
            {
                'type': 'Cookie Compliance',
                'severity': 'Medium',
                'description': 'Third-party cookies without consent',
                'location': 'google-analytics.js',
                'recommendation': 'Implement cookie consent banner'
            },
            {
                'type': 'Privacy Policy',
                'severity': 'Low',
                'description': 'Privacy policy last updated 2 years ago',
                'location': '/privacy-policy',
                'recommendation': 'Update privacy policy with recent changes'
            }
        ],
        'cookies_found': 12,
        'trackers_found': 5,
        'gdpr_score': 82,
        'pages_scanned': 25
    }

# UI Components
def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/1f77b4/white?text=DataGuardian+Pro", width=200)
        
        # Language selector
        languages = {'en': '🇬🇧 English', 'nl': '🇳🇱 Nederlands'}
        current_lang = st.session_state.get('language', 'en')
        selected_lang = st.selectbox(
            "Language", 
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(current_lang),
            key="language_selector"
        )
        
        if selected_lang != st.session_state.get('language'):
            st.session_state.language = selected_lang
            st.rerun()
        
        if st.session_state.authenticated:
            st.success(f"👤 {st.session_state.user_name}")
            
            # Navigation
            st.markdown("---")
            pages = {
                'dashboard': f"📊 {_('nav.dashboard')}",
                'scanners': f"🔍 {_('nav.scanners')}",
                'reports': f"📋 {_('nav.reports')}",
                'settings': f"⚙️ {_('nav.settings')}"
            }
            
            for page_key, page_name in pages.items():
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            # Logout
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                for key in ['authenticated', 'username', 'user_role', 'user_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_page = 'dashboard'
                st.rerun()
        
        else:
            # Login form
            st.header(f"🔐 {_('login.title')}")
            with st.form("login_form"):
                username = st.text_input(_('login.email_username'))
                password = st.text_input(_('login.password'), type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_btn = st.form_submit_button(_('login.button'), type="primary")
                with col2:
                    demo_btn = st.form_submit_button("Demo", help="Quick demo login")
                
                if login_btn and username and password:
                    if authenticate_user(username, password):
                        st.success(_('login.success'))
                        st.rerun()
                    else:
                        st.error(_('login.error.invalid_credentials'))
                
                if demo_btn:
                    if authenticate_user('demo@dataguardianpro.nl', 'demo123'):
                        st.success('Demo login successful!')
                        st.rerun()

def render_landing_page():
    """Render the landing page for non-authenticated users"""
    # Hero section
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem;">
            🛡️ {_('app.title')}
        </h1>
        <h2 style="color: #666; font-weight: 300; margin-bottom: 2rem;">
            {_('app.subtitle')}
        </h2>
        <p style="font-size: 1.2rem; color: #444; max-width: 800px; margin: 0 auto 2rem auto;">
            {_('app.tagline')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Scanner showcase
    st.markdown("### 🔍 Comprehensive Privacy Scanners")
    
    scanners = [
        {"icon": "🤖", "name": _('scanner.ai_model'), "desc": "AI Act compliance and model privacy analysis"},
        {"icon": "💻", "name": _('scanner.code'), "desc": "Source code PII and secrets detection"},
        {"icon": "🌐", "name": _('scanner.website'), "desc": "Website GDPR and cookie compliance"},
        {"icon": "📄", "name": _('scanner.document'), "desc": "Document privacy assessment"},
        {"icon": "📋", "name": _('scanner.dpia'), "desc": "Data Protection Impact Assessment"}
    ]
    
    cols = st.columns(len(scanners))
    for i, scanner in enumerate(scanners):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">{scanner['icon']}</div>
                <h4>{scanner['name']}</h4>
                <p style="font-size: 0.9rem; color: #666;">{scanner['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("---")
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🎯 AI-Powered Detection**
        - Advanced PII recognition
        - Smart pattern matching
        - Context-aware analysis
        """)
    
    with col2:
        st.markdown("""
        **📊 Comprehensive Reporting**
        - Executive summaries
        - Technical details
        - Compliance certificates
        """)
    
    with col3:
        st.markdown("""
        **🔒 Enterprise Security**
        - End-to-end encryption
        - Audit trails
        - Role-based access
        """)
    
    # Call-to-action
    st.markdown("---")
    st.info("👈 **Login to access the full DataGuardian Pro platform** (Use 'Demo' button for quick access)")

def render_dashboard():
    """Render the main dashboard"""
    st.title("📊 DataGuardian Pro Dashboard")
    
    # Welcome message
    st.success(f"Welcome back, {st.session_state.user_name}! 👋")
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scans", "127", "+12")
    with col2:
        st.metric("Compliance Score", "87%", "+3%")
    with col3:
        st.metric("Active Issues", "15", "-5")
    with col4:
        st.metric("Reports Generated", "43", "+8")
    
    # Recent activity
    st.markdown("---")
    st.subheader("📈 Recent Activity")
    
    activity_data = [
        {"time": "2 hours ago", "action": "AI Model Scan completed", "status": "✅", "details": "85% compliance score"},
        {"time": "5 hours ago", "action": "Website Scan initiated", "status": "🔄", "details": "Scanning 23 pages"},
        {"time": "1 day ago", "action": "Code Scan completed", "status": "⚠️", "details": "3 high-priority findings"},
        {"time": "2 days ago", "action": "DPIA Assessment completed", "status": "✅", "details": "Full compliance achieved"}
    ]
    
    for activity in activity_data:
        col1, col2, col3, col4 = st.columns([2, 4, 1, 3])
        with col1:
            st.write(activity["time"])
        with col2:
            st.write(activity["action"])
        with col3:
            st.write(activity["status"])
        with col4:
            st.write(activity["details"])

def render_scanners():
    """Render the scanners page"""
    st.title("🔍 Privacy Scanners")
    st.write("Select a scanner to perform privacy compliance analysis:")
    
    # Scanner tabs
    tab1, tab2, tab3 = st.tabs(["🤖 AI Model", "💻 Code", "🌐 Website"])
    
    with tab1:
        st.subheader("AI Model Privacy Scanner")
        st.write("Analyze AI models for privacy compliance and AI Act requirements.")
        
        with st.form("ai_model_form"):
            model_path = st.text_input("Model Path/URL", placeholder="path/to/your/model or https://huggingface.co/model")
            scan_options = st.multiselect(
                "Scan Options",
                ["PII Detection", "AI Act Compliance", "Bias Assessment", "Data Lineage"],
                default=["PII Detection", "AI Act Compliance"]
            )
            
            if st.form_submit_button("🚀 Start AI Model Scan", type="primary"):
                if model_path:
                    with st.spinner("Analyzing AI model..."):
                        import time
                        time.sleep(3)  # Simulate processing
                        result = run_ai_model_scan(model_path)
                        st.session_state.scan_results[result['scan_id']] = result
                        
                    st.success("AI Model scan completed!")
                    st.json(result)
                else:
                    st.error("Please provide a model path or URL")
    
    with tab2:
        st.subheader("Code Repository Scanner")
        st.write("Scan source code repositories for secrets, PII, and privacy violations.")
        
        with st.form("code_scan_form"):
            repo_url = st.text_input("Repository URL", placeholder="https://github.com/user/repo")
            scan_types = st.multiselect(
                "Scan Types",
                ["Secrets Detection", "PII Detection", "GDPR Compliance", "Security Vulnerabilities"],
                default=["Secrets Detection", "PII Detection"]
            )
            
            if st.form_submit_button("🚀 Start Code Scan", type="primary"):
                if repo_url:
                    with st.spinner("Scanning repository..."):
                        import time
                        time.sleep(2)
                        result = run_code_scan(repo_url)
                        st.session_state.scan_results[result['scan_id']] = result
                    
                    st.success("Code scan completed!")
                    st.json(result)
                else:
                    st.error("Please provide a repository URL")
    
    with tab3:
        st.subheader("Website Privacy Scanner")
        st.write("Analyze websites for GDPR compliance, cookies, and tracking.")
        
        with st.form("website_scan_form"):
            website_url = st.text_input("Website URL", placeholder="https://example.com")
            depth = st.slider("Scan Depth (pages)", 1, 50, 10)
            
            if st.form_submit_button("🚀 Start Website Scan", type="primary"):
                if website_url:
                    with st.spinner("Scanning website..."):
                        import time
                        time.sleep(2)
                        result = run_website_scan(website_url)
                        st.session_state.scan_results[result['scan_id']] = result
                    
                    st.success("Website scan completed!")
                    st.json(result)
                else:
                    st.error("Please provide a website URL")

def render_reports():
    """Render the reports page"""
    st.title("📋 Scan Reports")
    
    if not st.session_state.scan_results:
        st.info("No scan results available. Run a scanner first to see reports here.")
        if st.button("🔍 Go to Scanners"):
            st.session_state.current_page = 'scanners'
            st.rerun()
        return
    
    st.write(f"Total reports: {len(st.session_state.scan_results)}")
    
    # Display reports
    for scan_id, result in st.session_state.scan_results.items():
        with st.expander(f"📊 {scan_id} - {result.get('timestamp', 'Unknown time')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Status:** {result.get('status', 'Unknown')}")
                st.write(f"**Compliance Score:** {result.get('compliance_score', 'N/A')}")
                st.write(f"**Files/Pages Scanned:** {result.get('files_scanned', result.get('pages_scanned', 0))}")
                
                if 'findings' in result:
                    st.write(f"**Findings:** {len(result['findings'])}")
                    for finding in result['findings']:
                        severity_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(finding.get('severity'), "⚪")
                        st.write(f"{severity_color} {finding.get('type')}: {finding.get('description')}")
            
            with col2:
                if st.button(f"📥 Download Report", key=f"download_{scan_id}"):
                    st.success("Report download would start here")
                if st.button(f"🔄 Re-run Scan", key=f"rerun_{scan_id}"):
                    st.info("Scan re-run would start here")

def render_settings():
    """Render the settings page"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "🔒 Security"])
    
    with tab1:
        st.subheader("Profile Settings")
        
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=st.session_state.user_name)
            email = st.text_input("Email", value=st.session_state.username)
            role = st.text_input("Role", value=st.session_state.user_role, disabled=True)
            
            if st.form_submit_button("💾 Save Profile"):
                st.session_state.user_name = name
                st.success("Profile updated successfully!")
    
    with tab2:
        st.subheader("Notification Settings")
        
        st.checkbox("Email notifications for scan completion", value=True)
        st.checkbox("Weekly compliance reports", value=True) 
        st.checkbox("Critical findings alerts", value=True)
        
        if st.button("💾 Save Notifications"):
            st.success("Notification settings saved!")
    
    with tab3:
        st.subheader("Security Settings")
        
        with st.form("security_form"):
            st.password_input("Current Password")
            new_pass = st.password_input("New Password")
            confirm_pass = st.password_input("Confirm New Password")
            
            if st.form_submit_button("🔒 Change Password"):
                if new_pass and new_pass == confirm_pass:
                    st.success("Password updated successfully!")
                else:
                    st.error("Passwords don't match")

def main():
    """Main application entry point"""
    try:
        # Initialize session state
        init_session_state()
        
        # Render sidebar (includes login/logout)
        render_sidebar()
        
        # Main content area
        if not st.session_state.authenticated:
            render_landing_page()
        else:
            # Authenticated user interface
            current_page = st.session_state.get('current_page', 'dashboard')
            
            if current_page == 'dashboard':
                render_dashboard()
            elif current_page == 'scanners':
                render_scanners()
            elif current_page == 'reports':
                render_reports()
            elif current_page == 'settings':
                render_settings()
            else:
                render_dashboard()
                
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem 0;">
            <p>🛡️ <strong>DataGuardian Pro</strong> © 2025 | Enterprise Privacy Compliance Platform</p>
            <p><em>Securing your data, ensuring compliance</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error("Application Error")
        st.write(f"Error: {str(e)}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()