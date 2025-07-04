import streamlit as st

# Configure page FIRST
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide"
)

# Minimal landing page to test functionality
st.title("🛡️ DataGuardian Pro")
st.subheader("Enterprise Privacy Compliance Platform")

st.write("Debug Mode - Testing basic functionality")

# Test authentication without complex imports
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username and password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.sidebar.error("Please enter username and password")
    
    # Landing page content
    st.markdown("""
    ## Welcome to DataGuardian Pro
    
    Your comprehensive GDPR compliance platform for:
    - 🔍 Code scanning for PII detection
    - 📄 Document analysis
    - 🖼️ Image processing
    - 🗄️ Database scanning
    - 🌐 Website compliance checking
    
    **Please login to access scanning features.**
    """)
    
else:
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.success("Successfully logged in! Full scanner interface will be available here.")
    
    # Simple scanner selection
    scan_type = st.selectbox("Select Scanner Type", [
        "Code Scanner", 
        "Document Scanner", 
        "Image Scanner",
        "Database Scanner"
    ])
    
    if st.button("Start Scan"):
        st.info(f"Starting {scan_type}... (Debug mode)")