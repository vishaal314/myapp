import streamlit as st
import json
import os
from datetime import datetime, timedelta
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simple authentication will be handled directly in the app

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'current_scan_id' not in st.session_state:
        st.session_state.current_scan_id = None
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    if 'payment_successful' not in st.session_state:
        st.session_state.payment_successful = False
    if 'payment_details' not in st.session_state:
        st.session_state.payment_details = None
    if 'checkout_session_id' not in st.session_state:
        st.session_state.checkout_session_id = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

def get_text(key, default=None):
    """Get text for interface elements"""
    # Simple text mapping without external file dependencies
    text_map = {
        'app.title': 'DataGuardian Pro',
        'app.subtitle': 'Enterprise Privacy Compliance Platform', 
        'app.tagline': 'Detect, Manage, and Report Privacy Compliance with AI-powered Precision',
        'login.title': 'Login',
        'login.username': 'Username or Email',
        'login.password': 'Password',
        'login.login_button': 'Login',
        'register.title': 'Register',
        'register.username': 'Username',
        'register.email': 'Email',
        'register.password': 'Password',
        'register.confirm_password': 'Confirm Password',
        'register.register_button': 'Register'
    }
    
    # Handle Dutch translations if needed
    if st.session_state.language == 'nl':
        dutch_map = {
            'app.title': 'DataGuardian Pro',
            'app.subtitle': 'Enterprise Privacy Compliance Platform',
            'app.tagline': 'Detecteer, Beheer en Rapporteer Privacy Compliance met AI-aangedreven Precisie',
            'login.title': 'Inloggen',
            'login.username': 'Gebruikersnaam of E-mail',
            'login.password': 'Wachtwoord',
            'login.login_button': 'Inloggen',
            'register.title': 'Registreren',
            'register.username': 'Gebruikersnaam',
            'register.email': 'E-mail',
            'register.password': 'Wachtwoord',
            'register.confirm_password': 'Bevestig Wachtwoord',
            'register.register_button': 'Registreren'
        }
        text_map.update(dutch_map)
    
    return text_map.get(key, default or key)

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Set page config
    st.set_page_config(
        page_title="DataGuardian Pro - Enterprise Privacy Compliance Platform",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    try:
        with open("static/custom.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    # Language switcher
    col1, col2, col3 = st.columns([6, 3, 1])
    with col3:
        language_options = {"en": "🇬🇧 English", "nl": "🇳🇱 Nederlands"}
        selected_language = st.selectbox(
            "",
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=0 if st.session_state.language == 'en' else 1,
            key="language_selector"
        )
        
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()
    
    # Main app title
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2E86AB; margin-bottom: 0.5rem;">{get_text('app.title')}</h1>
        <h3 style="color: #666; font-weight: normal; margin-bottom: 1rem;">{get_text('app.subtitle')}</h3>
        <p style="color: #888; font-size: 1.1rem;">{get_text('app.tagline')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """Show the login page"""
    st.markdown("---")
    
    # Create tabs for login and register
    tab1, tab2 = st.tabs([get_text('login.title'), get_text('register.title')])
    
    with tab1:
        st.subheader(get_text('login.title'))
        
        with st.form("login_form"):
            username_or_email = st.text_input(get_text('login.username'))
            password = st.text_input(get_text('login.password'), type="password")
            login_button = st.form_submit_button(get_text('login.login_button'))
            
            if login_button:
                if username_or_email and password:
                    # Simple authentication check (replace with actual auth)
                    if username_or_email == "admin" and password == "admin":
                        st.session_state.authenticated = True
                        st.session_state.username = username_or_email
                        st.session_state.role = "admin"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader(get_text('register.title'))
        
        with st.form("register_form"):
            new_username = st.text_input(get_text('register.username'))
            new_email = st.text_input(get_text('register.email'))
            new_password = st.text_input(get_text('register.password'), type="password")
            confirm_password = st.text_input(get_text('register.confirm_password'), type="password")
            register_button = st.form_submit_button(get_text('register.register_button'))
            
            if register_button:
                if new_username and new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

def show_main_app():
    """Show the main application interface"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}!")
        
        # Navigation options
        nav_options = [
            "🏠 Dashboard",
            "🔍 New Scan",
            "📊 History",
            "📋 Results",
            "📄 Reports"
        ]
        
        selected_nav = st.radio("Navigation", nav_options, key="main_nav")
        
        st.markdown("---")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()
    
    # Main content area
    if "Dashboard" in selected_nav:
        show_dashboard()
    elif "New Scan" in selected_nav:
        show_new_scan()
    elif "History" in selected_nav:
        show_history()
    elif "Results" in selected_nav:
        show_results()
    elif "Reports" in selected_nav:
        show_reports()

def show_dashboard():
    """Show the dashboard page"""
    st.header("📊 Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scans", "42", "5")
    
    with col2:
        st.metric("High Risk Items", "3", "-2")
    
    with col3:
        st.metric("Medium Risk Items", "15", "1")
    
    with col4:
        st.metric("Compliance Score", "87%", "3%")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    st.info("Recent scan activity will be displayed here.")

def show_new_scan():
    """Show the new scan page"""
    st.header("🔍 New Scan")
    
    # Scan type selection
    scan_types = [
        "Code Repository",
        "Document Upload",
        "Website Scanner",
        "Database Scanner",
        "API Scanner",
        "Image Scanner",
        "DPIA Assessment"
    ]
    
    selected_scan_type = st.selectbox("Select Scan Type", scan_types)
    
    st.markdown("---")
    
    if selected_scan_type == "Code Repository":
        st.subheader("Code Repository Scanner")
        repo_url = st.text_input("Repository URL")
        branch = st.text_input("Branch (optional)", value="main")
        
        if st.button("Start Code Scan"):
            if repo_url:
                st.success(f"Starting scan for repository: {repo_url}")
                # Add actual scanning logic here
            else:
                st.error("Please enter a repository URL")
    
    elif selected_scan_type == "Document Upload":
        st.subheader("Document Scanner")
        uploaded_files = st.file_uploader(
            "Choose files to scan",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt', 'xlsx']
        )
        
        if uploaded_files and st.button("Start Document Scan"):
            st.success(f"Starting scan for {len(uploaded_files)} files")
            # Add actual scanning logic here
    
    elif selected_scan_type == "DPIA Assessment":
        st.subheader("Data Protection Impact Assessment")
        st.info("DPIA assessment form will be displayed here.")
        
        if st.button("Start DPIA Assessment"):
            st.success("Starting DPIA assessment")
            # Add DPIA logic here
    
    else:
        st.info(f"{selected_scan_type} interface will be implemented here.")

def show_history():
    """Show the scan history page"""
    st.header("📊 Scan History")
    st.info("Scan history will be displayed here.")

def show_results():
    """Show the scan results page"""
    st.header("📋 Scan Results")
    st.info("Scan results will be displayed here.")

def show_reports():
    """Show the reports page"""
    st.header("📄 Reports")
    st.info("Report generation interface will be displayed here.")

if __name__ == "__main__":
    main()