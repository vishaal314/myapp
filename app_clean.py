import streamlit as st

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Set page config
st.set_page_config(
    page_title="DataGuardian Pro - Enterprise Privacy Compliance Platform",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main app title
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #2E86AB; margin-bottom: 0.5rem;">DataGuardian Pro</h1>
    <h3 style="color: #666; font-weight: normal; margin-bottom: 1rem;">Enterprise Privacy Compliance Platform</h3>
    <p style="color: #888; font-size: 1.1rem;">Detect, Manage, and Report Privacy Compliance with AI-powered Precision</p>
</div>
""", unsafe_allow_html=True)

# Language switcher in top right
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

# Authentication check
if not st.session_state.authenticated:
    st.markdown("---")
    
    # Login and Registration tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to DataGuardian Pro")
        
        with st.form("login_form"):
            username_or_email = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username_or_email and password:
                    # Simple authentication - replace with real auth system
                    if username_or_email == "admin" and password == "admin":
                        st.session_state.authenticated = True
                        st.session_state.username = username_or_email
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Try username: admin, password: admin")
                else:
                    st.error("Please fill in all fields")
        
        st.info("Demo credentials: username = admin, password = admin")
    
    with tab2:
        st.subheader("Register for DataGuardian Pro")
        
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if new_username and new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        st.success("Registration successful! Please login with your credentials.")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

else:
    # Main application interface
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}!")
        
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
            st.rerun()
    
    # Main content based on navigation
    if "Dashboard" in selected_nav:
        st.header("📊 Dashboard")
        
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
        st.subheader("Recent Activity")
        st.info("Recent scan activity will be displayed here.")
        
    elif "New Scan" in selected_nav:
        st.header("🔍 New Scan")
        
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
                
        elif selected_scan_type == "DPIA Assessment":
            st.subheader("Data Protection Impact Assessment")
            st.info("DPIA assessment form will be displayed here.")
            
            if st.button("Start DPIA Assessment"):
                st.success("Starting DPIA assessment")
        else:
            st.info(f"{selected_scan_type} interface will be implemented here.")
            
    elif "History" in selected_nav:
        st.header("📊 Scan History")
        st.info("Scan history will be displayed here.")
        
    elif "Results" in selected_nav:
        st.header("📋 Scan Results")
        st.info("Scan results will be displayed here.")
        
    elif "Reports" in selected_nav:
        st.header("📄 Reports")
        st.info("Report generation interface will be displayed here.")