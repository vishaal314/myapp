import streamlit as st
import pandas as pd
import plotly.express as px
import os
import uuid
from datetime import datetime
import json
import base64
from io import BytesIO

from services.code_scanner import CodeScanner
from services.blob_scanner import BlobScanner
from services.results_aggregator import ResultsAggregator
from services.report_generator import generate_report
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email
from utils.gdpr_rules import REGIONS, get_region_rules

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'current_scan_id' not in st.session_state:
    st.session_state.current_scan_id = None
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

# Set page config
st.set_page_config(
    page_title="GDPR Scan Engine",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication sidebar with professional colorful design
with st.sidebar:
    # Header with gradient background
    st.markdown("""
    <div style="background-image: linear-gradient(120deg, #3B82F6, #1E40AF); 
               padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;
               box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white; margin: 0; font-weight: bold;">GDPR Scan Engine</h2>
        <p style="color: #E0F2FE; margin: 5px 0 0 0; font-size: 0.9em;">Professional Compliance Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centered shield icon with glow effect
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="display: inline-block; 
                   background: radial-gradient(circle, rgba(239,246,255,0.8) 0%, rgba(219,234,254,0) 70%); 
                   border-radius: 50%; padding: 15px;">
            <img src="https://img.icons8.com/fluency/96/shield-lock.png" alt="GDPR Shield" 
                 style="width: 60px; height: 60px; display: block;">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Tab UI for login/register with colorful styling
        st.markdown("""
        <style>
        .tab-selected {
            background-color: #3B82F6 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 0;
        }
        .tab-not-selected {
            background-color: #EFF6FF;
            color: #1E40AF;
            border-radius: 5px;
            padding: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.columns(2)
        
        with tab1:
            if st.button("Login", key="tab_login", use_container_width=True):
                st.session_state.active_tab = "login"
        
        with tab2:
            if st.button("Register", key="tab_register", use_container_width=True):
                st.session_state.active_tab = "register"
        
        # Default to login tab if not set
        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "login"
            
        # Apply custom styling to selected tab
        if st.session_state.active_tab == "login":
            st.markdown("""
            <style>
            [data-testid="stButton"] button:nth-child(1) {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            [data-testid="stButton"] button:nth-child(2) {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin: 0; padding: 0; margin-bottom: 15px;'>", unsafe_allow_html=True)
        
        # Login Form with colorful styling
        if st.session_state.active_tab == "login":
            st.markdown("""
            <div style="background-image: linear-gradient(to right, #DBEAFE, #EFF6FF); 
                       padding: 15px; border-radius: 10px; margin-bottom: 15px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <h4 style="color: #1E40AF; margin: 0 0 10px 0; text-align: center;">
                    <i>Sign In</i>
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            username_or_email = st.text_input("Email/Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            cols = st.columns([3, 2])
            with cols[0]:
                remember = st.checkbox("Remember me", key="remember_login")
            with cols[1]:
                st.markdown("<p style='text-align: right; font-size: 0.8em;'><a href='#'>Forgot?</a></p>", unsafe_allow_html=True)
                
            # Blue gradient login button
            st.markdown("""
            <style>
            div[data-testid="stButton"] button[kind="primaryButton"] {
                background-image: linear-gradient(to right, #3B82F6, #2563EB);
                border: none;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            login_button = st.button("Sign In", use_container_width=True, key="sidebar_login", type="primary")
            
            if login_button:
                if not username_or_email or not password:
                    st.error("Please enter both email/username and password.")
                else:
                    user_data = authenticate(username_or_email, password)
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.username = user_data["username"]
                        st.session_state.role = user_data["role"]
                        st.session_state.email = user_data.get("email", "")
                        st.success(f"Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
        
        # Registration Form with green colorful styling
        else:
            st.markdown("""
            <div style="background-image: linear-gradient(to right, #D1FAE5, #ECFDF5); 
                       padding: 15px; border-radius: 10px; margin-bottom: 15px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <h4 style="color: #065F46; margin: 0 0 10px 0; text-align: center;">
                    <i>Create New Account</i>
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            new_username = st.text_input("Username", key="register_username")
            new_email = st.text_input("Email", key="register_email", 
                                    placeholder="Enter a valid email address")
            new_password = st.text_input("Password", type="password", key="register_password",
                                help="Password must be at least 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            # Role selection with custom styling
            role_options = ["viewer", "analyst", "admin"]
            new_role = st.selectbox("Role", role_options, index=0)
            
            # Green checkmark for terms
            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            # Green gradient register button
            st.markdown("""
            <style>
            div[data-testid="stButton"] button[kind="primaryButton"] {
                background-image: linear-gradient(to right, #10B981, #059669);
                border: none;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            register_button = st.button("Create Account", use_container_width=True, key="sidebar_register", type="primary")
            
            if register_button:
                if not new_username or not new_email or not new_password:
                    st.error("Please fill out all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif not terms:
                    st.error("You must agree to the Terms of Service and Privacy Policy.")
                else:
                    success, message = create_user(new_username, new_password, new_role, new_email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    else:
        # Colorful user profile section when logged in
        st.markdown(f"""
        <div style="background-image: linear-gradient(to right, #DBEAFE, #93C5FD); 
                   padding: 20px; border-radius: 15px; margin-bottom: 15px;
                   box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            <div style="display: flex; align-items: center; justify-content: center; 
                       width: 70px; height: 70px; background-color: #3B82F6; 
                       border-radius: 50%; margin: 0 auto 15px auto;">
                <span style="color: white; font-size: 1.8rem; font-weight: bold;">{st.session_state.username[0].upper()}</span>
            </div>
            <h3 style="margin: 0; color: #1E40AF; text-align: center;">Welcome back</h3>
            <p style="margin: 5px 0 0 0; text-align: center; font-weight: bold;">{st.session_state.username}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User details with icons
        st.markdown(f"""
        <div style="margin: 15px 0; background-color: white; padding: 15px; border-radius: 10px; 
                   border-left: 4px solid #3B82F6;">
            <p><span style="color: #3B82F6;">👤</span> <strong>Role:</strong> {st.session_state.role}</p>
            <p><span style="color: #3B82F6;">✉️</span> <strong>Email:</strong> {st.session_state.email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions section
        st.markdown("""
        <p style="font-size: 0.9rem; color: #6B7280; margin-bottom: 5px;">Quick Actions</p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("🔎 My Scans", use_container_width=True)
        with col2:
            st.button("⚙️ Settings", use_container_width=True)
        
        # Styled logout button
        st.markdown("""
        <style>
        div[data-testid="stButton"] button.logout {
            background-color: transparent;
            color: #DC2626;
            border: 1px solid #DC2626;
            margin-top: 15px;
        }
        div[data-testid="stButton"] button.logout:hover {
            background-color: #FEE2E2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.8em;">
        <p>© 2025 GDPR Scan Engine</p>
        <p>Secure • Compliant • Reliable</p>
    </div>
    """, unsafe_allow_html=True)

# Main content
if not st.session_state.logged_in:
    # Create a hero section with title
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.5rem;">GDPR Scan Engine</h1>
        <p style="font-size: 1.2rem; margin-bottom: 1rem;">Comprehensive GDPR compliance scanning and reporting</p>
    </div>
    """, unsafe_allow_html=True)
    
    # GDPR Compliance Images in a colorful grid
    st.markdown("<h2 style='text-align: center; margin: 1rem 0;'>GDPR Compliance Dashboard</h2>", unsafe_allow_html=True)
    
    # Add colorful GDPR compliance images
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #DBEAFE; height: 200px; text-align: center; 
                     background-image: linear-gradient(120deg, #DBEAFE, #93C5FD); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #1E40AF;">🔒 Data Protection</h3>
            <p style="color: #1E3A8A; font-weight: bold;">Compliance Score</p>
            <div style="font-size: 2rem; margin: 10px 0; color: #1E3A8A;">85%</div>
            <div style="background-color: #BFDBFE; border-radius: 10px; padding: 5px; width: 85%; margin: 0 auto;">
                <div style="background-color: #3B82F6; width: 85%; height: 10px; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #F0FDF4; height: 200px; text-align: center; 
                    background-image: linear-gradient(120deg, #F0FDF4, #86EFAC); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #166534;">🛡️ GDPR Readiness</h3>
            <p style="color: #166534; font-weight: bold;">Organization Score</p>
            <div style="font-size: 2rem; margin: 10px 0; color: #166534;">78%</div>
            <div style="background-color: #BBF7D0; border-radius: 10px; padding: 5px; width: 85%; margin: 0 auto;">
                <div style="background-color: #16A34A; width: 78%; height: 10px; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #FEF3C7; height: 200px; text-align: center; 
                    background-image: linear-gradient(120deg, #FEF3C7, #FCD34D); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #92400E;">⚠️ Risk Assessment</h3>
            <p style="color: #92400E; font-weight: bold;">Risk Mitigation</p>
            <div style="font-size: 2rem; margin: 10px 0; color: #92400E;">92%</div>
            <div style="background-color: #FDE68A; border-radius: 10px; padding: 5px; width: 85%; margin: 0 auto;">
                <div style="background-color: #F59E0B; width: 92%; height: 10px; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add app rating section
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Rate Our Application</h3>", unsafe_allow_html=True)
    
    rating_col1, rating_col2, rating_col3, rating_col4, rating_col5 = st.columns(5)
    with rating_col1:
        st.button("⭐ 1", use_container_width=True)
    with rating_col2:
        st.button("⭐⭐ 2", use_container_width=True)
    with rating_col3:
        st.button("⭐⭐⭐ 3", use_container_width=True)
    with rating_col4:
        st.button("⭐⭐⭐⭐ 4", use_container_width=True)
    with rating_col5:
        st.button("⭐⭐⭐⭐⭐ 5", use_container_width=True)
    
    feedback = st.text_area("Additional Feedback", placeholder="Share your thoughts on our GDPR Scan Engine...")
    st.button("Submit Feedback", use_container_width=True)
    
    # Show scanning services in boxes
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; margin: 2rem 0;'>Comprehensive Scanning Services</h2>", unsafe_allow_html=True)
    
    # First row of services
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #EFF6FF; height: 180px; text-align: center;">
            <h3 style="color: #1E40AF;">💻 Code Scanner</h3>
            <p style="font-size: 0.9rem;">Detect secrets & PII in source code using TruffleHog/Semgrep integration.</p>
            <p style="font-style: italic; font-size: 0.8rem; color: #4B5563;">Python + TruffleHog/Semgrep</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #EFF6FF; height: 180px; text-align: center;">
            <h3 style="color: #1E40AF;">📄 Blob Scanner</h3>
            <p style="font-size: 0.9rem;">Scan PDFs, Word docs & text files for PII with advanced OCR technology.</p>
            <p style="font-style: italic; font-size: 0.8rem; color: #4B5563;">Python + Presidio + OCR</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #EFF6FF; height: 180px; text-align: center;">
            <h3 style="color: #1E40AF;">🖼️ Image Scanner</h3>
            <p style="font-size: 0.9rem;">Analyze images for faces, text & visual identity information.</p>
            <p style="font-style: italic; font-size: 0.8rem; color: #4B5563;">Azure Vision API</p>
        </div>
        """, unsafe_allow_html=True)

    # Second row of services
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #EFF6FF; height: 180px; text-align: center;">
            <h3 style="color: #1E40AF;">🗄️ DB Scanner</h3>
            <p style="font-size: 0.9rem;">Structured database scanning for PII across tables & schemas.</p>
            <p style="font-style: italic; font-size: 0.8rem; color: #4B5563;">ADF + Python</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #EFF6FF; height: 180px; text-align: center;">
            <h3 style="color: #1E40AF;">🔌 API Scanner</h3>
            <p style="font-size: 0.9rem;">Scan API endpoints & traffic for PII exposure with NLP analysis.</p>
            <p style="font-style: italic; font-size: 0.8rem; color: #4B5563;">FastAPI + OpenAPI/NLP</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #EFF6FF; height: 180px; text-align: center;">
            <h3 style="color: #1E40AF;">🌱 Sustainability</h3>
            <p style="font-size: 0.9rem;">ESG compliance: carbon emissions, idle resources, storage bloat.</p>
            <p style="font-style: italic; font-size: 0.8rem; color: #4B5563;">Azure API + Python</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Key features section after services
    st.markdown("<h2 style='text-align: center; margin: 2rem 0;'>Key Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #DBEAFE; height: 150px; text-align: center;">
            <h3 style="color: #1E40AF;">🔍 Comprehensive Detection</h3>
            <p>Unified scanning across code, docs, images, DBs, APIs with a single orchestrated workflow.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #DBEAFE; height: 150px; text-align: center;">
            <h3 style="color: #1E40AF;">📊 Advanced Analysis</h3>
            <p>Risk scoring, compliance reporting, and remediation advice with region-specific GDPR rules.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #DBEAFE; height: 150px; text-align: center;">
            <h3 style="color: #1E40AF;">🇳🇱 Dutch GDPR Compliance</h3>
            <p>Special handling for BSN, medical data, and UAVG-specific requirements included.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # About section
    st.markdown("---")
    st.subheader("About GDPR Scan Engine")
    st.write("""
    Our GDPR Scan Engine identifies and reports on GDPR-relevant Personally Identifiable Information (PII) 
    across multiple sources, with a focus on Dutch-specific rules (UAVG), consent management, and legal 
    basis documentation.
    
    The tool fully implements all seven core GDPR principles:
    - Lawfulness, Fairness, and Transparency
    - Purpose Limitation
    - Data Minimization
    - Accuracy
    - Storage Limitation
    - Integrity and Confidentiality
    - Accountability
    """)

else:
    # Initialize aggregator
    results_aggregator = ResultsAggregator()
    
    # Navigation
    nav_options = ["Dashboard", "New Scan", "Scan History", "Reports"]
    selected_nav = st.sidebar.radio("Navigation", nav_options)
    
    if selected_nav == "Dashboard":
        st.title("GDPR Compliance Dashboard")
        
        # Summary metrics
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            total_scans = len(all_scans)
            total_pii = sum(scan.get('total_pii_found', 0) for scan in all_scans)
            high_risk_items = sum(scan.get('high_risk_count', 0) for scan in all_scans)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Scans", total_scans)
            col2.metric("Total PII Found", total_pii)
            col3.metric("High Risk Items", high_risk_items)
            
            # Recent scans
            st.subheader("Recent Scans")
            recent_scans = all_scans[-5:] if len(all_scans) > 5 else all_scans
            recent_scans_df = pd.DataFrame(recent_scans)
            if 'timestamp' in recent_scans_df.columns:
                recent_scans_df['timestamp'] = pd.to_datetime(recent_scans_df['timestamp'])
                recent_scans_df = recent_scans_df.sort_values('timestamp', ascending=False)
            
            if not recent_scans_df.empty:
                display_cols = ['scan_id', 'scan_type', 'timestamp', 'total_pii_found', 'high_risk_count', 'region']
                display_cols = [col for col in display_cols if col in recent_scans_df.columns]
                st.dataframe(recent_scans_df[display_cols])
            
                # PII Types Distribution
                st.subheader("PII Types Distribution")
                
                # Aggregate PII types from all scans
                pii_counts = {}
                for scan in all_scans:
                    if 'pii_types' in scan:
                        for pii_type, count in scan['pii_types'].items():
                            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + count
                
                if pii_counts:
                    pii_df = pd.DataFrame(list(pii_counts.items()), columns=['PII Type', 'Count'])
                    fig = px.bar(pii_df, x='PII Type', y='Count', color='PII Type')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Risk Level Distribution
                st.subheader("Risk Level Distribution")
                risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
                for scan in all_scans:
                    if 'risk_levels' in scan:
                        for risk, count in scan['risk_levels'].items():
                            if risk in risk_counts:
                                risk_counts[risk] += count
                
                risk_df = pd.DataFrame(list(risk_counts.items()), columns=['Risk Level', 'Count'])
                fig = px.pie(risk_df, values='Count', names='Risk Level', color='Risk Level',
                             color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Scan Types
                st.subheader("Scan Types")
                scan_type_counts = {}
                for scan in all_scans:
                    scan_type = scan.get('scan_type', 'Unknown')
                    scan_type_counts[scan_type] = scan_type_counts.get(scan_type, 0) + 1
                
                scan_type_df = pd.DataFrame(list(scan_type_counts.items()), columns=['Scan Type', 'Count'])
                fig = px.bar(scan_type_df, x='Scan Type', y='Count', color='Scan Type')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No scan data available yet. Start a new scan to see results.")
        else:
            st.info("No scan data available yet. Start a new scan to see results.")
    
    elif selected_nav == "New Scan":
        st.title("Start a New GDPR Scan")
        
        # Scan configuration form - expanded with all scanner types
        scan_type = st.selectbox("Scan Type", [
            "Code Scan", 
            "Document Scan", 
            "Image Scan", 
            "Database Scan",
            "API Scan", 
            "Sustainability Scan"
        ])
        region = st.selectbox("Region", list(REGIONS.keys()))
        
        # Additional configurations - customized for each scan type
        with st.expander("Advanced Configuration"):
            # Common settings
            include_comments = st.checkbox("Include Comments in Code Scan", value=True)
            
            # Scan-specific configurations
            if scan_type == "Code Scan":
                file_extensions = st.multiselect("File Extensions", 
                                               [".py", ".js", ".java", ".php", ".cs", ".go", ".rb", ".ts", ".html", ".xml", ".json"],
                                               default=[".py", ".js", ".java", ".php"])
                use_semgrep = st.checkbox("Use Semgrep for deep code analysis", value=True)
                st.checkbox("Scan for hardcoded secrets", value=True)
                
            elif scan_type == "Document Scan":
                file_types = st.multiselect("Document Types",
                                          ["PDF", "DOCX", "TXT", "CSV", "XLSX"],
                                          default=["PDF", "DOCX", "TXT"])
                st.checkbox("Use OCR for scanned documents", value=True)
                st.slider("OCR Confidence Threshold", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
                
            elif scan_type == "Image Scan":
                file_types = st.multiselect("Image Types",
                                         ["JPG", "PNG", "TIFF", "BMP", "GIF"],
                                         default=["JPG", "PNG"])
                st.checkbox("Detect faces", value=True)
                st.checkbox("Detect text (OCR)", value=True)
                st.checkbox("Detect personally identifiable visual elements", value=True)
                
            elif scan_type == "Database Scan":
                db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "MongoDB"])
                connection_string = st.text_input("Connection String (or leave empty to use environment variables)")
                st.checkbox("Include table statistics", value=True)
                st.multiselect("PII Types to Scan For", 
                             ["Email", "Phone", "Address", "Name", "ID Numbers", "Financial", "Health", "All"],
                             default=["All"])
                
            elif scan_type == "API Scan":
                api_type = st.selectbox("API Type", ["REST", "GraphQL", "SOAP", "gRPC"])
                st.text_input("API Endpoint URL")
                st.checkbox("Parse Swagger/OpenAPI docs if available", value=True)
                st.checkbox("Use NLP for endpoint analysis", value=True)
                
            elif scan_type == "Sustainability Scan":
                scan_targets = st.multiselect("Sustainability Targets",
                                            ["Carbon Emissions", "Resource Utilization", "Storage Efficiency", "Code Efficiency", "All"],
                                            default=["All"])
                st.slider("Analysis Depth", min_value=1, max_value=5, value=3)
                st.checkbox("Include remediation suggestions", value=True)
        
        # File uploader - adaptive based on scan type
        if scan_type in ["Code Scan", "Document Scan", "Image Scan"]:
            uploaded_files = st.file_uploader(
                f"Upload {scan_type.split(' ')[0]} Files", 
                accept_multiple_files=True
            )
        elif scan_type == "Database Scan":
            st.info("Database scanning does not require file uploads. Configure the database connection and scan settings above.")
            uploaded_files = []
        elif scan_type == "API Scan":
            st.info("API scanning uses the endpoint URL provided in settings. Optionally, you can upload Swagger/OpenAPI specification files.")
            uploaded_files = st.file_uploader(
                "Upload API Specification (optional)",
                accept_multiple_files=True
            )
        elif scan_type == "Sustainability Scan":
            st.info("Sustainability scanning can analyze your cloud resources directly or you can upload configuration files and code.")
            uploaded_files = st.file_uploader(
                "Upload Configuration/Code Files (optional)",
                accept_multiple_files=True
            )
        
        # Scan button with proper validation for each scan type
        if st.button("Start Scan"):
            proceed_with_scan = False
            
            if scan_type in ["Code Scan", "Document Scan", "Image Scan"] and not uploaded_files:
                st.error(f"Please upload at least one file to scan for {scan_type}.")
            elif scan_type == "Database Scan" and 'connection_string' in locals() and not connection_string and 'db_type' in locals():
                # For database scans without connection string, we'll use environment variables
                st.info(f"Starting {db_type} scan using environment variables...")
                proceed_with_scan = True
            elif scan_type == "API Scan" and 'api_type' in locals():
                # For API scans
                proceed_with_scan = True
            elif scan_type == "Sustainability Scan":
                # For sustainability scans
                proceed_with_scan = True
            else:
                proceed_with_scan = bool(uploaded_files)
                
            if proceed_with_scan:
                # Generate a unique scan ID
                scan_id = str(uuid.uuid4())
                st.session_state.current_scan_id = scan_id
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Save uploaded files to temp directory
                temp_dir = f"temp_{scan_id}"
                os.makedirs(temp_dir, exist_ok=True)
                
                file_paths = []
                for i, uploaded_file in enumerate(uploaded_files):
                    progress = (i + 1) / (2 * len(uploaded_files))
                    progress_bar.progress(progress)
                    status_text.text(f"Processing file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    # Save file
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(file_path)
                
                # Initialize scanner based on type
                if scan_type == "Code Scan":
                    scanner = CodeScanner(
                        extensions=file_extensions if 'file_extensions' in locals() else [".py", ".js", ".java", ".php"],
                        include_comments=include_comments,
                        region=region
                    )
                else:  # Document Scan
                    scanner = BlobScanner(
                        file_types=file_types if 'file_types' in locals() else ["PDF", "DOCX", "TXT"],
                        region=region
                    )
                
                # Run scan
                scan_results = []
                for i, file_path in enumerate(file_paths):
                    progress = 0.5 + (i + 1) / (2 * len(file_paths))
                    progress_bar.progress(progress)
                    status_text.text(f"Scanning file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
                    
                    try:
                        result = scanner.scan_file(file_path)
                        scan_results.append(result)
                    except Exception as e:
                        st.error(f"Error scanning {os.path.basename(file_path)}: {str(e)}")
                
                # Aggregate and save results
                timestamp = datetime.now().isoformat()
                
                # Count PIIs by type and risk level
                pii_types = {}
                risk_levels = {"Low": 0, "Medium": 0, "High": 0}
                total_pii_found = 0
                high_risk_count = 0
                
                for result in scan_results:
                    for pii_item in result.get('pii_found', []):
                        pii_type = pii_item.get('type', 'Unknown')
                        risk_level = pii_item.get('risk_level', 'Medium')
                        
                        pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
                        total_pii_found += 1
                        
                        if risk_level == "High":
                            high_risk_count += 1
                
                # Create aggregated scan result
                aggregated_result = {
                    'scan_id': scan_id,
                    'username': st.session_state.username,
                    'timestamp': timestamp,
                    'scan_type': scan_type,
                    'region': region,
                    'file_count': len(file_paths),
                    'total_pii_found': total_pii_found,
                    'high_risk_count': high_risk_count,
                    'pii_types': pii_types,
                    'risk_levels': risk_levels,
                    'detailed_results': scan_results
                }
                
                # Save to database
                results_aggregator.save_scan_result(aggregated_result)
                
                # Store in session state for immediate display
                st.session_state.scan_results = aggregated_result
                
                # Clean up temp files
                for file_path in file_paths:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
                
                # Show completion
                progress_bar.progress(1.0)
                status_text.text("Scan completed!")
                
                st.success(f"Scan completed successfully! Scan ID: {scan_id}")
                st.info("Navigate to 'Scan History' to view detailed results")
        
    elif selected_nav == "Scan History":
        st.title("Scan History")
        
        # Get all scans for the user
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            # Convert to DataFrame for display
            scans_df = pd.DataFrame(all_scans)
            if 'timestamp' in scans_df.columns:
                scans_df['timestamp'] = pd.to_datetime(scans_df['timestamp'])
                scans_df = scans_df.sort_values('timestamp', ascending=False)
            
            # Select columns to display
            display_cols = ['scan_id', 'timestamp', 'scan_type', 'region', 'file_count', 'total_pii_found', 'high_risk_count']
            display_cols = [col for col in display_cols if col in scans_df.columns]
            
            # Rename columns for better display
            display_df = scans_df[display_cols].copy()
            column_map = {
                'scan_id': 'Scan ID',
                'timestamp': 'Date & Time',
                'scan_type': 'Scan Type',
                'region': 'Region',
                'file_count': 'Files Scanned',
                'total_pii_found': 'Total PII Found',
                'high_risk_count': 'High Risk Items'
            }
            display_df.rename(columns=column_map, inplace=True)
            
            # Display scan history table
            st.dataframe(display_df, use_container_width=True)
            
            # Allow user to select a scan to view details
            selected_scan_id = st.selectbox(
                "Select a scan to view details",
                options=scans_df['scan_id'].tolist(),
                format_func=lambda x: f"{x} - {scans_df[scans_df['scan_id']==x]['timestamp'].iloc[0]} ({scans_df[scans_df['scan_id']==x]['scan_type'].iloc[0]})"
            )
            
            if selected_scan_id:
                # Get the selected scan details
                selected_scan = results_aggregator.get_scan_by_id(selected_scan_id)
                
                if selected_scan:
                    st.subheader(f"Scan Details: {selected_scan_id}")
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Scan Type", selected_scan.get('scan_type', 'N/A'))
                    col2.metric("Region", selected_scan.get('region', 'N/A'))
                    col3.metric("Files Scanned", selected_scan.get('file_count', 0))
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total PII Found", selected_scan.get('total_pii_found', 0))
                    col2.metric("High Risk Items", selected_scan.get('high_risk_count', 0))
                    timestamp = selected_scan.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    col3.metric("Date & Time", timestamp)
                    
                    # PII Types breakdown
                    if 'pii_types' in selected_scan and selected_scan['pii_types']:
                        st.subheader("PII Types Found")
                        pii_df = pd.DataFrame(list(selected_scan['pii_types'].items()), columns=['PII Type', 'Count'])
                        fig = px.bar(pii_df, x='PII Type', y='Count', color='PII Type')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Risk levels breakdown
                    if 'risk_levels' in selected_scan and selected_scan['risk_levels']:
                        st.subheader("Risk Level Distribution")
                        risk_df = pd.DataFrame(list(selected_scan['risk_levels'].items()), columns=['Risk Level', 'Count'])
                        fig = px.pie(risk_df, values='Count', names='Risk Level', color='Risk Level',
                                    color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed findings
                    if 'detailed_results' in selected_scan and selected_scan['detailed_results']:
                        st.subheader("Detailed Findings")
                        
                        # Extract all PII items from all files
                        all_pii_items = []
                        for file_result in selected_scan['detailed_results']:
                            file_name = file_result.get('file_name', 'Unknown')
                            for pii_item in file_result.get('pii_found', []):
                                pii_item['file_name'] = file_name
                                all_pii_items.append(pii_item)
                        
                        if all_pii_items:
                            # Convert to DataFrame
                            pii_items_df = pd.DataFrame(all_pii_items)
                            
                            # Select columns to display
                            cols_to_display = ['file_name', 'type', 'value', 'location', 'risk_level', 'reason']
                            cols_to_display = [col for col in cols_to_display if col in pii_items_df.columns]
                            
                            # Rename columns for better display
                            column_map = {
                                'file_name': 'File',
                                'type': 'PII Type',
                                'value': 'Value',
                                'location': 'Location',
                                'risk_level': 'Risk Level',
                                'reason': 'Reason'
                            }
                            pii_items_df = pii_items_df[cols_to_display].rename(columns=column_map)
                            
                            # Apply styling based on risk level
                            def highlight_risk(val):
                                if val == 'High':
                                    return 'background-color: #ffcccc'
                                elif val == 'Medium':
                                    return 'background-color: #ffffcc'
                                elif val == 'Low':
                                    return 'background-color: #ccffcc'
                                return ''
                            
                            # Display the styled DataFrame
                            if 'Risk Level' in pii_items_df.columns:
                                styled_df = pii_items_df.style.applymap(highlight_risk, subset=['Risk Level'])
                                st.dataframe(styled_df, use_container_width=True)
                            else:
                                st.dataframe(pii_items_df, use_container_width=True)
                        else:
                            st.info("No PII items found in this scan.")
                    
                    # Generate report button
                    if st.button("Generate PDF Report"):
                        st.session_state.current_scan_id = selected_scan_id
                        pdf_bytes = generate_report(selected_scan)
                        
                        # Create download link
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_scan_id}.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No scan history available. Start a new scan to see results here.")
    
    elif selected_nav == "Reports":
        st.title("GDPR Compliance Reports")
        
        # Get all scans
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            # Create a select box for scan selection
            scan_options = []
            for scan in all_scans:
                scan_id = scan.get('scan_id', 'Unknown')
                timestamp = scan.get('timestamp', 'Unknown')
                scan_type = scan.get('scan_type', 'Unknown')
                
                if timestamp != 'Unknown':
                    try:
                        timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                scan_options.append({
                    'scan_id': scan_id,
                    'display': f"{timestamp} - {scan_type} (ID: {scan_id})"
                })
            
            selected_scan = st.selectbox(
                "Select a scan to generate a report",
                options=range(len(scan_options)),
                format_func=lambda i: scan_options[i]['display']
            )
            
            selected_scan_id = scan_options[selected_scan]['scan_id']
            scan_data = results_aggregator.get_scan_by_id(selected_scan_id)
            
            if scan_data:
                # Report generation options
                st.subheader("Report Options")
                
                col1, col2 = st.columns(2)
                with col1:
                    include_details = st.checkbox("Include Detailed Findings", value=True)
                    include_charts = st.checkbox("Include Charts", value=True)
                
                with col2:
                    include_metadata = st.checkbox("Include Scan Metadata", value=True)
                    include_recommendations = st.checkbox("Include Recommendations", value=True)
                
                # Generate report
                if st.button("Generate Report"):
                    with st.spinner("Generating report..."):
                        pdf_bytes = generate_report(
                            scan_data,
                            include_details=include_details,
                            include_charts=include_charts,
                            include_metadata=include_metadata,
                            include_recommendations=include_recommendations
                        )
                        
                        # Create download link
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_scan_id}.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        st.success("Report generated successfully!")
                
                # Report preview (if available from a previous generation)
                if 'current_scan_id' in st.session_state and st.session_state.current_scan_id == selected_scan_id and 'pdf_bytes' in locals():
                    st.subheader("Report Preview")
                    st.write("Preview not available. Please download the report to view.")
            else:
                st.error(f"Could not find scan with ID: {selected_scan_id}")
        else:
            st.info("No scan history available to generate reports. Start a new scan first.")

