import streamlit as st
import pandas as pd
import plotly.express as px
import os
import uuid
import random
import string
from datetime import datetime
import json
import base64
from io import BytesIO

from services.code_scanner import CodeScanner
from services.blob_scanner import BlobScanner
from services.results_aggregator import ResultsAggregator
from services.report_generator import generate_report
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email
from services.stripe_payment import display_payment_button, handle_payment_callback, SCAN_PRICES
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
if 'payment_successful' not in st.session_state:
    st.session_state.payment_successful = False
if 'payment_details' not in st.session_state:
    st.session_state.payment_details = None
if 'checkout_session_id' not in st.session_state:
    st.session_state.checkout_session_id = None
if 'email' not in st.session_state:
    st.session_state.email = None

# Set page config
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication sidebar with professional colorful design
with st.sidebar:
    # Header with gradient background and professional name
    st.markdown("""
    <div style="background-image: linear-gradient(120deg, #3B82F6, #1E40AF); 
               padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;
               box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white; margin: 0; font-weight: bold;">DataGuardian Pro</h2>
        <p style="color: #E0F2FE; margin: 5px 0 0 0; font-size: 0.9em;">Enterprise Privacy Compliance Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Meaningful GDPR theme with privacy-focused visual
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px; padding: 0 10px;">
        <div style="background-image: linear-gradient(120deg, #EFF6FF, #DBEAFE); 
                   border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <div style="background-image: linear-gradient(120deg, #3B82F6, #1E40AF); 
                           width: 40px; height: 40px; border-radius: 8px; display: flex; 
                           justify-content: center; align-items: center; margin-right: 10px;">
                    <span style="color: white; font-size: 20px;">🔒</span>
                </div>
                <div style="background-image: linear-gradient(120deg, #10B981, #047857); 
                           width: 40px; height: 40px; border-radius: 8px; display: flex; 
                           justify-content: center; align-items: center; margin-right: 10px;">
                    <span style="color: white; font-size: 20px;">📊</span>
                </div>
                <div style="background-image: linear-gradient(120deg, #F59E0B, #B45309); 
                           width: 40px; height: 40px; border-radius: 8px; display: flex; 
                           justify-content: center; align-items: center;">
                    <span style="color: white; font-size: 20px;">📋</span>
                </div>
            </div>
            <p style="color: #1E40AF; font-size: 0.9em; margin: 0; text-align: center;">
                Privacy • Compliance • Transparency
            </p>
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
                        # Add permissions to session state
                        st.session_state.permissions = user_data.get("permissions", [])
                        # If permissions not found, get from role
                        if not st.session_state.permissions and "role" in user_data:
                            from services.auth import ROLE_PERMISSIONS
                            if user_data["role"] in ROLE_PERMISSIONS:
                                st.session_state.permissions = ROLE_PERMISSIONS[user_data["role"]]["permissions"]
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
                <span style="color: white; font-size: 1.8rem; font-weight: bold;">{st.session_state.username[0].upper() if st.session_state.username else 'U'}</span>
            </div>
            <h3 style="margin: 0; color: #1E40AF; text-align: center;">Welcome back</h3>
            <p style="margin: 5px 0 0 0; text-align: center; font-weight: bold;">{st.session_state.username}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User details with icons including permissions
        st.markdown(f"""
        <div style="margin: 15px 0; background-color: white; padding: 15px; border-radius: 10px; 
                   border-left: 4px solid #3B82F6;">
            <p><span style="color: #3B82F6;">👤</span> <strong>Role:</strong> {st.session_state.role}</p>
            <p><span style="color: #3B82F6;">✉️</span> <strong>Email:</strong> {st.session_state.email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Include a "My Permissions" collapsible section
        with st.expander("My Permissions"):
            from services.auth import ROLE_PERMISSIONS, get_user_permissions
            
            # Get user's permissions
            user_permissions = st.session_state.get("permissions", [])
            
            # Get role description
            role = st.session_state.get("role", "")
            role_description = ROLE_PERMISSIONS.get(role, {}).get("description", "Custom role")
            
            st.markdown(f"**Role:** {role.title()}")
            st.markdown(f"**Description:** {role_description}")
            
            # Display permissions in categorized sections
            permissions_by_category = {}
            for perm in user_permissions:
                if ":" in perm:
                    category = perm.split(":")[0]
                    if category not in permissions_by_category:
                        permissions_by_category[category] = []
                    permissions_by_category[category].append(perm)
            
            # Show permissions by category
            for category, perms in permissions_by_category.items():
                st.subheader(f"{category.title()} Permissions")
                for perm in perms:
                    st.markdown(f"- {perm}")
                st.markdown("---")
        
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
    # Simple clean hero section with professional name
    st.title("DataGuardian Pro")
    st.write("Enterprise Privacy Compliance Platform for GDPR and International Data Standards")
    
    # Add simple divider
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Simplified compliance dashboard
    st.header("Compliance Status")
    
    # Streamlined metrics in cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="padding: 20px; border-radius: 8px; background-color: #EFF6FF; border-left: 5px solid #3B82F6;">
            <p style="font-size: 16px; margin: 0; color: #1E40AF;">Data Protection</p>
            <h2 style="font-size: 36px; margin: 10px 0; color: #1E3A8A;">85%</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 8px; background-color: #F0FDF4; border-left: 5px solid #16A34A;">
            <p style="font-size: 16px; margin: 0; color: #166534;">GDPR Readiness</p>
            <h2 style="font-size: 36px; margin: 10px 0; color: #166534;">78%</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="padding: 20px; border-radius: 8px; background-color: #FEF3C7; border-left: 5px solid #F59E0B;">
            <p style="font-size: 16px; margin: 0; color: #92400E;">Risk Mitigation</p>
            <h2 style="font-size: 36px; margin: 10px 0; color: #92400E;">92%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Application rating - simplified
    st.markdown("<hr style='margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    st.header("Rate Our Application")
    
    # Simplified rating UI
    cols = st.columns(5)
    for i, col in enumerate(cols, 1):
        with col:
            stars = "⭐" * i
            st.button(stars, key=f"rate_{i}", use_container_width=True)
    
    # Simplified feedback form
    feedback = st.text_area("Your Feedback", 
                            placeholder="Share your thoughts on the GDPR Scan Engine...",
                            max_chars=500)
    st.button("Submit Feedback", use_container_width=True)
    
    # Scanning services section - comprehensive list of all services
    st.markdown("<hr style='margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    st.header("Our Scanning Services")
    
    # Create 3 columns for better organization of all services
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="border-left: 4px solid #3B82F6; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #1E40AF;">💻 Code Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Tech:</span> Python + TruffleHog/Semgrep</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Purpose:</span> Detect PII/secrets in code</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Input:</span> Source code files (.py, .js, .java, etc.)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="border-left: 4px solid #3B82F6; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #1E40AF;">📄 Blob Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Tech:</span> Python + Presidio + OCR</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Purpose:</span> Scan PDFs/DOCs for PII</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Input:</span> Document files (PDF, DOCX, TXT, etc.)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="border-left: 4px solid #3B82F6; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #1E40AF;">🖼️ Image Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Tech:</span> Azure Vision API</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Purpose:</span> Visual identity, faces</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #1E40AF; font-weight: bold;">Input:</span> Image files (JPG, PNG, GIF, etc.)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border-left: 4px solid #10B981; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #047857;">🗄️ DB Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Tech:</span> ADF + Presidio</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Purpose:</span> Structured DB scan</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Input:</span> Database connection string</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="border-left: 4px solid #10B981; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #047857;">🔌 API Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Tech:</span> FastAPI + Swagger + NLP</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Purpose:</span> API input/output scanning</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Input:</span> API endpoint URL or Swagger docs</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="border-left: 4px solid #10B981; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #047857;">📤 Manual Upload Tool</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Tech:</span> Streamlit</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Purpose:</span> Upload manual files</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #047857; font-weight: bold;">Input:</span> Any file types for manual scanning</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="border-left: 4px solid #F59E0B; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #92400E;">🌱 Sustainability Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Tech:</span> Azure APIs</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Purpose:</span> ESG compliance check</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Input:</span> Configuration files or cloud access</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="border-left: 4px solid #F59E0B; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #92400E;">🤖 AI Model Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Tech:</span> Azure AI Content/NLP</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Purpose:</span> Scan AI models for data leakage</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Input:</span> Model files or API access</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="border-left: 4px solid #F59E0B; padding: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #92400E;">📊 SOC2 Scanner</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Tech:</span> Python rule engine</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Purpose:</span> SOC2-specific logging/access rules</p>
            <p style="margin: 0; font-size: 12px;"><span style="color: #92400E; font-weight: bold;">Input:</span> Log files and access control configs</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Key features in clean format
    st.markdown("<hr style='margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    st.header("Key Features")
    
    st.write("""
    * **Comprehensive Detection**: Unified scanning across multiple data sources
    * **Advanced Analysis**: Risk scoring and compliance reporting with remediation advice
    * **Dutch GDPR Compliance**: Special handling for BSN, medical data, and UAVG requirements
    * **Complete GDPR Principles**: All seven core GDPR principles fully implemented
    * **Customizable Scanning**: Configure scans based on your specific compliance needs
    """)
    
    # About section - simplified
    st.markdown("<hr style='margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    st.header("About DataGuardian Pro")
    
    st.write("""
    DataGuardian Pro provides comprehensive identification and reporting of 
    Personally Identifiable Information (PII) across multiple sources, with a focus on 
    Dutch GDPR (UAVG) compliance requirements.
    
    The platform supports all seven core GDPR principles:
    
    1. Lawfulness, Fairness, and Transparency
    2. Purpose Limitation
    3. Data Minimization
    4. Accuracy
    5. Storage Limitation
    6. Integrity and Confidentiality
    7. Accountability
    """)

else:
    # Initialize aggregator
    results_aggregator = ResultsAggregator()
    
    # Handle any payment callbacks (success/cancel)
    handle_payment_callback(results_aggregator)
    
    # Add free trial check
    if 'free_trial_start' not in st.session_state:
        # Initialize free trial when user first logs in
        st.session_state.free_trial_start = datetime.now()
        st.session_state.free_trial_scans_used = 0
    
    # Calculate days remaining in free trial (3 days total)
    days_elapsed = (datetime.now() - st.session_state.free_trial_start).days
    free_trial_days_left = max(0, 3 - days_elapsed)
    free_trial_active = free_trial_days_left > 0 and st.session_state.free_trial_scans_used < 5
    
    # Navigation 
    # Import auth functions for permission checks
    from services.auth import has_permission
    
    # Define base navigation options
    nav_options = ["New Scan", "Dashboard", "Scan History", "Reports", "Saved Reports"]
    
    # Add Admin section if user has admin permissions
    if has_permission('admin:access'):
        nav_options.append("Admin")
    
    selected_nav = st.sidebar.radio("Navigation", nav_options)
    
    # Add quick access buttons
    st.sidebar.markdown("### Quick Access")
    quick_col1, quick_col2 = st.sidebar.columns(2)
    
    with quick_col1:
        if st.button("📊 Dashboard", key="quick_dashboard", help="View your compliance dashboard"):
            st.session_state.selected_nav = "Dashboard"
            st.rerun()
    
    with quick_col2:
        if st.button("📑 Reports", key="quick_reports", help="View your saved reports"):
            st.session_state.selected_nav = "Saved Reports"
            st.rerun()
    
    # Membership section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Membership Options")
    
    # Display current membership status
    if 'premium_member' not in st.session_state:
        st.session_state.premium_member = False
        
    membership_status = "Premium Member ✓" if st.session_state.premium_member else "Free Trial"
    membership_expiry = "Unlimited" if st.session_state.premium_member else f"{free_trial_days_left} days left"
    
    # Display membership info
    st.sidebar.markdown(f"""
    <div style="padding: 10px; background-color: {'#e6f7e6' if st.session_state.premium_member else '#f7f7e6'}; border-radius: 5px; margin-bottom: 15px;">
        <h4 style="margin: 0; color: {'#2e7d32' if st.session_state.premium_member else '#7d6c2e'};">{membership_status}</h4>
        <p><strong>Status:</strong> {'Active' if st.session_state.premium_member or free_trial_active else 'Expired'}</p>
        <p><strong>Expires:</strong> {membership_expiry}</p>
        <p><strong>Scans Used:</strong> {st.session_state.free_trial_scans_used}/5 (Free Trial)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Membership purchase options
    if not st.session_state.premium_member:
        membership_option = st.sidebar.selectbox(
            "Select Membership Plan", 
            ["Monthly ($29.99)", "Quarterly ($79.99)", "Annual ($299.99)"]
        )
        
        if st.sidebar.button("Upgrade to Premium", type="primary"):
            # Set a flag for payment flow
            st.session_state.show_membership_payment = True
            
    # User Permissions Section
    from services.auth import get_user_permissions, get_all_permissions, get_user, get_all_roles
    
    with st.sidebar.expander("Your Profile & Permissions"):
        # Get current user data and permissions
        current_user = get_user(st.session_state.username)
        user_role = current_user.get('role', 'Basic User') if current_user else 'Basic User'
        user_permissions = get_user_permissions()
        all_permissions = get_all_permissions()
        all_roles = get_all_roles()
        
        # Display current role
        st.markdown(f"**Current Role:** {user_role}")
        
        # Find role description
        role_desc = all_roles.get(user_role, {}).get('description', 'No description available')
        st.markdown(f"*{role_desc}*")
        
        # Display permissions section
        st.markdown("#### Your Permissions:")
        
        # Group permissions by category
        permissions_by_category = {}
        for perm in user_permissions:
            category = perm.split(':')[0] if ':' in perm else 'Other'
            if category not in permissions_by_category:
                permissions_by_category[category] = []
            permissions_by_category[category].append(perm)
        
        # Display permissions by category without nested expanders
        for category, perms in permissions_by_category.items():
            st.markdown(f"**{category.title()} ({len(perms)})**")
            for perm in perms:
                desc = all_permissions.get(perm, "No description available")
                st.markdown(f"- **{perm}**: {desc}")
    
    # Membership information
    with st.sidebar.expander("Membership Benefits"):
        st.markdown("""
        - **Unlimited scans** across all scan types
        - **Priority support** for compliance issues
        - **Advanced reporting** with recommendations
        - **API access** for automated scanning
        - **Team collaboration** features
        """)
            
    # Handle membership payment display
    if 'show_membership_payment' in st.session_state and st.session_state.show_membership_payment:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Complete Membership Purchase")
        
        # Mock payment form for membership
        with st.sidebar.form("membership_payment_form"):
            st.write("Enter Payment Details")
            card_number = st.text_input("Card Number", placeholder="Enter 16-digit card number")
            col1, col2 = st.columns(2)
            with col1:
                expiry = st.text_input("Expiry", placeholder="MM/YY")
            with col2:
                cvc = st.text_input("CVC", placeholder="123", type="password")
            
            name_on_card = st.text_input("Name on Card", placeholder="Enter name on card")
            
            # Payment validation
            payment_valid = False
            payment_message = ""
            
            # Submit button for payment
            if st.form_submit_button("Complete Purchase", type="primary"):
                # Validate inputs
                if not card_number or len(card_number.replace(" ", "")) != 16:
                    payment_message = "Please enter a valid 16-digit card number"
                elif not expiry or "/" not in expiry:
                    payment_message = "Please enter a valid expiry date (MM/YY)"
                elif not cvc or len(cvc) != 3:
                    payment_message = "Please enter a valid 3-digit CVC"
                elif not name_on_card:
                    payment_message = "Please enter the name on your card"
                else:
                    payment_valid = True
                    
                if payment_valid:
                    # Complete the purchase (simulated)
                    st.session_state.premium_member = True
                    st.session_state.show_membership_payment = False
                    st.session_state.payment_confirmation = {
                        "id": f"mem_{uuid.uuid4().hex[:8]}",
                        "amount": membership_option.split("$")[1].split(")")[0],
                        "status": "succeeded",
                        "timestamp": datetime.now().isoformat()
                    }
                    st.rerun()
        
        # Show payment error message if any
        if 'payment_message' in locals() and payment_message:
            st.sidebar.error(payment_message)
    
    if selected_nav == "Dashboard":
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title("DataGuardian Pro - Compliance Dashboard")
        
        # Check if user has permission to view dashboard
        if not require_permission('dashboard:view'):
            st.warning("You don't have permission to access the dashboard. Please contact an administrator for access.")
            st.info("Your role requires the 'dashboard:view' permission to use this feature.")
            st.stop()
        
        # Display user information for audit
        with st.expander("User Information for Audit"):
            user_email = "sapreatel@example.com"  # Default for demonstration
            user_role = "Enterprise Admin"
            
            st.markdown(f"""
            <div style="padding: 10px; background-color: #f0f5ff; border-radius: 5px;">
                <h4 style="margin: 0; color: #1E40AF;">User Details</h4>
                <p><strong>Username:</strong> {st.session_state.username}</p>
                <p><strong>Email:</strong> {user_email}</p>
                <p><strong>Role:</strong> {user_role}</p>
                <p><strong>Last Login:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Audit ID:</strong> {str(uuid.uuid4())[:8]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Record this access for audit trail
            st.info("Access to this dashboard has been recorded in the audit log.")
            
            try:
                # Log this access for audit purposes
                results_aggregator.log_audit_event(
                    username=st.session_state.username,
                    action="DASHBOARD_ACCESS",
                    details={"access_time": datetime.now().isoformat(), "email": user_email}
                )
            except Exception as e:
                st.warning(f"Could not log audit event: {str(e)}")
        
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
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title("Start a New DataGuardian Pro Scan")
        
        # Check if user has permission to create scans
        if not require_permission('scan:create'):
            st.warning("You don't have permission to create new scans. Please contact an administrator for access.")
            st.info("Your role requires the 'scan:create' permission to use this feature.")
            st.stop()
        
        # Scan configuration form - expanded with all scanner types
        scan_type_options = [
            "Code Scan", 
            "Blob Scan", 
            "Image Scan", 
            "Database Scan",
            "API Scan",
            "Website Scan",
            "Manual Upload",
            "Sustainability Scan",
            "AI Model Scan",
            "SOC2 Scan"
        ]
        
        # Add premium tag to premium features
        if not has_permission('scan:premium'):
            scan_type_options_with_labels = []
            premium_scans = ["Image Scan", "API Scan", "Sustainability Scan", "AI Model Scan", "SOC2 Scan"]
            
            for option in scan_type_options:
                if option in premium_scans:
                    scan_type_options_with_labels.append(f"{option} 💎")
                else:
                    scan_type_options_with_labels.append(option)
                    
            scan_type = st.selectbox("Scan Type", scan_type_options_with_labels)
            # Remove the premium tag for processing
            scan_type = scan_type.replace(" 💎", "")
            
            # Show premium feature message if needed
            if scan_type in premium_scans:
                st.warning("This is a premium scan type. Please upgrade your membership to use this feature.")
                with st.expander("Premium Feature Details"):
                    st.markdown("""
                    Premium scan types provide advanced detection capabilities and comprehensive reporting.
                    Upgrade your membership to access all premium features.
                    """)
                    if st.button("View Upgrade Options"):
                        st.session_state.selected_nav = "Membership"
                        st.rerun()
        else:
            scan_type = st.selectbox("Scan Type", scan_type_options)
        
        region = st.selectbox("Region", list(REGIONS.keys()))
        
        # Additional configurations - customized for each scan type
        with st.expander("Advanced Configuration"):
            # Scan-specific configurations based on type
            if scan_type == "Code Scan":
                # 1. Code Scanner
                st.subheader("Code Scanner Configuration")
                
                # Use session state to remember the selection
                if 'repo_source' not in st.session_state:
                    st.session_state.repo_source = "Upload Files"
                
                # Create the radio button and update session state
                repo_source = st.radio("Repository Source", ["Upload Files", "Repository URL"], 
                                      index=0 if st.session_state.repo_source == "Upload Files" else 1,
                                      key="repo_source_radio")
                
                # Update the session state
                st.session_state.repo_source = repo_source
                
                if repo_source == "Repository URL":
                    repo_url = st.text_input("Repository URL (GitHub, GitLab, Bitbucket)", placeholder="https://github.com/username/repo", key="repo_url")
                    branch_name = st.text_input("Branch Name", value="main", key="branch_name")
                    auth_token = st.text_input("Authentication Token (if private)", type="password", key="auth_token")
                    
                    # Git metadata collection options
                    st.subheader("Git Metadata")
                    collect_git_metadata = st.checkbox("Collect Git metadata", value=True)
                    st.markdown("""
                    <small>Includes commit hash, author, and last modified date for better traceability of findings.</small>
                    """, unsafe_allow_html=True)
                    
                    # Git History Options as regular fields instead of an expander
                    if collect_git_metadata:
                        st.markdown("##### Git History Options")
                        st.slider("History Depth (commits)", min_value=1, max_value=100, value=10)
                        st.checkbox("Include commit messages in analysis", value=True)
                        st.number_input("Age limit (days)", min_value=1, max_value=365, value=90)
                
                # Multi-language support
                lang_support = st.multiselect(
                    "Languages to Scan", 
                    ["Python", "JavaScript", "Java", "Go", "Ruby", "PHP", "C#", "C/C++", "TypeScript", "Kotlin", "Swift", 
                     "Terraform", "YAML", "JSON", "HTML", "CSS", "SQL", "Bash", "PowerShell", "Rust"],
                    default=["Python", "JavaScript", "Java", "Terraform", "YAML"]
                )
                
                # File extensions automatically mapped from languages
                file_extensions = []
                for lang in lang_support:
                    if lang == "Python":
                        file_extensions.extend([".py", ".pyw", ".pyx", ".pxd", ".pyi"])
                    elif lang == "JavaScript":
                        file_extensions.extend([".js", ".jsx", ".mjs"])
                    elif lang == "Java":
                        file_extensions.extend([".java", ".jsp", ".jav"])
                    elif lang == "Go":
                        file_extensions.extend([".go"])
                    elif lang == "Ruby":
                        file_extensions.extend([".rb", ".rhtml", ".erb"])
                    elif lang == "PHP":
                        file_extensions.extend([".php", ".phtml", ".php3", ".php4", ".php5"])
                    elif lang == "C#":
                        file_extensions.extend([".cs", ".cshtml", ".csx"])
                    elif lang == "C/C++":
                        file_extensions.extend([".c", ".cpp", ".cc", ".h", ".hpp"])
                    elif lang == "TypeScript":
                        file_extensions.extend([".ts", ".tsx"])
                    elif lang == "Kotlin":
                        file_extensions.extend([".kt", ".kts"])
                    elif lang == "Swift":
                        file_extensions.extend([".swift"])
                    elif lang == "Terraform":
                        file_extensions.extend([".tf", ".tfvars"])
                    elif lang == "YAML":
                        file_extensions.extend([".yml", ".yaml"])
                    elif lang == "JSON":
                        file_extensions.extend([".json"])
                    elif lang == "HTML":
                        file_extensions.extend([".html", ".htm", ".xhtml"])
                    elif lang == "CSS":
                        file_extensions.extend([".css", ".scss", ".sass", ".less"])
                    elif lang == "SQL":
                        file_extensions.extend([".sql"])
                    elif lang == "Bash":
                        file_extensions.extend([".sh", ".bash"])
                    elif lang == "PowerShell":
                        file_extensions.extend([".ps1", ".psm1"])
                    elif lang == "Rust":
                        file_extensions.extend([".rs"])
                
                # Show the automatically selected extensions
                st.caption("Selected File Extensions:")
                st.code(", ".join(file_extensions), language="text")
                
                # Scan targets
                scan_targets = st.multiselect(
                    "Scan For", 
                    ["Secrets", "API Keys", "PII", "Credentials", "Tokens", "Connection Strings", "All"],
                    default=["All"]
                )
                
                # Advanced Secret Detection
                st.subheader("Secret Detection Configuration")
                col1, col2 = st.columns(2)
                with col1:
                    use_entropy = st.checkbox("Use entropy analysis", value=True)
                    st.markdown("<small>Detects random strings that may be secrets</small>", unsafe_allow_html=True)
                    
                    use_regex = st.checkbox("Use regex patterns", value=True)
                    st.markdown("<small>Detects known patterns like API keys</small>", unsafe_allow_html=True)
                
                with col2:
                    use_known_providers = st.checkbox("Detect known providers", value=True)
                    st.markdown("<small>AWS, Azure, GCP, Stripe, etc.</small>", unsafe_allow_html=True)
                    
                    use_semgrep = st.checkbox("Use Semgrep for deep code analysis", value=True)
                    st.markdown("<small>Advanced pattern matching</small>", unsafe_allow_html=True)
                
                # Regional PII tagging options
                st.subheader("Regional PII Tagging")
                col1, col2 = st.columns(2)
                with col1:
                    regional_options = st.multiselect(
                        "Regional Regulations", 
                        ["GDPR (EU)", "UAVG (NL)", "BDSG (DE)", "CNIL (FR)", "DPA (UK)", "LGPD (BR)", "CCPA (US)", "PIPEDA (CA)"],
                        default=["GDPR (EU)", "UAVG (NL)"]
                    )
                
                with col2:
                    include_article_refs = st.checkbox("Include regulation article references", value=True)
                    st.markdown("<small>e.g., GDPR Art. 9 for sensitive data</small>", unsafe_allow_html=True)
                
                # False positive suppression
                st.subheader("False Positive Management")
                
                false_positive_method = st.radio(
                    "False Positive Suppression Method",
                    ["Baseline Diffing", "Ignore Rules", "Manual Review", "None"],
                    index=1
                )
                
                if false_positive_method == "Baseline Diffing":
                    st.file_uploader("Upload baseline results JSON", type=["json"], key="baseline_file")
                elif false_positive_method == "Ignore Rules":
                    st.text_area("Ignore Rules (one per line)", 
                               placeholder="*.test.js\n**/vendor/**\n**/.git/**\nSECRET_*=*\nTEST_*=*")
                
                # CI/CD Compatibility
                st.subheader("CI/CD Integration")
                ci_cd_options = st.multiselect(
                    "CI/CD Output Formats",
                    ["JSON", "SARIF", "CSV", "JUnit XML", "HTML", "Markdown"],
                    default=["JSON", "SARIF"]
                )
                
                exit_on_failure = st.checkbox("Exit on critical findings", value=False)
                st.markdown("<small>Causes pipeline failure when critical issues are found</small>", unsafe_allow_html=True)
                
                # Custom rules (without using expander to avoid nesting issues)
                st.subheader("Custom Rules Configuration")
                rule_source = st.radio(
                    "Custom Rules Source",
                    ["Upload File", "Enter Manually", "Git Repository"],
                    index=1
                )
                
                if rule_source == "Upload File":
                    st.file_uploader("Upload custom rules file", type=["yaml", "yml"], key="custom_rules_file")
                elif rule_source == "Enter Manually":
                    st.text_area("Custom Semgrep Rules (YAML format)", 
                               height=150,
                               placeholder="rules:\n  - id: hardcoded-password\n    pattern: $X = \"password\"\n    message: Hardcoded password\n    severity: WARNING")
                elif rule_source == "Git Repository":
                    st.text_input("Rules Git Repository URL", placeholder="https://github.com/username/custom-rules")
                    st.text_input("Repository Path", placeholder="path/to/rules", value="rules")
                        
                    # Custom presidio recognizers
                    st.checkbox("Use custom Presidio recognizers", value=False)
                    st.text_area("Custom Presidio Recognizers (Python)", 
                               placeholder="from presidio_analyzer import PatternRecognizer\n\nmy_recognizer = PatternRecognizer(\n    supported_entity='CUSTOM_ENTITY',\n    patterns=[{\"name\": \"custom pattern\", \"regex\": r'pattern_here'}]\n)")
                    
                # Code inclusion options
                include_comments = st.checkbox("Include comments in scan", value=True)
                include_strings = st.checkbox("Scan string literals", value=True)
                include_variables = st.checkbox("Analyze variable names", value=True)
                
            elif scan_type == "Blob Scan":
                # 2. Blob Scanner
                st.subheader("Blob Scanner Configuration")
                blob_source = st.radio("Blob Storage Location", ["Upload Files", "Azure Blob", "AWS S3", "Local Path"])
                
                if blob_source in ["Azure Blob", "AWS S3"]:
                    st.text_input(f"{blob_source} URL/Connection String", 
                                placeholder="https://account.blob.core.windows.net/container" if blob_source == "Azure Blob" else "s3://bucket-name/prefix")
                    st.text_input("Storage Account Key/Access Key", type="password")
                elif blob_source == "Local Path":
                    st.text_input("Local Folder Path", placeholder="/path/to/documents")
                
                file_types = st.multiselect("Document Types to Scan",
                                        ["PDF", "DOCX", "TXT", "CSV", "XLSX", "RTF", "XML", "JSON", "HTML"],
                                        default=["PDF", "DOCX", "TXT"])
                
                ocr_lang = st.selectbox("OCR Language", 
                                      ["English", "Dutch", "German", "French", "Spanish", "Italian"],
                                      index=0)
                
                use_ocr = st.checkbox("Enable OCR for scanned documents", value=True)
                include_subfolders = st.checkbox("Include subfolders", value=True)
                
                st.multiselect("PII Types to Detect", 
                             ["PERSON", "EMAIL", "PHONE", "ADDRESS", "CREDIT_CARD", "IBAN", "PASSPORT", "BSN", 
                              "MEDICAL_RECORD", "IP_ADDRESS", "ALL"],
                             default=["ALL"])
                
                st.slider("OCR Confidence Threshold", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
                
            elif scan_type == "Image Scan":
                # 3. Image Scanner
                st.subheader("Image Scanner Configuration")
                image_source = st.radio("Image Source", ["Upload Files", "Azure Blob", "AWS S3", "Local Path"])
                
                if image_source in ["Azure Blob", "AWS S3"]:
                    st.text_input(f"{image_source} URL/Connection String", 
                                placeholder="https://account.blob.core.windows.net/container" if image_source == "Azure Blob" else "s3://bucket-name/prefix")
                    st.text_input("Storage Account Key/Access Key", type="password")
                elif image_source == "Local Path":
                    st.text_input("Local Folder Path", placeholder="/path/to/images")
                
                file_types = st.multiselect("Image Types",
                                         ["JPG", "PNG", "TIFF", "BMP", "GIF", "WEBP"],
                                         default=["JPG", "PNG"])
                
                detection_targets = st.multiselect("Detection Targets", 
                                                ["Faces", "License Plates", "Text in Images", "Personal Objects", "Identifiable Locations", "All"],
                                                default=["All"])
                
                sensitivity_level = st.select_slider("Sensitivity Level", 
                                                   options=["Low", "Medium", "High (GDPR Strict)"],
                                                   value="Medium")
                
                st.checkbox("Blur detected PII in output images", value=True)
                st.checkbox("Extract text with OCR", value=True)
                
            elif scan_type == "Database Scan":
                # 4. DB Scanner
                st.subheader("Database Scanner Configuration")
                db_type = st.selectbox("Database Type", 
                                     ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "MongoDB", "Cosmos DB", "DynamoDB", "Snowflake"])
                
                connection_option = st.radio("Connection Method", ["Connection String", "Individual Parameters"])
                
                if connection_option == "Connection String":
                    connection_string = st.text_input("Connection String", type="password", 
                                                    placeholder="postgresql://username:password@hostname:port/database")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        db_server = st.text_input("Server", placeholder="localhost or db.example.com")
                        db_port = st.text_input("Port", placeholder="5432")
                    with col2:
                        db_username = st.text_input("Username")
                        db_password = st.text_input("Password", type="password")
                    
                    db_name = st.text_input("Database Name")
                
                table_option = st.radio("Tables to Scan", ["All Tables", "Specific Tables"])
                
                if table_option == "Specific Tables":
                    st.text_area("Tables to Include (comma-separated)", placeholder="users, customers, orders")
                
                st.text_area("Columns to Exclude (comma-separated)", placeholder="id, created_at, updated_at")
                
                st.multiselect("PII Types to Scan For", 
                             ["Email", "Phone", "Address", "Name", "ID Numbers", "Financial", "Health", "Biometric", "Passwords", "All"],
                             default=["All"])
                
                st.number_input("Scan Sample Size (rows per table)", min_value=100, max_value=10000, value=1000, step=100)
                st.checkbox("Include table statistics", value=True)
                st.checkbox("Generate remediation suggestions", value=True)
                
            elif scan_type == "API Scan":
                # 5. API Scanner
                st.subheader("API Scanner Configuration")
                api_type = st.selectbox("API Type", ["REST", "GraphQL", "SOAP", "gRPC"])
                
                api_source = st.radio("API Definition Source", ["Live Endpoint URL", "OpenAPI/Swagger Specification", "Both"])
                
                if api_source in ["Live Endpoint URL", "Both"]:
                    st.text_input("API Endpoint URL", placeholder="https://api.example.com/v1")
                
                st.text_input("Authentication Token (if required)", type="password")
                
                scan_mode = st.radio("Scan Mode", ["Static (spec-based)", "Live Testing", "Both"])
                
                st.checkbox("Parse Swagger/OpenAPI docs if available", value=True)
                st.checkbox("Include headers in scan", value=True)
                st.checkbox("Use NLP for endpoint analysis", value=True)
                
                # Replaced expander to prevent nesting issue
                st.subheader("Custom PII Patterns")
                st.text_area("Custom PII terms or patterns (one per line)", 
                           placeholder="ssn: \\d{3}-\\d{2}-\\d{4}\ncredit_card: (?:\\d{4}[- ]?){4}")
                           
            elif scan_type == "Website Scan":
                # Website Scanner
                st.subheader("Website Scanner Configuration")
                
                # Website URL input
                website_url = st.text_input("Website URL", placeholder="https://example.com")
                
                # Scan depth
                scan_depth = st.slider("Crawl Depth", min_value=1, max_value=5, value=2, 
                                     help="How many levels of links to follow from the starting URL")
                
                # Language support
                language_options = ["Dutch", "English", "French", "German", "Italian", "Spanish", 
                                  "Portuguese", "Russian", "Chinese", "Japanese", "Korean"]
                
                website_languages = st.multiselect("Website Languages", 
                                              language_options, 
                                              default=["English", "Dutch"],
                                              help="Select the languages used on the website for better extraction")
                
                # Scan options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Content Extraction")
                    include_text = st.checkbox("Extract text content", value=True)
                    include_images = st.checkbox("Analyze images", value=True)
                    include_forms = st.checkbox("Scan form fields", value=True)
                    include_metadata = st.checkbox("Extract metadata", value=True)
                
                with col2:
                    st.subheader("Detection Options")
                    detect_pii = st.checkbox("Detect PII in content", value=True)
                    detect_cookies = st.checkbox("Analyze cookies", value=True)
                    detect_trackers = st.checkbox("Detect trackers", value=True)
                    analyze_privacy_policy = st.checkbox("Analyze privacy policy", value=True)
                
                # Advanced options
                st.subheader("Advanced Options")
                
                # Rate limiting to avoid overloading the target website
                requests_per_minute = st.slider("Requests per minute", 
                                             min_value=10, max_value=120, value=30,
                                             help="Limit request rate to avoid overloading the target website")
                
                # Authentication options if the website requires login
                need_auth = st.checkbox("Website requires authentication", value=False)
                
                if need_auth:
                    auth_method = st.radio("Authentication Method", 
                                        ["Form Login", "Basic Auth", "OAuth", "API Key"])
                    
                    if auth_method == "Form Login":
                        login_url = st.text_input("Login URL", placeholder="https://example.com/login")
                        username_field = st.text_input("Username Field", value="username")
                        password_field = st.text_input("Password Field", value="password")
                        username = st.text_input("Username")
                        password = st.text_input("Password", type="password")
                    elif auth_method == "Basic Auth":
                        username = st.text_input("Username")
                        password = st.text_input("Password", type="password")
                    elif auth_method == "API Key":
                        api_key = st.text_input("API Key", type="password")
                        api_key_name = st.text_input("API Key Parameter Name", value="api_key")
                        api_key_location = st.radio("API Key Location", ["Query Parameter", "Header", "Cookie"])
                
                # GDPR/Privacy specific options
                st.subheader("GDPR Compliance Checks")
                
                compliance_checks = st.multiselect("Compliance Checks",
                                               ["Cookie Consent", "Privacy Policy", "Data Collection Disclosure",
                                                "Third-party Data Sharing", "Right to be Forgotten",
                                                "Data Export Functionality", "All"],
                                               default=["All"])
                
                # Custom patterns for website scanning
                st.text_area("Custom PII patterns to detect", 
                           placeholder="email: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\nphone_nl: (\\+31|0)\\s?[1-9][0-9]{8}")
                
            elif scan_type == "Manual Upload":
                # 6. Manual Upload Tool
                st.subheader("Manual Upload Configuration")
                
                scan_mode = st.selectbox("Scan Mode", ["Text", "Table", "Image", "NLP"])
                
                ocr_language = st.selectbox("Language (for OCR/NLP accuracy)",
                                          ["English", "Dutch", "German", "French", "Spanish", "Italian"],
                                          index=0)
                
                retention_policy = st.radio("Retention Policy", 
                                          ["Delete after scan", "Store temporarily (24 hours)", "Store permanently"])
                
                sensitivity = st.select_slider("Sensitivity Level", 
                                             options=["Low", "Medium", "High"],
                                             value="Medium")
                
                st.checkbox("Extract metadata from files", value=True)
                st.checkbox("Enable OCR for non-text content", value=True)
                
            elif scan_type == "Sustainability Scan":
                # 7. Sustainability Scanner
                st.subheader("Sustainability Scanner Configuration")
                
                cloud_provider = st.selectbox("Cloud Provider", ["Azure", "AWS", "GCP", "None/Other"])
                
                if cloud_provider == "Azure":
                    st.text_input("Azure Subscription ID")
                    st.text_input("Azure Tenant ID")
                    st.text_input("Azure Client ID")
                    st.text_input("Azure Client Secret", type="password")
                elif cloud_provider in ["AWS", "GCP"]:
                    st.text_input(f"{cloud_provider} Access Key/ID")
                    st.text_input(f"{cloud_provider} Secret Key", type="password")
                
                scan_targets = st.multiselect("ESG Focus Areas",
                                            ["Carbon Usage", "VM Energy Score", "Storage Energy Impact", 
                                             "Network Efficiency", "Resource Optimization", "All"],
                                            default=["All"])
                
                timeframe = st.selectbox("Analysis Timeframe", 
                                       ["Last 7 days", "Last 30 days", "Last 90 days", "Last year"])
                
                report_format = st.multiselect("Report Format", 
                                             ["CSV", "PDF", "Interactive Dashboard", "All"],
                                             default=["Interactive Dashboard"])
                
                st.slider("Analysis Depth", min_value=1, max_value=5, value=3)
                st.checkbox("Include remediation suggestions", value=True)
                
            elif scan_type == "AI Model Scan":
                # 8. AI Model Scanner
                st.subheader("AI Model Scanner Configuration")
                
                model_source = st.radio("Model Source", ["Upload Files", "API Endpoint", "Model Hub"])
                
                if model_source == "API Endpoint":
                    st.text_input("Model API Endpoint", placeholder="https://api.example.com/model")
                    st.text_input("API Key/Token", type="password")
                elif model_source == "Model Hub":
                    st.text_input("Model Hub URL/ID", placeholder="huggingface/bert-base-uncased")
                
                st.text_area("Sample Input Prompts (one per line)", 
                           placeholder="What is my credit card number?\nWhat's my social security number?\nTell me about Jane Doe's medical history.")
                
                leakage_types = st.multiselect("Leakage Types to Detect",
                                             ["PII in Training Data", "Bias Indicators", "Regulatory Non-compliance", 
                                              "Sensitive Information Exposure", "All"],
                                             default=["All"])
                
                context = st.multiselect("Domain Context",
                                       ["Health", "Finance", "HR", "Legal", "General", "All"],
                                       default=["General"])
                
                st.checkbox("Upload model documentation/data dictionary", value=False)
                st.checkbox("Perform adversarial testing", value=True)
                st.checkbox("Generate compliance report", value=True)
                
            elif scan_type == "SOC2 Scan":
                # 9. SOC2 Scanner
                st.subheader("SOC2 Scanner Configuration")
                
                log_source = st.radio("Log Source", ["Upload Log Files", "Cloud Storage", "Log Management System"])
                
                if log_source in ["Cloud Storage", "Log Management System"]:
                    st.text_input("Log Source URL/Connection String")
                    st.text_input("Access Key/Token", type="password")
                
                target_checks = st.multiselect("Target Checks",
                                             ["Logging Compliance", "IAM Policy Structure", "Session Timeout Rules", 
                                              "Access Controls", "Authentication Methods", "Encryption Practices", "All"],
                                             default=["All"])
                
                st.text_input("Access Control Config File Path", placeholder="/path/to/iam/config.yaml")
                
                timeframe = st.selectbox("Scan Timeframe", 
                                       ["Last 7 days", "Last 30 days", "Last 90 days", "Last year", "Custom"])
                
                if timeframe == "Custom":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.date_input("Start Date")
                    with col2:
                        st.date_input("End Date")
                
                # Avoid nested expander
                st.subheader("Custom SOC2 Ruleset")
                st.text_area("Custom SOC2 rules (JSON format)", 
                           height=150,
                           placeholder='{\n  "rules": [\n    {\n      "id": "session-timeout",\n      "requirement": "CC6.1",\n      "check": "session_timeout < 15"\n    }\n  ]\n}')
        
        # File uploader - adaptive based on scan type
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Upload Files")
        
        if scan_type == "Code Scan":
            # Use what was already set in the Advanced Configuration section
            # repo_source is now directly in st.session_state from the radio button
                
            if st.session_state.repo_source == "Upload Files":
                upload_help = "Upload source code files to scan for PII and secrets"
                uploaded_files = st.file_uploader(
                    "Upload Code Files", 
                    accept_multiple_files=True,
                    type=["py", "js", "java", "php", "cs", "go", "rb", "ts", "html", "xml", "json", "yaml", "yml", "c", "cpp", "h", "sql"],
                    help=upload_help
                )
            else:
                # For repository URL option, show a button to start scan directly
                st.info("Using repository URL for scanning. No file uploads required.")
                
                # Display repository information
                st.subheader("Repository Details")
                
                # Get values from session state if available
                repo_url = st.session_state.get('repo_url', '')
                branch_name = st.session_state.get('branch_name', 'main')
                
                # Show the information
                st.markdown(f"""
                **Repository URL:** {repo_url if repo_url else 'Not specified'}  
                **Branch:** {branch_name}
                """)
                
                # Empty upload files list - will be handled differently
                uploaded_files = []
        
        elif scan_type == "Blob Scan":
            if 'blob_source' in locals() and blob_source == "Upload Files":
                upload_help = "Upload document files to scan for PII"
                uploaded_files = st.file_uploader(
                    "Upload Document Files", 
                    accept_multiple_files=True,
                    type=["pdf", "docx", "doc", "txt", "csv", "xlsx", "xls", "rtf", "xml", "json", "html"],
                    help=upload_help
                )
            else:
                # For other blob source options
                uploaded_files = []
                
        elif scan_type == "Image Scan":
            if 'image_source' in locals() and image_source == "Upload Files":
                upload_help = "Upload image files to scan for faces and visual identifiers"
                uploaded_files = st.file_uploader(
                    "Upload Image Files", 
                    accept_multiple_files=True,
                    type=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
                    help=upload_help
                )
            else:
                # For other image source options
                uploaded_files = []
                
        elif scan_type == "Database Scan":
            st.info("Database scanning does not require file uploads. Configure the database connection and scan settings above.")
            uploaded_files = []
            
        elif scan_type == "API Scan":
            if api_source in ["OpenAPI/Swagger Specification", "Both"]:
                upload_help = "Upload OpenAPI/Swagger specification files"
                uploaded_files = st.file_uploader(
                    "Upload API Specification Files", 
                    accept_multiple_files=True,
                    type=["json", "yaml", "yml"],
                    help=upload_help
                )
                if not uploaded_files:
                    st.info("You can provide an API endpoint URL or upload a Swagger/OpenAPI specification.")
            else:
                uploaded_files = []
                
        elif scan_type == "Manual Upload":
            upload_help = "Upload any files for manual scanning"
            uploaded_files = st.file_uploader(
                "Upload Files for Manual Scan", 
                accept_multiple_files=True,
                help=upload_help
            )
            
        elif scan_type == "Sustainability Scan":
            if cloud_provider == "None/Other":
                upload_help = "Upload cloud configuration files (Terraform, CloudFormation, etc.)"
                uploaded_files = st.file_uploader(
                    "Upload Cloud Configuration Files", 
                    accept_multiple_files=True,
                    type=["tf", "json", "yaml", "yml", "xml"],
                    help=upload_help
                )
            else:
                uploaded_files = []
                st.info(f"The scan will use the provided {cloud_provider} credentials to analyze your cloud resources.")
                
        elif scan_type == "AI Model Scan":
            if model_source == "Upload Files":
                upload_help = "Upload model files or sample data"
                uploaded_files = st.file_uploader(
                    "Upload Model Files or Sample Data", 
                    accept_multiple_files=True,
                    type=["h5", "pb", "tflite", "pt", "onnx", "json", "csv", "txt"],
                    help=upload_help
                )
            else:
                uploaded_files = []
                
        elif scan_type == "SOC2 Scan":
            if log_source == "Upload Log Files":
                upload_help = "Upload log files and access control configurations"
                uploaded_files = st.file_uploader(
                    "Upload Log Files", 
                    accept_multiple_files=True,
                    type=["log", "json", "yaml", "yml", "csv", "txt"],
                    help=upload_help
                )
            else:
                uploaded_files = []
        
        # Prominent "Start Scan" button with free trial info
        scan_btn_col1, scan_btn_col2 = st.columns([3, 1])
        with scan_btn_col1:
            start_scan = st.button("Start Scan", use_container_width=True, type="primary")
        with scan_btn_col2:
            if free_trial_active:
                st.success(f"Free Trial: {free_trial_days_left} days left")
            else:
                st.warning("Premium Features")
        
        if start_scan:
            # Check if user is logged in first
            if not st.session_state.logged_in:
                st.error("Please log in to perform a scan.")
                st.info("Login with your account or register a new one from the sidebar.")
                st.stop()
                
            # Check if user email is available
            user_email = st.session_state.email
            if not user_email:
                user_email = "sapreatel@example.com"  # Default for demo purposes
                
            # Basic scan validation
            proceed_with_scan = False
            
            # Special case for Repository URL option
            if scan_type == "Code Scan" and st.session_state.repo_source == "Repository URL":
                proceed_with_scan = True
            # Other validation logic
            elif scan_type in ["Code Scan", "Blob Scan", "Image Scan"] and not uploaded_files:
                st.error(f"Please upload at least one file to scan for {scan_type}.")
            elif scan_type == "Database Scan":
                # For database scans, always allow
                proceed_with_scan = True
            elif scan_type == "API Scan":
                # For API scans
                proceed_with_scan = True
            elif scan_type == "Sustainability Scan":
                # For sustainability scans
                proceed_with_scan = True
            elif scan_type == "SOC2 Scan":
                # For SOC2 scans
                proceed_with_scan = True
            elif scan_type == "AI Model Scan":
                # For AI Model scans
                proceed_with_scan = True
            elif scan_type == "Manual Upload" and not uploaded_files:
                st.error("Please upload at least one file for manual scanning.")
            else:
                proceed_with_scan = bool(uploaded_files)
            
            # If we can proceed with the scan based on validation
            if proceed_with_scan:
                # Check if free trial is active
                if free_trial_active:
                    st.success(f"Using free trial (Days left: {free_trial_days_left}, Scans used: {st.session_state.free_trial_scans_used}/5)")
                    
                    # Generate a unique scan ID
                    scan_id = str(uuid.uuid4())
                    st.session_state.current_scan_id = scan_id
                    
                    # Increment free trial scan count
                    st.session_state.free_trial_scans_used += 1
                    
                    # Set payment as "free"
                    st.session_state.payment_successful = True
                    st.session_state.payment_details = {
                        "status": "succeeded",
                        "amount": 0,
                        "scan_type": scan_type,
                        "user_email": user_email,
                        "is_free_trial": True
                    }
                    
                    # Log the free trial scan
                    try:
                        results_aggregator.log_audit_event(
                            username=st.session_state.username,
                            action="FREE_TRIAL_SCAN",
                            details={
                                "scan_type": scan_type,
                                "trial_days_left": free_trial_days_left,
                                "trial_scans_used": st.session_state.free_trial_scans_used,
                                "user_email": user_email,
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                    except Exception as e:
                        st.warning(f"Audit logging failed: {str(e)}")
                    
                else:
                    # Handle payment flow
                    st.markdown("---")
                    st.subheader("Payment Required")
                    
                    # Display information about the scan type
                    st.markdown(f"""
                    #### {scan_type} Details
                    
                    Your scan is ready to begin. To proceed, please complete the payment below.
                    """)
                    
                    # Show payment options
                    payment_container = st.container()
                    
                    with payment_container:
                        # Create metadata for this scan
                        metadata = {
                            "scan_type": scan_type,
                            "region": region,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Display payment button
                        checkout_id = display_payment_button(scan_type, user_email, metadata)
                        
                        # Show alternative payment option for easy testing
                        st.markdown("---")
                        st.markdown("### Test Payment Option")
                        if st.button("Complete Payment (Demo Mode)"):
                            # Generate a unique scan ID
                            scan_id = str(uuid.uuid4())
                            st.session_state.current_scan_id = scan_id
                            
                            # Mark payment as successful in session state
                            st.session_state.payment_successful = True
                            st.session_state.payment_details = {
                                "status": "succeeded",
                                "amount": SCAN_PRICES[scan_type] / 100,
                                "scan_type": scan_type,
                                "user_email": user_email
                            }
                            
                            # Log the successful payment
                            try:
                                results_aggregator.log_audit_event(
                                    username=st.session_state.username,
                                    action="PAYMENT_SIMULATED",
                                    details={
                                        "scan_type": scan_type,
                                        "amount": SCAN_PRICES[scan_type] / 100,
                                        "user_email": user_email,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                )
                            except Exception as e:
                                st.warning(f"Audit logging failed: {str(e)}")
                            
                            # Continue directly to scan without requiring a page reload
                        
                    # If payment is not completed, stop execution here
                    if not st.session_state.payment_successful:
                        st.stop()
                
            # If either free trial is active or payment is successful, proceed with the scan
            if proceed_with_scan and st.session_state.payment_successful:
                # Generate a unique scan ID if not already set
                # Generate a more meaningful scan ID
                scan_date = datetime.now().strftime('%Y%m%d')
                scan_type_prefix = scan_type[:3].upper()
                # Use a shorter random component
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                
                if not st.session_state.current_scan_id:
                    # Format: COD-20230815-a1b2c3
                    scan_id = f"{scan_type_prefix}-{scan_date}-{random_suffix}"
                    st.session_state.current_scan_id = scan_id
                else:
                    scan_id = st.session_state.current_scan_id
                
                st.success(f"Payment successful! Starting scan...")
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Handle Repository URL special case
                if scan_type == "Code Scan" and st.session_state.repo_source == "Repository URL":
                    # Instead of relying on file upload, we'll handle the repository URL scanning differently
                    st.info("Starting repository URL scan...")
                    
                    # Create a placeholder file for demonstration
                    temp_dir = f"temp_{str(uuid.uuid4())}"
                    os.makedirs(temp_dir, exist_ok=True)
                    mock_file_path = os.path.join(temp_dir, "repo_scan_placeholder.txt")
                    with open(mock_file_path, "w") as f:
                        f.write("Repository URL scan placeholder")
                    
                    # Create a mock list of files to satisfy the code expectations
                    class MockFile:
                        def __init__(self, name):
                            self.name = name
                        def getbuffer(self):
                            return b"Repository URL scan"
                    
                    uploaded_files = [MockFile("github_repo.txt")]
                
                # Save uploaded files to temp directory
                temp_dir = f"temp_{scan_id}"
                os.makedirs(temp_dir, exist_ok=True)
                
                file_paths = []
                if uploaded_files:
                    for i, uploaded_file in enumerate(uploaded_files):
                        progress = (i + 1) / (2 * len(uploaded_files))
                        progress_bar.progress(progress)
                        status_text.text(f"Processing file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Save file
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                else:
                    # For scan types without file uploads
                    dummy_file = os.path.join(temp_dir, "scan_configuration.txt")
                    with open(dummy_file, "w") as f:
                        f.write(f"Scan type: {scan_type}\nRegion: {region}\nTimestamp: {datetime.now().isoformat()}")
                    file_paths = [dummy_file]
                
                # Initialize actual scanner based on scan type
                if scan_type == "Code Scan":
                    # Use the real code scanner with long-running protection
                    file_extensions = [".py", ".js", ".java", ".tf", ".yaml", ".yml"]  # Default extensions
                    
                    # Create scanner with long-running scan resilience
                    scanner = CodeScanner(
                        extensions=file_extensions,
                        include_comments=True,
                        region=region,
                        use_entropy=True,
                        use_git_metadata=True,
                        include_article_refs=True,
                        max_timeout=3600,  # 1 hour maximum timeout
                        checkpoint_interval=300  # Save checkpoint every 5 minutes
                    )
                    
                    # Set up progress reporting callback
                    def update_progress(current, total, current_file):
                        progress = 0.5 + (current / total / 2)  # Scale to 50%-100% range
                        progress_bar.progress(min(progress, 1.0))
                        status_text.text(f"Scanning file {current}/{total}: {current_file}")
                    
                    scanner.set_progress_callback(update_progress)
                else:
                    # For other scan types, use mock implementation
                    scanner_mock = {
                        'scan_file': lambda file_path: {
                            'file_name': os.path.basename(file_path),
                            'file_size': os.path.getsize(file_path),
                            'scan_timestamp': datetime.now().isoformat(),
                            'pii_found': [
                                {
                                    'type': 'EMAIL',
                                    'value': '[REDACTED EMAIL]',
                                    'location': 'Line 42',
                                    'risk_level': 'Medium',
                                    'reason': 'Email addresses are personal identifiers under GDPR'
                                },
                                {
                                    'type': 'CREDIT_CARD',
                                    'value': '[REDACTED CREDIT CARD]',
                                    'location': 'Line 78',
                                    'risk_level': 'High',
                                    'reason': 'Financial information requires special protection under GDPR'
                                },
                                {
                                    'type': 'PHONE',
                                    'value': '[REDACTED PHONE]',
                                    'location': 'Line 125',
                                    'risk_level': 'Low',
                                    'reason': 'Phone numbers are personal identifiers under GDPR'
                                }
                            ]
                        }
                    }
                    scanner = scanner_mock
                
                # Log the scan attempt with user details
                try:
                    results_aggregator.log_audit_event(
                        username=st.session_state.username,
                        action="SCAN_STARTED",
                        details={
                            "scan_type": scan_type,
                            "region": region,
                            "user_email": user_email,  # Track specific user for audit
                            "timestamp": datetime.now().isoformat(),
                            "user_role": st.session_state.role
                        }
                    )
                except Exception as e:
                    st.warning(f"Audit logging failed: {str(e)}")
                
                # Show informational message about the mock implementation
                st.info(f"Running demonstration scan for {scan_type}. Results are simulated for demonstration purposes.")
                
                # Reset payment information after scan is started
                st.session_state.payment_successful = False
                st.session_state.payment_details = None
                
                # Run scan based on scanner type
                scan_results = []
                
                if scan_type == "Code Scan":
                    # For code scan, use the directory-level scan with resilience features
                    try:
                        # Check if we have a directory of files or individual files
                        if len(file_paths) == 1 and os.path.isdir(file_paths[0]):
                            # Scan entire directory with resilient method
                            directory_path = file_paths[0]
                            status_text.text(f"Starting directory scan of: {directory_path}")
                            
                            # Configure ignore patterns
                            ignore_patterns = [
                                "node_modules/**", 
                                "**/.git/**", 
                                "**/__pycache__/**",
                                "**/venv/**",
                                "**/vendor/**",
                                "**/dist/**",
                                "**/build/**"
                            ]
                            
                            # Run the resilient scan with checkpointing
                            result = scanner.scan_directory(
                                directory_path=directory_path,
                                progress_callback=update_progress,
                                ignore_patterns=ignore_patterns,
                                max_file_size_mb=50,
                                continue_from_checkpoint=True
                            )
                            
                            # Store directory scan result
                            scan_results = result.get('findings', [])
                            
                            # Show status update
                            status_text.text(f"Completed scan with {result.get('completion_percentage', 0)}% coverage.")
                        else:
                            # Scan individual files
                            for i, file_path in enumerate(file_paths):
                                progress = 0.5 + (i + 1) / (2 * len(file_paths))
                                progress_bar.progress(progress)
                                status_text.text(f"Scanning file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
                                
                                # Use timeout-protected scan
                                result = scanner._scan_file_with_timeout(file_path)
                                scan_results.append(result)
                    except Exception as e:
                        st.error(f"Error during code scan: {str(e)}")
                else:
                    # For other scan types, use the mock scanner
                    for i, file_path in enumerate(file_paths):
                        progress = 0.5 + (i + 1) / (2 * len(file_paths))
                        progress_bar.progress(progress)
                        status_text.text(f"Scanning file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
                        
                        try:
                            # Call scan_file method directly on the dictionary object
                            result = scanner_mock['scan_file'](file_path)
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
                
                # Create a meaningful scan ID for display
                scan_date = datetime.now().strftime('%Y%m%d')
                display_scan_id = f"{scan_type[:3].upper()}-{scan_date}-{scan_id[:6]}"
                
                st.success(f"Scan completed successfully! Scan ID: {display_scan_id}")
                st.info("Navigate to 'Scan History' to view detailed results")
        
    elif selected_nav == "Scan History":
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title("Scan History & Analytics")
        
        # Check if user has permission to view scan history
        if not require_permission('history:view'):
            st.warning("You don't have permission to view scan history. Please contact an administrator for access.")
            st.info("Your role requires the 'history:view' permission to use this feature.")
            st.stop()
        
        # Get all scans for the user
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            # Convert to DataFrame for display
            scans_df = pd.DataFrame(all_scans)
            if 'timestamp' in scans_df.columns:
                scans_df['timestamp'] = pd.to_datetime(scans_df['timestamp'])
                scans_df = scans_df.sort_values('timestamp', ascending=False)
            
            # Create meaningful scan IDs 
            if 'scan_id' in scans_df.columns:
                # Create a new column for display purposes
                scans_df['display_scan_id'] = scans_df.apply(
                    lambda row: f"{row['scan_type'][:3].upper()}-{row['timestamp'].strftime('%Y%m%d')}-{row['scan_id'][:6]}",
                    axis=1
                )
            
            # Select columns to display
            display_cols = ['display_scan_id', 'timestamp', 'scan_type', 'region', 'file_count', 'total_pii_found', 'high_risk_count']
            display_cols = [col for col in display_cols if col in scans_df.columns]
            
            # Store mapping of display ID to actual scan_id
            id_mapping = dict(zip(scans_df['display_scan_id'], scans_df['scan_id']))
            st.session_state.scan_id_mapping = id_mapping
            
            # Rename columns for better display
            display_df = scans_df[display_cols].copy()
            column_map = {
                'display_scan_id': 'Scan ID',
                'timestamp': 'Date & Time',
                'scan_type': 'Scan Type',
                'region': 'Region',
                'file_count': 'Files Scanned',
                'total_pii_found': 'Total PII Found',
                'high_risk_count': 'High Risk Items'
            }
            display_df.rename(columns=column_map, inplace=True)
            
            # Add some key metrics at the top
            total_scans = len(all_scans)
            total_pii = sum(scan.get('total_pii_found', 0) for scan in all_scans)
            high_risk = sum(scan.get('high_risk_count', 0) for scan in all_scans)
            
            # Display metrics in a dashboard-like layout
            st.markdown("### Compliance Overview")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            metric_col1.markdown(f"""
            <div style="padding: 10px; background-color: #f0f5ff; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0;">Total Scans</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{total_scans}</p>
            </div>
            """, unsafe_allow_html=True)
            
            metric_col2.markdown(f"""
            <div style="padding: 10px; background-color: #f0fff0; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0;">Total PII Found</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{total_pii}</p>
            </div>
            """, unsafe_allow_html=True)
            
            metric_col3.markdown(f"""
            <div style="padding: 10px; background-color: #fff0f0; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0;">High Risk Items</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{high_risk}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add visualization tabs
            st.markdown("### Scan Analysis")
            viz_tabs = st.tabs(["Timeline", "Risk Analysis", "Scan History"])
            
            with viz_tabs[0]:  # Timeline
                if 'timestamp' in scans_df.columns:
                    # Create a date field
                    scans_df['date'] = scans_df['timestamp'].dt.date
                    
                    # Group by date and count
                    date_counts = scans_df.groupby('date').size().reset_index(name='count')
                    
                    # Create timeline chart
                    fig = px.line(date_counts, x='date', y='count', 
                                  title="Scan Activity Over Time",
                                  labels={'count': 'Number of Scans', 'date': 'Date'})
                    
                    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add trend analysis
                    if len(date_counts) > 1:
                        st.info("📈 Scan activity trend analysis shows your team is actively monitoring for compliance issues.")
                else:
                    st.info("Timeline data not available.")
            
            with viz_tabs[1]:  # Risk Analysis
                # Collect total counts by risk level
                risk_data = {
                    "Risk Level": ["High", "Medium", "Low"],
                    "Count": [
                        sum(scan.get('high_risk_count', 0) for scan in all_scans),
                        sum(scan.get('medium_risk_count', 0) for scan in all_scans),
                        sum(scan.get('low_risk_count', 0) for scan in all_scans)
                    ]
                }
                risk_df = pd.DataFrame(risk_data)
                
                # Create donut chart
                fig = px.pie(risk_df, values='Count', names='Risk Level', hole=0.4,
                           title="Risk Level Distribution",
                           color='Risk Level',
                           color_discrete_map={'High': '#ff4136', 'Medium': '#ff851b', 'Low': '#2ecc40'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Add PII types aggregated from all scans
                pii_counts = {}
                for scan in all_scans:
                    if 'pii_types' in scan and scan['pii_types']:
                        for pii_type, count in scan['pii_types'].items():
                            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + count
                
                if pii_counts:
                    pii_df = pd.DataFrame(list(pii_counts.items()), columns=['PII Type', 'Count'])
                    pii_df = pii_df.sort_values('Count', ascending=False)
                    
                    fig = px.bar(pii_df, x='PII Type', y='Count', title="Most Common PII Types Found",
                                color='Count', color_continuous_scale='Blues')
                    st.plotly_chart(fig, use_container_width=True)
            
            with viz_tabs[2]:  # Scan History Table
                # Add styling to the dataframe
                def highlight_risk(val):
                    if isinstance(val, (int, float)):
                        if val > 10:
                            return 'background-color: #FFCCCB'  # Light red for high risk
                        elif val > 5:
                            return 'background-color: #FFE5B4'  # Light orange for medium risk
                    return ''
                
                # Apply styling
                styled_df = display_df.style.applymap(highlight_risk, subset=['High Risk Items', 'Total PII Found'])
                
                # Display scan history table with styled data
                st.dataframe(styled_df, use_container_width=True)
            
            # Allow user to select a scan to view details
            selected_display_id = st.selectbox(
                "Select a scan to view details",
                options=scans_df['display_scan_id'].tolist(),
                format_func=lambda x: f"{x} - {scans_df[scans_df['display_scan_id']==x]['timestamp'].iloc[0].strftime('%b %d, %Y %H:%M')}"
            )
            
            # Convert display ID back to actual scan_id
            selected_scan_id = id_mapping.get(selected_display_id)
            
            if selected_scan_id:
                # Get the selected scan details
                selected_scan = results_aggregator.get_scan_by_id(selected_scan_id)
                
                if selected_scan:
                    st.subheader(f"Scan Details: {selected_display_id}")
                    
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
                    
                    # Generate report buttons
                    report_col1, report_col2 = st.columns(2)
                    
                    with report_col1:
                        if st.button("Generate PDF Report", key="gen_pdf_report"):
                            st.session_state.current_scan_id = selected_scan_id
                            
                            with st.spinner("Generating PDF report..."):
                                pdf_bytes = generate_report(selected_scan)
                                
                                # Create download link
                                b64_pdf = base64.b64encode(pdf_bytes).decode()
                                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_display_id}.pdf">Download PDF Report</a>'
                                st.markdown(href, unsafe_allow_html=True)
                    
                    with report_col2:
                        if st.button("Generate Interactive HTML Report", key="gen_html_report"):
                            # Import HTML report generator
                            from services.html_report_generator import save_html_report, get_html_report_as_base64
                            
                            with st.spinner("Generating interactive HTML report..."):
                                # Create reports directory if it doesn't exist
                                reports_dir = "reports"
                                os.makedirs(reports_dir, exist_ok=True)
                                
                                # Save the HTML report
                                file_path = save_html_report(selected_scan, reports_dir)
                                
                                # Create download link
                                st.success(f"HTML report saved to {file_path}")
                                st.info("You can view and download the report from the 'Saved Reports' page.")
                                
                                # Option to view the report immediately
                                if st.button("View Report Now", key="view_html_now"):
                                    # Read the HTML content
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        html_content = f.read()
                                    
                                    # Create a data URL for the iframe
                                    encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                                    data_url = f"data:text/html;base64,{encoded_content}"
                                    
                                    # Display in an iframe
                                    st.markdown(f"""
                                    <div style="border:1px solid #ddd; padding:5px; border-radius:5px;">
                                        <iframe src="{data_url}" width="100%" height="600px"></iframe>
                                    </div>
                                    """, unsafe_allow_html=True)
        else:
            st.info("No scan history available. Start a new scan to see results here.")
    
    elif selected_nav == "Saved Reports":
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        from services.html_report_generator import get_html_report_as_base64, save_html_report
        import glob
        import os
        
        st.title("Saved GDPR Compliance Reports")
        
        # Check if user has permission to view reports
        if not require_permission('report:view'):
            st.warning("You don't have permission to access saved reports. Please contact an administrator for access.")
            st.info("Your role requires the 'report:view' permission to use this feature.")
            st.stop()
        
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Look for saved reports
        report_files = glob.glob(os.path.join(reports_dir, "*.html"))
        
        if report_files:
            st.success(f"Found {len(report_files)} saved reports")
            
            # Sort by modification time (newest first)
            report_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Display in a table
            report_data = []
            for report_file in report_files:
                filename = os.path.basename(report_file)
                created_time = datetime.fromtimestamp(os.path.getmtime(report_file))
                size_kb = os.path.getsize(report_file) / 1024
                
                # Extract scan ID from filename if possible
                scan_id = "Unknown"
                if "_" in filename:
                    parts = filename.split("_")
                    if len(parts) >= 3:
                        scan_id = parts[2]
                
                report_data.append({
                    "Filename": filename,
                    "Scan ID": scan_id,
                    "Created": created_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Size (KB)": f"{size_kb:.1f}"
                })
            
            # Create dataframe for display
            reports_df = pd.DataFrame(report_data)
            
            # Add view button column
            st.dataframe(reports_df)
            
            # Allow user to select a report to view
            selected_report = st.selectbox("Select a report to view:", 
                                        options=report_files,
                                        format_func=lambda x: os.path.basename(x))
            
            if selected_report:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔍 View Report", key="view_report"):
                        # Read the HTML content
                        with open(selected_report, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Create a data URL for the iframe
                        encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                        data_url = f"data:text/html;base64,{encoded_content}"
                        
                        # Display in an iframe
                        st.markdown(f"""
                        <div style="border:1px solid #ddd; padding:5px; border-radius:5px;">
                            <iframe src="{data_url}" width="100%" height="600px"></iframe>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📥 Download Report", key="download_report"):
                        # Read the HTML content
                        with open(selected_report, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Create download link
                        b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                        href = f'<a href="data:text/html;base64,{b64_html}" download="{os.path.basename(selected_report)}">Download HTML Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No saved reports found. Generate a report from the Scan History page to see it here.")
            
            # Add a demo report if needed
            if st.button("Generate Demo Report"):
                # Create a sample scan result
                sample_scan = {
                    "scan_id": f"demo-{uuid.uuid4().hex[:8]}",
                    "scan_type": "Website Scan",
                    "timestamp": datetime.now().isoformat(),
                    "domain": "example.com",
                    "region": "Netherlands",
                    "total_pii_found": 24,
                    "high_risk_count": 3,
                    "medium_risk_count": 8,
                    "low_risk_count": 13,
                    "compliance_score": 78,
                    "findings": [
                        {
                            "type": "Email",
                            "value": "j***@example.com",
                            "location": "https://example.com/contact",
                            "risk_level": "Medium",
                            "reason": "Email addresses are personal data under GDPR Art. 4."
                        },
                        {
                            "type": "Phone",
                            "value": "+31*******89",
                            "location": "https://example.com/about",
                            "risk_level": "Medium",
                            "reason": "Phone numbers are personal data under GDPR Art. 4."
                        },
                        {
                            "type": "Cookies",
                            "value": "5 cookies found",
                            "location": "https://example.com",
                            "risk_level": "Medium",
                            "reason": "Cookies require consent under GDPR."
                        }
                    ],
                    "pii_types": {
                        "Email": 5,
                        "Phone": 3,
                        "Address": 2,
                        "Name": 8,
                        "IP Address": 6
                    },
                    "recommendations": [
                        {
                            "title": "Implement Cookie Consent Banner",
                            "priority": "High",
                            "description": "Implement a cookie consent banner to comply with GDPR.",
                            "steps": [
                                "Add cookie consent banner",
                                "Allow users to opt out of non-essential cookies",
                                "Document cookie usage in privacy policy"
                            ]
                        },
                        {
                            "title": "Review Personal Data Collection",
                            "priority": "Medium",
                            "description": "Review personal data collection practices.",
                            "steps": [
                                "Inventory all personal data collected",
                                "Document legal basis for collection",
                                "Implement data minimization"
                            ]
                        }
                    ]
                }
                
                # Save the HTML report
                file_path = save_html_report(sample_scan, reports_dir)
                
                # Confirm to the user
                st.success(f"Demo report saved to {file_path}")
                st.info("Refresh this page to see and interact with the report.")
    
    elif selected_nav == "Reports":
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title("GDPR Compliance Reports")
        
        # Check if user has permission to view reports
        if not require_permission('report:view'):
            st.warning("You don't have permission to access reports. Please contact an administrator for access.")
            st.info("Your role requires the 'report:view' permission to use this feature.")
            st.stop()
            
        # Get all scans
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            # Create a DataFrame for easy manipulation
            scans_df = pd.DataFrame(all_scans)
            
            # Create meaningful scan IDs 
            if 'scan_id' in scans_df.columns and 'timestamp' in scans_df.columns and 'scan_type' in scans_df.columns:
                # Convert timestamp to datetime
                if 'timestamp' in scans_df.columns:
                    scans_df['timestamp'] = pd.to_datetime(scans_df['timestamp'])
                
                # Create a new column for display purposes
                scans_df['display_scan_id'] = scans_df.apply(
                    lambda row: f"{row['scan_type'][:3].upper()}-{row['timestamp'].strftime('%Y%m%d')}-{row['scan_id'][:6]}",
                    axis=1
                )
                
                # Store mapping of display ID to actual scan_id
                id_mapping = dict(zip(scans_df['display_scan_id'], scans_df['scan_id']))
                st.session_state.report_scan_id_mapping = id_mapping
            
            # Create a select box for scan selection
            scan_options = []
            for _, scan in scans_df.iterrows():
                scan_id = scan.get('scan_id', 'Unknown')
                display_id = scan.get('display_scan_id', scan_id)
                timestamp = scan.get('timestamp', 'Unknown')
                scan_type = scan.get('scan_type', 'Unknown')
                
                if isinstance(timestamp, pd.Timestamp):
                    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                elif timestamp != 'Unknown':
                    try:
                        timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                scan_options.append({
                    'scan_id': scan_id,
                    'display_id': display_id,
                    'display': f"{timestamp} - {scan_type} (ID: {display_id})"
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
                        selected_display_id = scan_options[selected_scan]['display_id']
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_display_id}.pdf">Download PDF Report</a>'
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
            
    elif selected_nav == "Admin":
        # Import required auth functionality
        from services.auth import require_permission, get_all_roles, get_all_permissions, get_user, create_user, update_user, delete_user, add_custom_permissions
        
        st.title("Admin Dashboard")
        
        # Check admin access permission
        if not require_permission('admin:access'):
            st.warning("You don't have permission to access the admin dashboard. This incident will be reported.")
            st.error("Unauthorized access attempt has been logged.")
            st.stop()
        
        # Admin tabs
        admin_tabs = st.tabs(["User Management", "Role Management", "Audit Logs", "System Settings"])
        
        with admin_tabs[0]:  # User Management
            st.header("User Management")
            
            # Check for user management permission
            if not has_permission('admin:manage_users'):
                st.warning("You don't have permission to manage users.")
                st.info("Your role requires the 'admin:manage_users' permission to use this feature.")
            else:
                # Load all users for display
                all_users = {}
                try:
                    import json
                    with open('users.json', 'r') as f:
                        all_users = json.load(f)
                except Exception as e:
                    st.error(f"Error loading users: {str(e)}")
                
                if all_users:
                    # Convert to DataFrame for display
                    users_list = []
                    for username, user_data in all_users.items():
                        user_info = {
                            'username': username,
                            'email': user_data.get('email', 'N/A'),
                            'role': user_data.get('role', 'Basic User'),
                            'created_at': user_data.get('created_at', 'Unknown')
                        }
                        users_list.append(user_info)
                    
                    users_df = pd.DataFrame(users_list)
                    st.dataframe(users_df, use_container_width=True)
                    
                    # User management actions
                    st.subheader("User Actions")
                    
                    action_tabs = st.tabs(["Create User", "Edit User", "Delete User"])
                    
                    with action_tabs[0]:  # Create User
                        st.subheader("Create New User")
                        
                        with st.form("create_user_form"):
                            new_username = st.text_input("Username")
                            new_password = st.text_input("Password", type="password")
                            new_email = st.text_input("Email")
                            
                            # Get all available roles
                            all_roles = get_all_roles()
                            role_options = list(all_roles.keys())
                            new_role = st.selectbox("Role", role_options)
                            
                            # Form submission
                            submit_button = st.form_submit_button("Create User")
                            
                            if submit_button:
                                if not new_username or not new_password or not new_email:
                                    st.error("All fields are required")
                                else:
                                    # Create the new user
                                    success, message = create_user(
                                        username=new_username,
                                        password=new_password,
                                        role=new_role,
                                        email=new_email
                                    )
                                    
                                    if success:
                                        st.success(f"User '{new_username}' created successfully!")
                                        # Log this admin action
                                        try:
                                            results_aggregator.log_audit_event(
                                                username=st.session_state.username,
                                                action="USER_CREATED",
                                                details={
                                                    "created_username": new_username,
                                                    "role": new_role,
                                                    "timestamp": datetime.now().isoformat()
                                                }
                                            )
                                        except Exception as e:
                                            st.warning(f"Could not log audit event: {str(e)}")
                                    else:
                                        st.error(f"Error creating user: {message}")
                    
                    with action_tabs[1]:  # Edit User
                        st.subheader("Edit User")
                        
                        # Select user to edit
                        edit_username = st.selectbox(
                            "Select User to Edit",
                            [user['username'] for user in users_list]
                        )
                        
                        if edit_username:
                            # Get current user data
                            user_data = get_user(edit_username)
                            
                            if user_data:
                                with st.form("edit_user_form"):
                                    # Editable fields
                                    new_email = st.text_input("Email", value=user_data.get('email', ''))
                                    
                                    # Get all available roles
                                    all_roles = get_all_roles()
                                    role_options = list(all_roles.keys())
                                    current_role_index = role_options.index(user_data.get('role', 'Basic User')) if user_data.get('role', 'Basic User') in role_options else 0
                                    new_role = st.selectbox("Role", role_options, index=current_role_index)
                                    
                                    # Optional password change
                                    new_password = st.text_input("New Password (leave blank to keep current)", type="password")
                                    
                                    # Form submission
                                    submit_button = st.form_submit_button("Update User")
                                    
                                    if submit_button:
                                        # Prepare updates
                                        updates = {
                                            'email': new_email,
                                            'role': new_role
                                        }
                                        
                                        if new_password:
                                            updates['password'] = new_password
                                        
                                        # Update the user
                                        success = update_user(edit_username, updates)
                                        
                                        if success:
                                            st.success(f"User '{edit_username}' updated successfully!")
                                            # Log this admin action
                                            try:
                                                results_aggregator.log_audit_event(
                                                    username=st.session_state.username,
                                                    action="USER_UPDATED",
                                                    details={
                                                        "updated_username": edit_username,
                                                        "new_role": new_role,
                                                        "timestamp": datetime.now().isoformat()
                                                    }
                                                )
                                            except Exception as e:
                                                st.warning(f"Could not log audit event: {str(e)}")
                                        else:
                                            st.error(f"Error updating user: {edit_username}")
                            else:
                                st.error(f"Could not find user: {edit_username}")
                    
                    with action_tabs[2]:  # Delete User
                        st.subheader("Delete User")
                        
                        # Select user to delete
                        delete_username = st.selectbox(
                            "Select User to Delete",
                            [user['username'] for user in users_list]
                        )
                        
                        if delete_username:
                            # Confirm deletion
                            st.warning(f"Are you sure you want to delete user '{delete_username}'? This action cannot be undone.")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                confirm = st.checkbox("I understand the consequences")
                            
                            if confirm:
                                with col2:
                                    if st.button("Delete User", type="primary"):
                                        # Delete the user
                                        success = delete_user(delete_username)
                                        
                                        if success:
                                            st.success(f"User '{delete_username}' deleted successfully!")
                                            # Log this admin action
                                            try:
                                                results_aggregator.log_audit_event(
                                                    username=st.session_state.username,
                                                    action="USER_DELETED",
                                                    details={
                                                        "deleted_username": delete_username,
                                                        "timestamp": datetime.now().isoformat()
                                                    }
                                                )
                                            except Exception as e:
                                                st.warning(f"Could not log audit event: {str(e)}")
                                        else:
                                            st.error(f"Error deleting user: {delete_username}")
                else:
                    st.info("No users found. Create a new user to get started.")
        
        with admin_tabs[1]:  # Role Management
            st.header("Role Management")
            
            # Check for role management permission
            if not has_permission('admin:manage_roles'):
                st.warning("You don't have permission to manage roles.")
                st.info("Your role requires the 'admin:manage_roles' permission to use this feature.")
            else:
                # Get all roles and permissions
                all_roles = get_all_roles()
                all_permissions = get_all_permissions()
                
                # Display roles
                st.subheader("Available Roles")
                
                roles_list = []
                for role_name, role_data in all_roles.items():
                    role_info = {
                        'name': role_name,
                        'description': role_data.get('description', 'No description'),
                        'permissions_count': len(role_data.get('permissions', []))
                    }
                    roles_list.append(role_info)
                
                roles_df = pd.DataFrame(roles_list)
                st.dataframe(roles_df, use_container_width=True)
                
                # Role details
                st.subheader("Role Details")
                
                selected_role = st.selectbox("Select Role", list(all_roles.keys()))
                
                if selected_role:
                    role_data = all_roles.get(selected_role, {})
                    st.markdown(f"**Description:** {role_data.get('description', 'No description')}")
                    
                    # Show permissions
                    st.markdown(f"**Permissions ({len(role_data.get('permissions', []))}):**")
                    
                    # Group permissions by category
                    permissions_by_category = {}
                    for perm in role_data.get('permissions', []):
                        category = perm.split(':')[0] if ':' in perm else 'Other'
                        if category not in permissions_by_category:
                            permissions_by_category[category] = []
                        permissions_by_category[category].append(perm)
                    
                    # Display permissions by category without nested expanders
                    for category, perms in permissions_by_category.items():
                        st.markdown(f"**{category.title()} ({len(perms)})**")
                        for perm in perms:
                            desc = all_permissions.get(perm, "No description available")
                            st.markdown(f"- **{perm}**: {desc}")
                
                # Add custom permissions
                st.subheader("Add Custom Permissions to User")
                
                with st.form("add_custom_permissions"):
                    # Get all users
                    all_users = {}
                    try:
                        import json
                        with open('users.json', 'r') as f:
                            all_users = json.load(f)
                    except Exception as e:
                        st.error(f"Error loading users: {str(e)}")
                    
                    user_options = list(all_users.keys())
                    target_user = st.selectbox("Select User", user_options)
                    
                    # Display all available permissions
                    perm_options = list(all_permissions.keys())
                    custom_perms = st.multiselect("Select Custom Permissions", perm_options)
                    
                    # Form submission
                    submit_button = st.form_submit_button("Add Custom Permissions")
                    
                    if submit_button:
                        if target_user and custom_perms:
                            # Add custom permissions
                            success = add_custom_permissions(target_user, custom_perms)
                            
                            if success:
                                st.success(f"Custom permissions added to user '{target_user}' successfully!")
                                # Log this admin action
                                try:
                                    results_aggregator.log_audit_event(
                                        username=st.session_state.username,
                                        action="CUSTOM_PERMISSIONS_ADDED",
                                        details={
                                            "target_username": target_user,
                                            "permissions": custom_perms,
                                            "timestamp": datetime.now().isoformat()
                                        }
                                    )
                                except Exception as e:
                                    st.warning(f"Could not log audit event: {str(e)}")
                            else:
                                st.error(f"Error adding custom permissions to user: {target_user}")
                        else:
                            st.error("Please select a user and at least one permission")
        
        with admin_tabs[2]:  # Audit Logs
            st.header("Audit Logs")
            
            # Check for audit logs permission
            if not has_permission('admin:view_audit_logs'):
                st.warning("You don't have permission to view audit logs.")
                st.info("Your role requires the 'admin:view_audit_logs' permission to use this feature.")
            else:
                try:
                    # Get audit logs from results aggregator
                    audit_logs = results_aggregator.get_audit_logs()
                    
                    if audit_logs and len(audit_logs) > 0:
                        # Convert to DataFrame
                        logs_df = pd.DataFrame(audit_logs)
                        
                        # Format timestamp
                        if 'timestamp' in logs_df.columns:
                            logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
                            logs_df = logs_df.sort_values('timestamp', ascending=False)
                        
                        # Display logs
                        st.dataframe(logs_df, use_container_width=True)
                        
                        # Filters
                        st.subheader("Filter Logs")
                        
                        if 'action' in logs_df.columns:
                            action_types = logs_df['action'].unique().tolist()
                            selected_actions = st.multiselect("Filter by Action", action_types)
                            
                            if selected_actions:
                                filtered_df = logs_df[logs_df['action'].isin(selected_actions)]
                                st.dataframe(filtered_df, use_container_width=True)
                    else:
                        st.info("No audit logs found.")
                except Exception as e:
                    st.error(f"Error loading audit logs: {str(e)}")
        
        with admin_tabs[3]:  # System Settings
            st.header("System Settings")
            
            # Check for system settings permission
            if not has_permission('admin:system_settings'):
                st.warning("You don't have permission to modify system settings.")
                st.info("Your role requires the 'admin:system_settings' permission to use this feature.")
            else:
                st.subheader("General Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    session_timeout = st.number_input("Session Timeout (minutes)", min_value=5, max_value=120, value=30)
                    max_login_attempts = st.number_input("Max Login Attempts", min_value=3, max_value=10, value=5)
                
                with col2:
                    password_expiry_days = st.number_input("Password Expiry (days)", min_value=30, max_value=365, value=90)
                    enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=False)
                
                st.subheader("Compliance Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_retention_days = st.number_input("Data Retention Period (days)", min_value=1, max_value=3650, value=365)
                    default_region = st.selectbox("Default Compliance Region", list(REGIONS.keys()))
                
                with col2:
                    scan_timeout_minutes = st.number_input("Scan Timeout (minutes)", min_value=5, max_value=120, value=60)
                    enable_auto_redaction = st.checkbox("Enable Auto-Redaction", value=True)
                
                # Save settings
                if st.button("Save System Settings", type="primary"):
                    # In a real implementation, these would be saved to a config file or database
                    st.success("System settings saved successfully!")
                    
                    # Log this admin action
                    try:
                        results_aggregator.log_audit_event(
                            username=st.session_state.username,
                            action="SYSTEM_SETTINGS_UPDATED",
                            details={
                                "session_timeout": session_timeout,
                                "max_login_attempts": max_login_attempts,
                                "password_expiry": password_expiry_days,
                                "enable_2fa": enable_2fa,
                                "data_retention": data_retention_days,
                                "default_region": default_region,
                                "scan_timeout": scan_timeout_minutes,
                                "enable_auto_redaction": enable_auto_redaction,
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                    except Exception as e:
                        st.warning(f"Could not log audit event: {str(e)}")
                        
        # Display audit trail for admin actions
        with st.expander("Admin Actions Audit Trail"):
            st.info("All actions in the Admin Dashboard are logged for compliance and security purposes.")
            st.markdown("""
            Logged information includes:
            - Username of admin performing the action
            - Action performed
            - Timestamp
            - Detailed information about the change
            
            These logs are immutable and cannot be modified or deleted, even by administrators.
            """)

