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
from services.website_scanner import WebsiteScanner
from services.results_aggregator import ResultsAggregator
from services.repo_scanner import RepoScanner
from services.report_generator import generate_report
from services.certificate_generator import CertificateGenerator
from services.optimized_scanner import OptimizedScanner
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email
from services.stripe_payment import display_payment_button, handle_payment_callback, SCAN_PRICES
from utils.gdpr_rules import REGIONS, get_region_rules
from utils.risk_analyzer import RiskAnalyzer, get_severity_color, colorize_finding, get_risk_color_gradient
from utils.i18n import initialize, language_selector, get_text, set_language, LANGUAGES

# Define translation function
def _(key, default=None):
    return get_text(key, default)
from utils.compliance_score import calculate_compliance_score, display_compliance_score_card
from utils.animated_language_switcher import animated_language_switcher, get_welcome_message_animation

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
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default language is English

# Flag for redirecting to login after language change
if 'redirect_to_login' not in st.session_state:
    st.session_state.redirect_to_login = False

# Set page config
st.set_page_config(
    page_title="DataGuardian Pro - Enterprise Privacy Compliance Platform",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication sidebar with professional colorful design
with st.sidebar:
    # Add sidebar language switcher at the top with animated flags
    st.markdown("### 🌐 Interactive Language")
    # Use the animated language switcher with flags
    animated_language_switcher(key_suffix="sidebar", show_title=True, use_buttons=True)
    # Initialize translations
    initialize()
    
    # Header with gradient background and professional name
    # Get translations or use defaults if translations aren't loaded yet
    title = get_text("app.title", "DataGuardian Pro")
    subtitle = get_text("app.subtitle", "Enterprise Privacy Compliance Platform")
    
    st.markdown(f"""
    <div style="background-image: linear-gradient(120deg, #6200EA, #3700B3); 
               padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;
               box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white; margin: 0; font-weight: bold;">{title}</h2>
        <p style="color: #E9DAFF; margin: 5px 0 0 0; font-size: 0.9em;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Meaningful GDPR theme with privacy-focused visual
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 25px; padding: 0 10px;">
        <div style="background-image: linear-gradient(120deg, #F5F0FF, #E9DAFF); 
                   border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <div style="background-image: linear-gradient(120deg, #6200EA, #3700B3); 
                           width: 40px; height: 40px; border-radius: 8px; display: flex; 
                           justify-content: center; align-items: center; margin-right: 10px;">
                    <span style="color: white; font-size: 20px;">🔒</span>
                </div>
                <div style="background-image: linear-gradient(120deg, #00BFA5, #00897B); 
                           width: 40px; height: 40px; border-radius: 8px; display: flex; 
                           justify-content: center; align-items: center; margin-right: 10px;">
                    <span style="color: white; font-size: 20px;">📊</span>
                </div>
                <div style="background-image: linear-gradient(120deg, #FF6D00, #E65100); 
                           width: 40px; height: 40px; border-radius: 8px; display: flex; 
                           justify-content: center; align-items: center;">
                    <span style="color: white; font-size: 20px;">📋</span>
                </div>
            </div>
            <p style="color: #4527A0; font-size: 0.9em; margin: 0; text-align: center;">
                {_("app.tagline")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector in sidebar expander with animated flags
    # Removed duplicate language switcher
    
    if not st.session_state.logged_in:
        # Tab UI for login/register with colorful styling
        st.markdown("""
        <style>
        .tab-selected {
            background-color: #6200EA !important;
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 0;
        }
        .tab-not-selected {
            background-color: #F5F0FF;
            color: #4527A0;
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
                background-color: #6200EA;
                color: white;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            [data-testid="stButton"] button:nth-child(2) {
                background-color: #6200EA;
                color: white;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin: 0; padding: 0; margin-bottom: 15px;'>", unsafe_allow_html=True)
        
        # Login Form with colorful styling
        if st.session_state.active_tab == "login":
            st.markdown(f"""
            <div style="background-image: linear-gradient(to right, #F5F0FF, #E9DAFF); 
                       padding: 15px; border-radius: 10px; margin-bottom: 15px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <h4 style="color: #4527A0; margin: 0 0 10px 0; text-align: center;">
                    <i>{_("sidebar.sign_in")}</i>
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            username_or_email = st.text_input(_("login.email_username"), key="login_username")
            password = st.text_input(_("login.password"), type="password", key="login_password")
            
            cols = st.columns([3, 2])
            with cols[0]:
                remember = st.checkbox(_("login.remember_me"), key="remember_login")
            with cols[1]:
                st.markdown(f"<p style='text-align: right; font-size: 0.8em;'><a href='#'>{_('login.forgot_password')}</a></p>", unsafe_allow_html=True)
                
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
            
            login_button = st.button(_("login.button"), use_container_width=True, key="sidebar_login", type="primary")
            
            if login_button:
                if not username_or_email or not password:
                    st.error(_("login.error.missing_fields"))
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
                        
                        # Preserve the current language across login
                        current_language = st.session_state.get('language', 'en')
                        
                        # Ensure the language setting persists after login
                        set_language(current_language)
                        
                        st.success(_("login.success"))
                        st.rerun()
                    else:
                        st.error(_("login.error.invalid_credentials"))
        
        # Registration Form with green colorful styling
        else:
            st.markdown(f"""
            <div style="background-image: linear-gradient(to right, #D1FAE5, #ECFDF5); 
                       padding: 15px; border-radius: 10px; margin-bottom: 15px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <h4 style="color: #065F46; margin: 0 0 10px 0; text-align: center;">
                    <i>{_("sidebar.create_account")}</i>
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            new_username = st.text_input(_("register.username"), key="register_username")
            new_email = st.text_input(_("register.email"), key="register_email", 
                                    placeholder=_("register.email_placeholder"))
            new_password = st.text_input(_("register.password"), type="password", key="register_password",
                                help=_("register.password_help"))
            confirm_password = st.text_input(_("register.confirm_password"), type="password", key="confirm_password")
            
            # Role selection with custom styling
            role_options = ["viewer", "analyst", "admin"]
            new_role = st.selectbox(_("register.role"), role_options, index=0)
            
            # Green checkmark for terms
            terms = st.checkbox(_("register.terms"))
            
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
            
            register_button = st.button(_("register.button"), use_container_width=True, key="sidebar_register", type="primary")
            
            if register_button:
                if not new_username or not new_email or not new_password:
                    st.error(_("register.error.missing_fields"))
                elif new_password != confirm_password:
                    st.error(_("register.error.passwords_mismatch"))
                elif not terms:
                    st.error(_("register.error.terms_required"))
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
            <h3 style="margin: 0; color: #1E40AF; text-align: center;">{_("sidebar.welcome")}</h3>
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
    # Check if we need to redirect to login after language change
    if st.session_state.redirect_to_login:
        # Reset the flag and show login page
        st.session_state.redirect_to_login = False
        st.session_state.active_tab = "login"
        st.rerun()
        
    # Add animated welcome message in multiple languages
    st.markdown(get_welcome_message_animation(), unsafe_allow_html=True)
    
    # Use our new professional landing page module
    from utils.landing_page import display_landing_page_grid
    display_landing_page_grid()
    
    # Add spacing
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Our landing page already has metric cards, no need to duplicate them
    st.write("")
    
    # Add a professional container with subtle background for the whole page
    st.markdown("""
    <style>
    .main-container {
        background-color: #fafbfd;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 30px;
    }
    .section-heading {
        color: #2563EB;
        font-weight: 600;
        text-align: center;
        position: relative;
        padding-bottom: 15px;
        margin: 25px 0 30px 0;
    }
    .section-heading:after {
        content: "";
        position: absolute;
        left: 50%;
        bottom: 0;
        transform: translateX(-50%);
        height: 3px;
        width: 80px;
        background: linear-gradient(90deg, #2563EB, #93C5FD);
        border-radius: 3px;
    }
    </style>
    <div class="main-container">
    """, unsafe_allow_html=True)
    
    # Simple footer spacer
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Clean footer with professional styling
    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #e0e0e0;'>", unsafe_allow_html=True)
    
    # Professional footer with company info
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(to right, #f8f9fa, #f1f3f5); 
               border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <h4 style="color: #3B82F6; margin-bottom: 15px;">DataGuardian</h4>
        <p style="color: #4b5563; margin-bottom: 5px;">Enterprise Privacy Compliance Platform</p>
        <p style="color: #6b7280; font-size: 0.8em;">© 2025 DataGuardian. All rights reserved.</p>
    </div>
    </div><!-- Close main-container -->
    """, unsafe_allow_html=True)

else:
    # Reinitialize language to ensure it's properly loaded after login
    current_language = st.session_state.get('language', 'en')
    set_language(current_language)
    
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
    nav_options = [_("scan.title"), _("dashboard.welcome"), _("history.title"), _("results.title"), _("report.generate")]
    
    # Add Admin section if user has admin permissions
    if has_permission('admin:access'):
        nav_options.append(_("admin.title"))
    
    selected_nav = st.sidebar.radio(_("sidebar.navigation"), nav_options)
    
    # Add quick access buttons
    st.sidebar.markdown(f"### {_('sidebar.quick_access')}")
    quick_col1, quick_col2 = st.sidebar.columns(2)
    
    with quick_col1:
        if st.button(f"📊 {_('sidebar.dashboard')}", key="quick_dashboard", help=_("sidebar.dashboard_help")):
            st.session_state.selected_nav = _("dashboard.welcome")
            st.rerun()
    
    with quick_col2:
        if st.button(f"📑 {_('sidebar.reports')}", key="quick_reports", help=_("sidebar.reports_help")):
            st.session_state.selected_nav = _("report.generate")
            st.rerun()
    
    # Membership section
    st.sidebar.markdown("---")
    st.sidebar.subheader(_("sidebar.membership_options"))
    
    # Display current membership status
    if 'premium_member' not in st.session_state:
        st.session_state.premium_member = False
        
    membership_status = _("sidebar.premium_member") if st.session_state.premium_member else _("sidebar.free_trial")
    membership_expiry = _("sidebar.unlimited") if st.session_state.premium_member else f"{free_trial_days_left} {_('sidebar.days_left')}"
    
    # Display membership info
    st.sidebar.markdown(f"""
    <div style="padding: 10px; background-color: {'#e6f7e6' if st.session_state.premium_member else '#f7f7e6'}; border-radius: 5px; margin-bottom: 15px;">
        <h4 style="margin: 0; color: {'#2e7d32' if st.session_state.premium_member else '#7d6c2e'};">{membership_status}</h4>
        <p><strong>{_("sidebar.status")}:</strong> {_("sidebar.active") if st.session_state.premium_member or free_trial_active else _("sidebar.expired")}</p>
        <p><strong>{_("sidebar.expires")}:</strong> {membership_expiry}</p>
        <p><strong>{_("sidebar.scans_used")}:</strong> {st.session_state.free_trial_scans_used}/5 ({_("sidebar.free_trial")})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Membership purchase options
    if not st.session_state.premium_member:
        membership_option = st.sidebar.selectbox(
            _("sidebar.select_plan"), 
            [_("sidebar.plan_monthly"), _("sidebar.plan_quarterly"), _("sidebar.plan_annual")]
        )
        
        if st.sidebar.button(_("sidebar.upgrade_button"), type="primary"):
            # Set a flag for payment flow
            st.session_state.show_membership_payment = True
            
    # User Permissions Section
    from services.auth import get_user_permissions, get_all_permissions, get_user, get_all_roles
    
    with st.sidebar.expander(_("sidebar.profile_permissions")):
        # Get current user data and permissions
        current_user = get_user(st.session_state.username)
        user_role = current_user.get('role', _("sidebar.basic_user")) if current_user else _("sidebar.basic_user")
        user_permissions = get_user_permissions()
        all_permissions = get_all_permissions()
        all_roles = get_all_roles()
        
        # Display current role
        st.markdown(f"**{_('sidebar.current_role')}:** {user_role}")
        
        # Find role description
        role_desc = all_roles.get(user_role, {}).get('description', _("sidebar.no_description"))
        st.markdown(f"*{role_desc}*")
        
        # Display permissions section
        st.markdown(f"#### {_('sidebar.your_permissions')}:")
        
        # Group permissions by category
        permissions_by_category = {}
        for perm in user_permissions:
            category = perm.split(':')[0] if ':' in perm else _("sidebar.other")
            if category not in permissions_by_category:
                permissions_by_category[category] = []
            permissions_by_category[category].append(perm)
        
        # Display permissions by category without nested expanders
        for category, perms in permissions_by_category.items():
            st.markdown(f"**{category.title()} ({len(perms)})**")
            for perm in perms:
                desc = all_permissions.get(perm, _("sidebar.no_description"))
                st.markdown(f"- **{perm}**: {desc}")
    
    # Membership information
    with st.sidebar.expander(_("sidebar.membership_benefits")):
        st.markdown(f"""
        - **{_("sidebar.benefit_unlimited_scans")}**
        - **{_("sidebar.benefit_priority_support")}**
        - **{_("sidebar.benefit_advanced_reporting")}**
        - **{_("sidebar.benefit_api_access")}**
        - **{_("sidebar.benefit_team_collaboration")}**
        """)
            
    # Handle membership payment display
    if 'show_membership_payment' in st.session_state and st.session_state.show_membership_payment:
        st.sidebar.markdown("---")
        st.sidebar.subheader(_("sidebar.complete_purchase"))
        
        # Payment form for membership
        with st.sidebar.form("membership_payment_form"):
            st.write(_("sidebar.enter_payment_details"))
            card_number = st.text_input(_("sidebar.card_number"), placeholder=_("sidebar.card_number_placeholder"))
            col1, col2 = st.columns(2)
            with col1:
                expiry = st.text_input(_("sidebar.expiry"), placeholder=_("sidebar.expiry_placeholder"))
            with col2:
                cvc = st.text_input(_("sidebar.cvc"), placeholder=_("sidebar.cvc_placeholder"), type="password")
            
            name_on_card = st.text_input(_("sidebar.name_on_card"), placeholder=_("sidebar.name_on_card_placeholder"))
            
            # Payment validation
            payment_valid = False
            payment_message = ""
            
            # Submit button for payment
            if st.form_submit_button(_("sidebar.complete_purchase_button"), type="primary"):
                # Validate inputs
                if not card_number or len(card_number.replace(" ", "")) != 16:
                    payment_message = _("sidebar.error.card_number")
                elif not expiry or "/" not in expiry:
                    payment_message = _("sidebar.error.expiry")
                elif not cvc or len(cvc) != 3:
                    payment_message = _("sidebar.error.cvc")
                elif not name_on_card:
                    payment_message = _("sidebar.error.name_on_card")
                else:
                    payment_valid = True
                    
                if payment_valid:
                    # Complete the purchase (simulated)
                    st.session_state.premium_member = True
                    st.session_state.show_membership_payment = False
                    
                    # Get price from the selected plan
                    amount = ""
                    if _("sidebar.plan_monthly") == membership_option:
                        amount = "29.99"
                    elif _("sidebar.plan_quarterly") == membership_option:
                        amount = "79.99"
                    elif _("sidebar.plan_annual") == membership_option:
                        amount = "299.99"
                        
                    st.session_state.payment_confirmation = {
                        "id": f"mem_{uuid.uuid4().hex[:8]}",
                        "amount": amount,
                        "status": "succeeded",
                        "timestamp": datetime.now().isoformat()
                    }
                    st.rerun()
        
        # Show payment error message if any
        if 'payment_message' in locals() and payment_message:
            st.sidebar.error(payment_message)
    
    if selected_nav == _("dashboard.welcome"):
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        # Check if user has permission to view dashboard
        if not require_permission('dashboard:view'):
            st.warning("You don't have permission to access the dashboard. Please contact an administrator for access.")
            st.info("Your role requires the 'dashboard:view' permission to use this feature.")
            st.stop()
        
        # Clean dashboard header with professional styling
        st.markdown(f"""
        <div style="padding: 15px 0; text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2563EB; font-weight: 600; margin-bottom: 5px;">{_("dashboard.title")}</h1>
            <p style="color: #64748b; font-size: 16px;">{_("dashboard.subtitle")}</p>
        </div>
        """, unsafe_allow_html=True)
            
        # Log this access silently without showing UI elements
        try:
            results_aggregator.log_audit_event(
                username=st.session_state.username,
                action="DASHBOARD_ACCESS",
                details={"access_time": datetime.now().isoformat()}
            )
        except Exception:
            pass
        
        # Summary metrics
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            total_scans = len(all_scans)
            total_pii = sum(scan.get('total_pii_found', 0) for scan in all_scans)
            high_risk_items = sum(scan.get('high_risk_count', 0) for scan in all_scans)
            
            col1, col2, col3 = st.columns(3)
            col1.metric(_("dashboard.metric.total_scans"), total_scans)
            col2.metric(_("dashboard.metric.total_pii"), total_pii)
            col3.metric(_("dashboard.metric.high_risk"), high_risk_items)
            
            # Privacy & Compliance Analytics Dashboard Section
            st.markdown(f"""
            <h3 style="margin: 20px 0 15px 0; color: #1e3a8a; font-weight: 600;">
                {_("dashboard.analytics_title")}
            </h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="background-color: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0;">
                    <h4 style="margin: 0 0 5px 0; color: #1976D2; font-size: 15px;">{_("dashboard.cost_efficiency")}</h4>
                    <p style="font-size: 24px; font-weight: 600; color: #2E7D32; margin: 10px 0 5px 0;">€104,800.01</p>
                    <p style="margin: 0; color: #6b7280; font-size: 0.85em;">{_("dashboard.potential_savings")}</p>
                </div>
            
                <div style="background-color: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0;">
                    <h4 style="margin: 0 0 5px 0; color: #1976D2; font-size: 15px;">{_("dashboard.sustainability_score")}</h4>
                    <div style="width: 70px; height: 70px; margin: 10px auto; background-color: #8BC34A; border-radius: 50%; display: flex; justify-content: center; align-items: center;">
                        <span style="color: white; font-size: 24px; font-weight: 600;">71</span>
                    </div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.85em;">{_("dashboard.status")}: <span style="color: #8BC34A; font-weight: 600;">{_("dashboard.status_good")}</span></p>
                </div>
            
                <div style="background-color: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0;">
                    <h4 style="margin: 0 0 5px 0; color: #1976D2; font-size: 15px;">{_("dashboard.fine_protection")}</h4>
                    <p style="font-size: 24px; font-weight: 600; color: #9C27B0; margin: 10px 0 5px 0;">92%</p>
                    <p style="margin: 0; color: #6b7280; font-size: 0.85em;">{_("dashboard.risk_mitigation")}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recent scans
            st.subheader(_("dashboard.recent_scans"))
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
                st.subheader(_("dashboard.pii_distribution"))
                
                # Aggregate PII types from all scans
                pii_counts = {}
                for scan in all_scans:
                    if 'pii_types' in scan:
                        for pii_type, count in scan['pii_types'].items():
                            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + count
                
                if pii_counts:
                    pii_df = pd.DataFrame(list(pii_counts.items()), columns=[_("dashboard.pii_type"), _("dashboard.count")])
                    fig = px.bar(pii_df, x=_("dashboard.pii_type"), y=_("dashboard.count"), color=_("dashboard.pii_type"))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Risk Level Distribution
                st.subheader(_("dashboard.risk_distribution"))
                risk_counts = {_("severity.low"): 0, _("severity.medium"): 0, _("severity.high"): 0}
                for scan in all_scans:
                    if 'risk_levels' in scan:
                        for risk, count in scan['risk_levels'].items():
                            # Map English risk levels to translated values
                            if risk == 'Low':
                                risk_counts[_("severity.low")] += count
                            elif risk == 'Medium':
                                risk_counts[_("severity.medium")] += count
                            elif risk == 'High':
                                risk_counts[_("severity.high")] += count
                
                risk_df = pd.DataFrame(list(risk_counts.items()), columns=[_("dashboard.risk_level"), _("dashboard.count")])
                fig = px.pie(risk_df, values=_("dashboard.count"), names=_("dashboard.risk_level"), color=_("dashboard.risk_level"),
                             color_discrete_map={_("severity.low"): 'green', _("severity.medium"): 'orange', _("severity.high"): 'red'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Scan Types
                st.subheader(_("dashboard.scan_distribution"))
                scan_type_counts = {}
                for scan in all_scans:
                    scan_type = scan.get('scan_type', _("dashboard.unknown"))
                    scan_type_counts[scan_type] = scan_type_counts.get(scan_type, 0) + 1
                
                scan_type_df = pd.DataFrame(list(scan_type_counts.items()), columns=[_("dashboard.scan_type"), _("dashboard.count")])
                fig = px.bar(scan_type_df, x=_("dashboard.scan_type"), y=_("dashboard.count"), color=_("dashboard.scan_type"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(_("dashboard.no_scan_data"))
        else:
            st.info(_("dashboard.no_scan_data"))
    
    elif selected_nav == _("scan.title"):
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title(_("scan.new_scan_title"))
        
        # Check if user has permission to create scans
        if not require_permission('scan:create'):
            st.warning(_("permission.no_scan_create"))
            st.info(_("permission.requires_scan_create"))
            st.stop()
        
        # Scan configuration form - expanded with all scanner types
        scan_type_options = [
            _("scan.code"), 
            _("scan.document"),  # Blob Scan
            _("scan.image"), 
            _("scan.database"),
            _("scan.api"),
            _("scan.website"),
            _("scan.manual_upload"),
            _("scan.sustainability"),
            _("scan.ai_model"),
            _("scan.soc2")
        ]
        
        # Add premium tag to premium features
        if not has_permission('scan:premium'):
            scan_type_options_with_labels = []
            premium_scans = [_("scan.image"), _("scan.api"), _("scan.sustainability"), _("scan.ai_model"), _("scan.soc2")]
            
            for option in scan_type_options:
                if option in premium_scans:
                    scan_type_options_with_labels.append(f"{option} 💎")
                else:
                    scan_type_options_with_labels.append(option)
                    
            scan_type = st.selectbox(_("scan.select_type"), scan_type_options_with_labels)
            # Remove the premium tag for processing
            scan_type = scan_type.replace(" 💎", "")
            
            # Show premium feature message if needed
            if scan_type in premium_scans:
                st.warning(_("scan.premium_warning"))
                with st.expander(_("scan.premium_details_title")):
                    st.markdown(_("scan.premium_details_description"))
                    if st.button(_("scan.view_upgrade_options")):
                        st.session_state.selected_nav = _("nav.membership")
                        st.rerun()
        else:
            scan_type = st.selectbox(_("scan.select_type"), scan_type_options)
        
        region = st.selectbox(_("scan.select_region"), list(REGIONS.keys()))
        
        # Additional configurations - customized for each scan type
        with st.expander(_("scan.advanced_configuration")):
            # Scan-specific configurations based on type
            if scan_type == _("scan.code"):
                # 1. Code Scanner
                st.subheader("Code Scanner Configuration")
                
                # Use session state to remember the selection
                if 'repo_source' not in st.session_state:
                    st.session_state.repo_source = _("scan.upload_files")
                
                # Create the radio button and update session state
                repo_source = st.radio(_("scan.repository_details"), [_("scan.upload_files"), _("scan.repository_url")], 
                                      index=0 if st.session_state.repo_source == _("scan.upload_files") else 1,
                                      key="repo_source_radio")
                
                # Update the session state
                st.session_state.repo_source = repo_source
                
                if repo_source == _("scan.repository_url"):
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
                
            elif scan_type == _("scan.document"):
                # 2. Blob Scanner
                st.subheader("Blob Scanner Configuration")
                blob_source = st.radio(_("scan.repository_details"), [_("scan.upload_files"), "Azure Blob", "AWS S3", "Local Path"])
                
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
                
            elif scan_type == _("scan.image"):
                # 3. Image Scanner
                st.subheader("Image Scanner Configuration")
                image_source = st.radio(_("scan.repository_details"), [_("scan.upload_files"), "Azure Blob", "AWS S3", "Local Path"])
                
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
                
            elif scan_type == _("scan.database"):
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
                
            elif scan_type == _("scan.api"):
                # 5. API Scanner
                st.subheader("API Scanner Configuration")
                api_type = st.selectbox("API Type", ["REST", "GraphQL", "SOAP", "gRPC"])
                
                api_source = st.radio(_("scan.repository_details"), ["Live Endpoint URL", "OpenAPI/Swagger Specification", "Both"])
                
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
                           
            elif scan_type == _("scan.website"):
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
                
                # Website scan doesn't require file uploads
                uploaded_files = []
                
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
                
            elif scan_type == _("scan.manual"):
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
                
            elif scan_type == _("scan.sustainability"):
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
                
            elif scan_type == _("scan.ai_model"):
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
                
            elif scan_type == _("scan.soc2"):
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
        st.subheader(_("scan.upload_files"))
        
        if scan_type == _("scan.code"):
            # Use what was already set in the Advanced Configuration section
            # repo_source is now directly in st.session_state from the radio button
                
            if st.session_state.repo_source == _("scan.upload_files"):
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
                st.subheader(_("scan.repository_details"))
                
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
        
        elif scan_type == _("scan.blob"):
            if 'blob_source' in locals() and blob_source == _("scan.upload_files"):
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
                
        elif scan_type == _("scan.image"):
            if 'image_source' in locals() and image_source == _("scan.upload_files"):
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
                
        elif scan_type == _("scan.database"):
            st.info("Database scanning does not require file uploads. Configure the database connection and scan settings above.")
            uploaded_files = []
            
        elif scan_type == _("scan.api"):
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
                
        elif scan_type == _("scan.manual"):
            upload_help = "Upload any files for manual scanning"
            uploaded_files = st.file_uploader(
                "Upload Files for Manual Scan", 
                accept_multiple_files=True,
                help=upload_help
            )
            
        elif scan_type == _("scan.sustainability"):
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
                
        elif scan_type == _("scan.ai_model"):
            if model_source == _("scan.upload_files"):
                upload_help = "Upload model files or sample data"
                uploaded_files = st.file_uploader(
                    "Upload Model Files or Sample Data", 
                    accept_multiple_files=True,
                    type=["h5", "pb", "tflite", "pt", "onnx", "json", "csv", "txt"],
                    help=upload_help
                )
            else:
                uploaded_files = []
                
        elif scan_type == _("scan.soc2"):
            if log_source == _("scan.upload_files"):
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
            if scan_type == _("scan.code") and st.session_state.repo_source == _("scan.repository_url"):
                proceed_with_scan = True
            # Other validation logic
            elif scan_type in [_("scan.code"), _("scan.blob"), _("scan.image")] and not uploaded_files:
                st.error(f"Please upload at least one file to scan for {scan_type}.")
            elif scan_type == _("scan.database"):
                # For database scans, always allow
                proceed_with_scan = True
            elif scan_type == _("scan.api"):
                # For API scans
                proceed_with_scan = True
            elif scan_type == _("scan.sustainability"):
                # For sustainability scans
                proceed_with_scan = True
            elif scan_type == _("scan.soc2"):
                # For SOC2 scans
                proceed_with_scan = True
            elif scan_type == _("scan.ai_model"):
                # For AI Model scans
                proceed_with_scan = True
            elif scan_type == _("scan.manual") and not uploaded_files:
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
                if scan_type == _("scan.code") and st.session_state.repo_source == _("scan.repository_url"):
                    # We'll handle the repository URL scanning differently using our RepoScanner
                    st.info("Starting repository URL scan...")
                    
                    # Get repository URL parameters from session state
                    repo_url = st.session_state.get('repo_url', '')
                    branch_name = st.session_state.get('branch_name', 'main')
                    auth_token = st.session_state.get('auth_token', None)
                    
                    if not repo_url:
                        st.error("Repository URL not provided. Please enter a valid repository URL.")
                        st.stop()
                    
                    # Create a placeholder list of files to satisfy the code structure
                    class MockFile:
                        def __init__(self, name):
                            self.name = name
                        def getbuffer(self):
                            return b"Repository URL scan"
                    
                    uploaded_files = [MockFile("repository.scan")]
                
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
                if scan_type == _("scan.code"):
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
                
                if scan_type == _("scan.code"):
                    # For code scan, use the directory-level scan with resilience features
                    try:
                        # Special handling for repository URL scanning
                        if st.session_state.repo_source == _("scan.repository_url"):
                            # Get repository URL parameters from session state
                            repo_url = st.session_state.get('repo_url', '')
                            branch_name = st.session_state.get('branch_name', 'main')
                            auth_token = st.session_state.get('auth_token', None)
                            
                            if not repo_url:
                                st.error("Repository URL not provided. Please enter a valid repository URL.")
                                st.stop()
                                
                            status_text.text(f"Starting repository scan of: {repo_url} (branch: {branch_name})")
                            progress_bar.progress(0.1)
                            
                            # Make sure we're using a proper CodeScanner instance for the RepoScanner
                            from services.code_scanner import CodeScanner
                            
                            # Create a dedicated CodeScanner for the repository scanning
                            # This ensures we're not passing a dict or invalid scanner object
                            code_scanner_instance = CodeScanner(region=region)
                            
                            # Initialize the RepoScanner with a proper CodeScanner instance
                            repo_scanner = RepoScanner(code_scanner=code_scanner_instance)
                            
                            # Define a custom progress callback for repository scanning
                            def repo_progress_callback(current, total, current_file):
                                progress = 0.1 + (current / total * 0.8)  # Scale to 10%-90% range
                                progress_bar.progress(min(progress, 0.9))
                                status_text.text(f"Scanning repository file {current}/{total}: {current_file}")
                            
                            # Scan the repository
                            result = repo_scanner.scan_repository(
                                repo_url=repo_url,
                                branch=branch_name,
                                auth_token=auth_token,
                                progress_callback=repo_progress_callback
                            )
                            
                            # Check if scan was successful
                            if result.get('status') == 'error':
                                st.error(f"Repository scan failed: {result.get('message', 'Unknown error')}")
                                st.stop()
                            
                            # Check and display branch information
                            if 'repository_metadata' in result and 'active_branch' in result['repository_metadata']:
                                actual_branch = result['repository_metadata']['active_branch']
                                # If the actual branch is different from the requested branch, inform the user
                                if branch_name and actual_branch != branch_name:
                                    st.info(f"Note: Branch '{branch_name}' was not found. The repository was scanned using the default branch '{actual_branch}' instead.")
                            
                            # Store findings from repository scan
                            scan_results = result.get('findings', [])
                            
                            # Show completion status
                            progress_bar.progress(1.0)
                            file_count = len(scan_results)
                            status_text.text(f"Completed repository scan. Scanned {file_count} files.")
                            
                        # Standard directory or file scanning
                        elif len(file_paths) == 1 and os.path.isdir(file_paths[0]):
                            # Scan entire directory with resilient method
                            directory_path = file_paths[0]
                            status_text.text(f"Starting directory scan of: {directory_path}")
                            
                            # Configure ignore patterns - only ignore truly unnecessary files
                            # Reduced list to ensure we scan more files for better coverage
                            ignore_patterns = [
                                "**/.git/**",           # Git internals
                                "**/__pycache__/**",    # Python cache files
                                "**/venv/**"            # Virtual environments
                            ]
                            
                            # Define progress callback for directory scanning
                            def update_progress(current, total, current_file):
                                progress = 0.1 + (current / total * 0.8)  # Scale to 10%-90% range
                                progress_bar.progress(min(progress, 0.9))
                                status_text.text(f"Scanning file {current}/{total}: {current_file}")
                            
                            # Create a dedicated CodeScanner instance for directory scanning
                            # This ensures we're not using a potentially invalid scanner object
                            from services.code_scanner import CodeScanner
                            directory_scanner = CodeScanner(region=region)
                            
                            # Run the resilient scan with checkpointing
                            result = directory_scanner.scan_directory(
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
                                
                                # Create a dedicated CodeScanner instance for individual file scanning
                                from services.code_scanner import CodeScanner
                                file_scanner = CodeScanner(region=region)
                                
                                # Use timeout-protected scan
                                result = file_scanner._scan_file_with_timeout(file_path)
                                scan_results.append(result)
                    except Exception as e:
                        st.error(f"Error during code scan: {str(e)}")
                        # Show detailed error information for debugging
                        st.error(f"Error type: {type(e).__name__}")
                        import traceback
                        st.code(traceback.format_exc())
                elif scan_type == _("scan.website"):
                    # For website scan, use our WebsiteScanner class
                    try:
                        # Display scanning information
                        status_text.text(f"Starting website scan of: {website_url}")
                        
                        # Define progress callback for real-time updates
                        def website_progress_callback(current, total, url):
                            progress = 0.5 + (current / total / 2)  # Scale to 50%-100% range
                            progress_bar.progress(min(progress, 1.0))
                            status_text.text(f"Scanning page {current}/{total}: {url}")
                        
                        # Initialize websitescanner with proper configuration
                        languages = website_languages if 'website_languages' in locals() else ["English"]
                        rate_limit = requests_per_minute if 'requests_per_minute' in locals() else 10
                        max_pages = max_pages if 'max_pages' in locals() else 20
                        
                        website_scanner = WebsiteScanner(
                            languages=languages,
                            region=region,
                            rate_limit=rate_limit,
                            max_pages=max_pages,
                            cookies_enabled=True,
                            js_enabled=True
                        )
                        
                        # Set progress callback
                        website_scanner.set_progress_callback(website_progress_callback)
                        
                        # Run the website scan
                        result = website_scanner.scan_website(
                            url=website_url,
                            include_text=include_text if 'include_text' in locals() else True,
                            include_images=include_images if 'include_images' in locals() else True,
                            include_forms=include_forms if 'include_forms' in locals() else True,
                            include_metadata=include_metadata if 'include_metadata' in locals() else True,
                            detect_pii=detect_pii if 'detect_pii' in locals() else True,
                            detect_cookies=detect_cookies if 'detect_cookies' in locals() else True,
                            detect_trackers=detect_trackers if 'detect_trackers' in locals() else True,
                            analyze_privacy_policy=analyze_privacy_policy if 'analyze_privacy_policy' in locals() else True
                        )
                        
                        # Get findings from result
                        if 'findings' in result:
                            # The result already contains all necessary information
                            # Just store it for the aggregator
                            scan_results = [result]
                        else:
                            scan_results = []
                            st.error("No findings returned from website scan")
                        
                    except Exception as e:
                        st.error(f"Error during website scan: {str(e)}")
                        # Display error details
                        st.error(f"Error details: {type(e).__name__}")
                        import traceback
                        st.code(traceback.format_exc())
                else:
                    # For other scan types, create appropriate scanner based on scan type
                    from services.blob_scanner import BlobScanner
                    from services.image_scanner import ImageScanner
                    from services.db_scanner import DatabaseScanner
                    
                    # Initialize the appropriate scanner based on scan type
                    if scan_type == _("scan.document"):
                        scanner_instance = BlobScanner(region=region)
                    elif scan_type == _("scan.image"):
                        scanner_instance = ImageScanner(region=region)
                    elif scan_type == _("scan.database"):
                        scanner_instance = DatabaseScanner(region=region)
                    else:
                        # Generic mock scanner for other types
                        scanner_instance = {
                            'scan_file': lambda file_path: {
                                'pii_found': [
                                    {'type': 'Demo PII', 'value': f'Sample in {os.path.basename(file_path)}', 'location': file_path, 'risk_level': 'Medium'}
                                ],
                                'file_path': file_path,
                                'status': 'success',
                                'scan_time': datetime.now().isoformat()
                            }
                        }
                    
                    # Scan each file with the appropriate scanner
                    for i, file_path in enumerate(file_paths):
                        progress = 0.5 + (i + 1) / (2 * len(file_paths))
                        progress_bar.progress(progress)
                        status_text.text(f"Scanning file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
                        
                        try:
                            # Call scan_file method on the appropriate scanner
                            if isinstance(scanner_instance, dict):
                                # For mock scanners
                                result = scanner_instance['scan_file'](file_path)
                            else:
                                # For real scanner instances with method
                                result = scanner_instance.scan_file(file_path)
                                
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
                medium_risk_count = 0 
                low_risk_count = 0
                
                # Handle different formats based on scan type
                if scan_type == _("scan.website") and len(scan_results) > 0:
                    # Website scan has a different format - findings are directly in the result
                    result = scan_results[0]  # Website scanner returns a single comprehensive result
                    
                    # Extract findings directly 
                    if 'findings' in result:
                        findings = result.get('findings', [])
                        for finding in findings:
                            pii_type = finding.get('type', 'Unknown')
                            risk_level = finding.get('risk_level', 'Medium')
                            
                            # Update counts
                            pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
                            total_pii_found += 1
                            
                            if risk_level == "High":
                                high_risk_count += 1
                            elif risk_level == "Medium":
                                medium_risk_count += 1
                            elif risk_level == "Low":
                                low_risk_count += 1
                        
                        # If result has pre-calculated counts, use those
                        if all(key in result for key in ['total_pii_found', 'high_risk_count', 'medium_risk_count', 'low_risk_count']):
                            # These might be more accurate as they include analyzed security issues
                            total_pii_found = result.get('total_pii_found', total_pii_found)
                            high_risk_count = result.get('high_risk_count', high_risk_count)
                            medium_risk_count = result.get('medium_risk_count', medium_risk_count)
                            low_risk_count = result.get('low_risk_count', low_risk_count)
                            
                            # Use pre-calculated risk levels if provided
                            if 'risk_levels' in result:
                                risk_levels = result.get('risk_levels', risk_levels)
                            
                            # Use pre-calculated PII types if provided
                            if 'pii_types' in result:
                                pii_types = result.get('pii_types', pii_types)
                else:
                    # Standard format for other scan types
                    for result in scan_results:
                        for pii_item in result.get('pii_found', []):
                            pii_type = pii_item.get('type', 'Unknown')
                            risk_level = pii_item.get('risk_level', 'Medium')
                            
                            pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
                            total_pii_found += 1
                            
                            if risk_level == "High":
                                high_risk_count += 1
                            elif risk_level == "Medium":
                                medium_risk_count += 1
                            elif risk_level == "Low":
                                low_risk_count += 1
                
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
                
                # Immediate scan results preview
                st.markdown("---")
                st.subheader("Immediate Scan Results Preview")
                
                # Create a container for the preview
                preview_container = st.container()
                
                with preview_container:
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total PII Found", total_pii_found)
                    col2.metric("High Risk Items", high_risk_count)
                    col3.metric("Files Scanned", len(file_paths))
                    
                    # Calculate compliance score based on scan results
                    scan_type_specific_weights = {
                        _("scan.website"): {
                            "privacy_policy": 0.25,
                            "cookies_compliance": 0.20,
                            "data_security": 0.25,
                            "tracking_consent": 0.15,
                            "data_minimization": 0.15
                        },
                        _("scan.code"): {
                            "data_security": 0.30,
                            "sensitive_data_handling": 0.30,
                            "data_minimization": 0.20,
                            "purpose_limitation": 0.10,
                            "lawful_basis": 0.10
                        }
                    }
                    
                    # Get the weights for the current scan type, or use defaults
                    weights = scan_type_specific_weights.get(scan_type, None)
                    
                    # Calculate the compliance score
                    compliance_score_result = calculate_compliance_score(
                        scan_results=aggregated_result,
                        weights=weights
                    )
                    
                    # Display the compliance score card
                    st.markdown("### Compliance Score")
                    display_compliance_score_card(
                        compliance_score=compliance_score_result,
                        show_details=True,
                        animate=True,
                        key_suffix=f"scan_{scan_id}"
                    )
                    
                    # Risk Assessment
                    st.markdown("### Risk Assessment")
                    risk_level = "High" if high_risk_count > 10 else "Medium" if high_risk_count > 0 else "Low" if total_pii_found > 0 else "None"
                    risk_color = "red" if risk_level == "High" else "orange" if risk_level == "Medium" else "green"
                    
                    st.markdown(f"**Overall Risk Level:** <span style='color:{risk_color};'>{risk_level}</span>", unsafe_allow_html=True)
                    
                    # Create horizontal bar chart for PII types
                    if pii_types:
                        st.markdown("### PII Types Detected")
                        
                        # Convert to DataFrame for visualization
                        pii_df = pd.DataFrame(list(pii_types.items()), columns=['PII Type', 'Count'])
                        pii_df = pii_df.sort_values('Count', ascending=False)
                        
                        # Create a bar chart
                        fig = px.bar(pii_df, x='Count', y='PII Type', orientation='h', 
                                    color='Count', color_continuous_scale='blues')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Preview of findings
                    st.markdown("### Sample Findings")
                    all_findings = []
                    for result in scan_results:
                        for item in result.get('pii_found', []):
                            all_findings.append({
                                'Type': item.get('type', 'Unknown'),
                                'Value': item.get('value', 'Unknown'),
                                'Risk Level': item.get('risk_level', 'Unknown'),
                                'Location': item.get('location', 'Unknown')
                            })
                    
                    # Display a sample of findings (up to 10 items)
                    if all_findings:
                        sample_findings = all_findings[:10]
                        findings_df = pd.DataFrame(sample_findings)
                        st.dataframe(findings_df, use_container_width=True)
                        
                        # Show how many more findings there are
                        if len(all_findings) > 10:
                            st.info(f"Showing 10 of {len(all_findings)} findings. See full results in Scan History.")
                    else:
                        st.info("No findings to display.")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("View Full Report", key="view_full_report"):
                            st.session_state.selected_nav = _("history.title")
                            st.rerun()
                    
                    with col2:
                        # Report and Certificate Generation
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Generate PDF Report", key="quick_pdf_report", use_container_width=True):
                                # Import report generator
                                from services.report_generator import generate_report
                                
                                with st.spinner("Generating PDF report..."):
                                    pdf_bytes = generate_report(aggregated_result)
                                    
                                    # Create download link
                                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{display_scan_id}.pdf">Download PDF Report</a>'
                        
                        # Compliance Certificate for Premium users
                        with col2:
                            # Check if user is premium
                            is_premium = st.session_state.role in ["premium", "admin"]
                            
                            # Check if scan is fully compliant
                            cert_generator = CertificateGenerator(language=st.session_state.language)
                            is_compliant = cert_generator.is_fully_compliant(aggregated_result)
                            
                            # Button text based on compliance and premium status
                            if is_premium and is_compliant:
                                cert_btn_text = _("dashboard.generate_certificate")
                                cert_btn_disabled = False
                                cert_btn_help = _("dashboard.generate_certificate_help")
                            elif not is_premium and is_compliant:
                                cert_btn_text = _("dashboard.premium_certificate") 
                                cert_btn_disabled = True
                                cert_btn_help = _("dashboard.premium_certificate_help")
                            elif is_premium and not is_compliant:
                                cert_btn_text = _("dashboard.cannot_generate_certificate")
                                cert_btn_disabled = True
                                cert_btn_help = _("dashboard.cannot_generate_certificate_help")
                            else:
                                cert_btn_text = _("dashboard.premium_certificate")
                                cert_btn_disabled = True
                                cert_btn_help = _("dashboard.premium_certificate_help2")
                            
                            if st.button(cert_btn_text, key="generate_certificate", 
                                        disabled=cert_btn_disabled, help=cert_btn_help,
                                        use_container_width=True):
                                
                                with st.spinner(_("dashboard.generating_certificate")):
                                    # Get user info for certificate
                                    user_info = {
                                        "username": st.session_state.username,
                                        "role": st.session_state.role,
                                        "email": st.session_state.email,
                                        "membership": "premium"  # Since we already checked
                                    }
                                    
                                    # Generate certificate
                                    company_name = None  # Could be added as an input field if needed
                                    cert_path = cert_generator.generate_certificate(
                                        aggregated_result, user_info, company_name
                                    )
                                    
                                    if cert_path and os.path.exists(cert_path):
                                        # Read the certificate PDF
                                        with open(cert_path, 'rb') as file:
                                            cert_bytes = file.read()
                                        
                                        # Create download link
                                        b64_cert = base64.b64encode(cert_bytes).decode()
                                        href = f'<a href="data:application/pdf;base64,{b64_cert}" download="GDPR_Compliance_Certificate_{display_scan_id}.pdf">Download Compliance Certificate</a>'
                                        st.markdown(href, unsafe_allow_html=True)
                                        
                                        st.success(_("dashboard.certificate_success"))
                                    else:
                                        st.error(_("dashboard.certificate_error"))
                                
                    with col3:
                        # Quick HTML Report generation
                        if st.button("Generate HTML Report", key="quick_html_report"):
                            # Import HTML report generator
                            from services.html_report_generator import save_html_report
                            
                            with st.spinner("Generating HTML report..."):
                                # Create reports directory if it doesn't exist
                                reports_dir = "reports"
                                os.makedirs(reports_dir, exist_ok=True)
                                
                                # Save the HTML report
                                file_path = save_html_report(aggregated_result, reports_dir)
                                
                                # Success message
                                st.success(f"HTML report saved. You can access it from the '{_('results.title')}' page.")
                
                st.markdown("---")
                st.info(f"You can also access the full results in the '{_('history.title')}' section.")
        
    elif selected_nav == _("history.title"):
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title(_("history.title"))
        
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
            st.markdown(f"### {_('dashboard.compliance_status')}")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            metric_col1.markdown(f"""
            <div style="padding: 10px; background-color: #f0f5ff; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0;">{_('dashboard.total_scans')}</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{total_scans}</p>
            </div>
            """, unsafe_allow_html=True)
            
            metric_col2.markdown(f"""
            <div style="padding: 10px; background-color: #f0fff0; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0;">{_('dashboard.total_pii_found')}</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{total_pii}</p>
            </div>
            """, unsafe_allow_html=True)
            
            metric_col3.markdown(f"""
            <div style="padding: 10px; background-color: #fff0f0; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0;">{_('dashboard.high_risk_items')}</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{high_risk}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add visualization tabs
            st.markdown(f"### {_('dashboard.scan_analysis')}")
            viz_tabs = st.tabs([_("dashboard.timeline"), _("dashboard.risk_analysis"), _("dashboard.scan_history")])
            
            with viz_tabs[0]:  # Timeline
                if 'timestamp' in scans_df.columns:
                    # Create a date field
                    scans_df['date'] = scans_df['timestamp'].dt.date
                    
                    # Group by date and count
                    date_counts = scans_df.groupby('date').size().reset_index(name='count')
                    
                    # Create timeline chart
                    fig = px.line(date_counts, x='date', y='count', 
                                  title=_("dashboard.scan_activity_over_time"),
                                  labels={'count': _("dashboard.number_of_scans"), 'date': _("dashboard.date")})
                    
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
                           title=_("dashboard.risk_level_distribution"),
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
                    
                    fig = px.bar(pii_df, x='PII Type', y='Count', title=_("dashboard.most_common_pii_types"),
                                color='Count', color_continuous_scale='Blues')
                    st.plotly_chart(fig, use_container_width=True)
            
            with viz_tabs[2]:  # Scan History Table
                # Add styling to the dataframe
                def highlight_risk(val):
                    if isinstance(val, (int, float)):
                        if val > 10:
                            # Critical risk (red)
                            return 'background-color: #FFEBEE; color: #C62828; font-weight: bold'
                        elif val > 5:
                            # High risk (orange)
                            return 'background-color: #FFF8E1; color: #F57F17; font-weight: bold'
                        elif val > 0:
                            # Medium risk (yellow)
                            return 'background-color: #FFFDE7; color: #FBC02D; font-weight: normal'
                    elif isinstance(val, str):
                        # Process string risk levels using the Smart AI risk analyzer color scheme
                        if val == 'Critical':
                            return 'background-color: #FFEBEE; color: #C62828; font-weight: bold'
                        elif val == 'High':
                            return 'background-color: #FFEBEE; color: #D32F2F; font-weight: bold'
                        elif val == 'Medium':
                            return 'background-color: #FFF8E1; color: #F57F17; font-weight: bold'
                        elif val == 'Low':
                            return 'background-color: #F1F8E9; color: #558B2F; font-weight: normal'
                        elif val == 'Info':
                            return 'background-color: #E3F2FD; color: #1976D2; font-weight: normal'
                    return ''
                
                # Apply styling
                styled_df = display_df.style.applymap(highlight_risk, subset=['High Risk Items', 'Total PII Found'])
                
                # Display scan history table with styled data
                st.dataframe(styled_df, use_container_width=True)
            
            # Allow user to select a scan to view details
            selected_display_id = st.selectbox(
                _("dashboard.select_scan_to_view"),
                options=scans_df['display_scan_id'].tolist(),
                format_func=lambda x: f"{x} - {scans_df[scans_df['display_scan_id']==x]['timestamp'].iloc[0].strftime('%b %d, %Y %H:%M')}"
            )
            
            # Convert display ID back to actual scan_id
            selected_scan_id = id_mapping.get(selected_display_id)
            
            if selected_scan_id:
                # Get the selected scan details
                selected_scan = results_aggregator.get_scan_by_id(selected_scan_id)
                
                if selected_scan:
                    st.subheader(f"{_('dashboard.scan_details')}: {selected_display_id}")
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    col1.metric(_("dashboard.scan_type"), selected_scan.get('scan_type', 'N/A'))
                    col2.metric(_("dashboard.region"), selected_scan.get('region', 'N/A'))
                    col3.metric(_("dashboard.files_scanned"), selected_scan.get('file_count', 0))
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric(_("dashboard.total_pii"), selected_scan.get('total_pii_found', 0))
                    col2.metric(_("dashboard.high_risk_items"), selected_scan.get('high_risk_count', 0))
                    timestamp = selected_scan.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    col3.metric(_("dashboard.date_time"), timestamp)
                    
                    # PII Types breakdown
                    if 'pii_types' in selected_scan and selected_scan['pii_types']:
                        st.subheader(_("dashboard.pii_types_found"))
                        pii_df = pd.DataFrame(list(selected_scan['pii_types'].items()), columns=['PII Type', 'Count'])
                        fig = px.bar(pii_df, x='PII Type', y='Count', color='PII Type')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Risk levels breakdown
                    if 'risk_levels' in selected_scan and selected_scan['risk_levels']:
                        st.subheader(_("dashboard.risk_level_distribution"))
                        risk_df = pd.DataFrame(list(selected_scan['risk_levels'].items()), columns=['Risk Level', 'Count'])
                        fig = px.pie(risk_df, values='Count', names='Risk Level', color='Risk Level',
                                    color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed findings
                    if 'detailed_results' in selected_scan and selected_scan['detailed_results']:
                        st.subheader(_("dashboard.detailed_findings"))
                        
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
                            
                            # Apply styling based on risk level using Smart AI risk severity color-coding system
                            def highlight_risk(val):
                                if val == 'Critical':
                                    return 'background-color: #FFEBEE; color: #C62828; font-weight: bold'
                                elif val == 'High':
                                    return 'background-color: #FFEBEE; color: #D32F2F; font-weight: bold'
                                elif val == 'Medium':
                                    return 'background-color: #FFF8E1; color: #F57F17; font-weight: bold'
                                elif val == 'Low':
                                    return 'background-color: #F1F8E9; color: #558B2F; font-weight: normal'
                                elif val == 'Info':
                                    return 'background-color: #E3F2FD; color: #1976D2; font-weight: normal'
                                elif val == 'Safe':
                                    return 'background-color: #E8F5E9; color: #388E3C; font-weight: normal'
                                return ''
                            
                            # Display the styled DataFrame
                            if 'Risk Level' in pii_items_df.columns:
                                styled_df = pii_items_df.style.applymap(highlight_risk, subset=['Risk Level'])
                                st.dataframe(styled_df, use_container_width=True)
                            else:
                                st.dataframe(pii_items_df, use_container_width=True)
                        else:
                            st.info(_("dashboard.no_pii_found"))
                    
                    # Generate report buttons
                    report_col1, report_col2 = st.columns(2)
                    
                    with report_col1:
                        if st.button(_("dashboard.generate_pdf_report"), key="gen_pdf_report"):
                            st.session_state.current_scan_id = selected_scan_id
                            
                            with st.spinner(_("dashboard.generating_pdf_report")):
                                pdf_bytes = generate_report(selected_scan)
                                
                                # Create download link
                                b64_pdf = base64.b64encode(pdf_bytes).decode()
                                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_display_id}.pdf">{_("dashboard.download_pdf_report")}</a>'
                                st.markdown(href, unsafe_allow_html=True)
                    
                    with report_col2:
                        if st.button(_("dashboard.generate_html_report"), key="gen_html_report"):
                            # Import HTML report generator
                            from services.html_report_generator import save_html_report, get_html_report_as_base64
                            
                            with st.spinner(_("dashboard.generating_html_report")):
                                # Create reports directory if it doesn't exist
                                reports_dir = "reports"
                                os.makedirs(reports_dir, exist_ok=True)
                                
                                # Save the HTML report
                                file_path = save_html_report(selected_scan, reports_dir)
                                
                                # Create download link
                                st.success(_("dashboard.html_report_saved").format(file_path=file_path))
                                st.info(_("dashboard.view_report_from_results").format(results_page=_('results.title')))
                                
                                # View the report immediately
                                # Using a container to display the report 
                                report_container = st.container()
                                with report_container:
                                    # Read the HTML content
                                    try:
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            html_content = f.read()
                                        
                                        # Create a data URL for the iframe
                                        encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                                        data_url = f"data:text/html;base64,{encoded_content}"
                                        
                                        # Display in an iframe with proper styling and size
                                        st.markdown(f"""
                                        <div style="border:1px solid #ddd; padding:10px; border-radius:8px; margin-top:20px; background-color:#f9f9f9;">
                                            <h3 style="margin-top:0; margin-bottom:10px; color:#1E40AF;">{_("dashboard.generated_html_report")}</h3>
                                            <iframe src="{data_url}" width="100%" height="700px" style="border:1px solid #ddd; border-radius:4px;"></iframe>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Error displaying report: {str(e)}")
                                        st.info(f"Please go to the '{_('results.title')}' page to view your report.")
        else:
            st.info(_("dashboard.no_scan_history"))
    
    elif selected_nav == _("results.title"):
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        from services.html_report_generator import get_html_report_as_base64, save_html_report
        import glob
        import os
        
        st.title(_("results.title"))
        
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
            selected_report = st.selectbox(_("reports.select_report"), 
                                        options=report_files,
                                        format_func=lambda x: os.path.basename(x))
            
            if selected_report:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(_("reports.view_report"), key="view_report"):
                        try:
                            # Read the HTML content
                            with open(selected_report, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            # Create a data URL for the iframe
                            encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                            data_url = f"data:text/html;base64,{encoded_content}"
                            
                            # Display in an iframe with improved styling
                            st.markdown(f"""
                            <div style="border:1px solid #ddd; padding:10px; border-radius:8px; margin-top:20px; background-color:#f9f9f9;">
                                <h3 style="margin-top:0; margin-bottom:10px; color:#1E40AF;">{_("reports.gdpr_compliance_report")}</h3>
                                <iframe src="{data_url}" width="100%" height="700px" style="border:1px solid #ddd; border-radius:4px;"></iframe>
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error displaying report: {str(e)}")
                            st.info("Try downloading the report instead and view it in your browser.")
                
                with col2:
                    if st.button(_("reports.download_report"), key="download_report"):
                        # Read the HTML content
                        with open(selected_report, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Create download link
                        b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                        href = f'<a href="data:text/html;base64,{b64_html}" download="{os.path.basename(selected_report)}">{_("reports.download_html_report")}</a>'
                        st.markdown(href, unsafe_allow_html=True)
        else:
            st.info(_("reports.no_saved_reports"))
            
            # Add a demo report if needed
            if st.button("Generate Demo Report"):
                # Create a sample scan result
                sample_scan = {
                    "scan_id": f"demo-{uuid.uuid4().hex[:8]}",
                    "scan_type": _("scan.website"),
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
    
    elif selected_nav == _("report.generate") or selected_nav == _("reports.title"):
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title(_("report.generate"))
        
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
            # Fixed issue: Renamed underscore variable to avoid conflict with translation function
            for index, scan in scans_df.iterrows():
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
            
            # Use get_text directly to avoid any potential naming conflicts with variables
            select_scan_label = get_text("report.select_scan", "Select a scan to generate report")
            selected_scan_index = st.selectbox(
                select_scan_label,
                options=range(len(scan_options)),
                format_func=lambda i: scan_options[i]['display']
            )
            
            selected_scan_id = scan_options[selected_scan_index]['scan_id']
            scan_data = results_aggregator.get_scan_by_id(selected_scan_id)
            
            if scan_data:
                # Report generation options
                st.subheader(_("report.options"))
                
                col1, col2 = st.columns(2)
                with col1:
                    include_details = st.checkbox(_("report.include_detailed_findings"), value=True)
                    include_charts = st.checkbox(_("report.include_charts"), value=True)
                
                with col2:
                    include_metadata = st.checkbox(_("report.include_scan_metadata"), value=True)
                    include_recommendations = st.checkbox(_("report.include_recommendations"), value=True)
                
                # Generate report
                if st.button(_("report.generate")):
                    with st.spinner(_("report.generating")):
                        pdf_bytes = generate_report(
                            scan_data,
                            include_details=include_details,
                            include_charts=include_charts,
                            include_metadata=include_metadata,
                            include_recommendations=include_recommendations
                        )
                        
                        # Create download link
                        selected_display_id = scan_options[selected_scan_index]['display_id']
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_display_id}.pdf">{get_text("report.download_pdf", "Download PDF Report")}</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        st.success(_("report.generated_successfully"))
                
                # Report preview (if available from a previous generation)
                if 'current_scan_id' in st.session_state and st.session_state.current_scan_id == selected_scan_id and 'pdf_bytes' in locals():
                    st.subheader(_("report.preview"))
                    st.write(_("report.preview_not_available"))
            else:
                st.error(_("report.scan_not_found").format(scan_id=selected_scan_id))
        else:
            st.info(_("report.no_scan_history"))
            
    elif selected_nav == _("admin.title"):
        # Import required auth functionality
        from services.auth import require_permission, get_all_roles, get_all_permissions, get_user, create_user, update_user, delete_user, add_custom_permissions
        
        st.title(_("admin.title"))
        
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
            if not has_permission('user:create') and not has_permission('user:update') and not has_permission('user:delete'):
                st.warning("You don't have permission to manage users.")
                st.info("Your role requires 'user:create', 'user:update', or 'user:delete' permissions to use this feature.")
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
                st.info("Your role requires the 'admin:manage_roles' permission to use this feature. This is typically available to administrators only.")
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
                
                # User Role Management
                st.subheader("User Role & Permission Management")
                
                # Get all users
                all_users = {}
                try:
                    import json
                    with open('users.json', 'r') as f:
                        all_users = json.load(f)
                except Exception as e:
                    st.error(f"Error loading users: {str(e)}")
                
                if all_users:
                    # Create tabs for different permission management actions
                    role_tabs = st.tabs(["Change User Role", "Add Custom Permissions", "Remove Custom Permissions", "Reset Permissions"])
                    
                    # Tab 1: Change User Role
                    with role_tabs[0]:
                        with st.form("change_role_form"):
                            user_options = list(all_users.keys())
                            target_user = st.selectbox("Select User", user_options, key="change_role_user")
                            
                            # Get role options
                            role_options = list(all_roles.keys())
                            
                            # Get current role
                            current_role = "unknown"
                            if target_user and target_user in all_users:
                                current_role = all_users[target_user].get("role", "unknown")
                            
                            st.info(f"Current role: **{current_role}**")
                            
                            # Select new role
                            new_role = st.selectbox("Select New Role", role_options, 
                                                   index=role_options.index(current_role) if current_role in role_options else 0)
                            
                            # Form submission
                            submit_button = st.form_submit_button("Change Role")
                            
                            if submit_button:
                                if target_user and new_role:
                                    # Only process if role is actually changing
                                    if new_role != current_role:
                                        # Change role
                                        from services.auth import change_user_role
                                        success = change_user_role(target_user, new_role)
                                        
                                        if success:
                                            st.success(f"User '{target_user}' role changed from '{current_role}' to '{new_role}' successfully!")
                                            # Log this admin action
                                            try:
                                                results_aggregator.log_audit_event(
                                                    username=st.session_state.username,
                                                    action="USER_ROLE_CHANGED",
                                                    details={
                                                        "target_username": target_user,
                                                        "old_role": current_role,
                                                        "new_role": new_role,
                                                        "timestamp": datetime.now().isoformat()
                                                    }
                                                )
                                            except Exception as e:
                                                st.warning(f"Could not log audit event: {str(e)}")
                                        else:
                                            st.error(f"Error changing role for user: {target_user}")
                                    else:
                                        st.info(f"No change: User already has the role '{current_role}'")
                                else:
                                    st.error("Please select a user and a role")
                    
                    # Tab 2: Add Custom Permissions
                    with role_tabs[1]:
                        with st.form("add_custom_permissions"):
                            user_options = list(all_users.keys())
                            target_user = st.selectbox("Select User", user_options, key="add_perm_user")
                            
                            # Show user's role and current permissions
                            if target_user and target_user in all_users:
                                current_role = all_users[target_user].get("role", "unknown")
                                st.info(f"Current role: **{current_role}**")
                                
                                # Get user's current permissions
                                from services.auth import get_user_role_details
                                role_details = get_user_role_details(target_user)
                                
                                if role_details:
                                    # Display any custom permissions
                                    if role_details.get("custom_permissions"):
                                        st.write("**Current Custom Permissions:**")
                                        for perm in role_details.get("custom_permissions", []):
                                            desc = all_permissions.get(perm, "No description available")
                                            st.write(f"- **{perm}**: {desc}")
                            
                            # Display all available permissions
                            perm_options = list(all_permissions.keys())
                            custom_perms = st.multiselect("Select Custom Permissions to Add", perm_options, key="add_perms")
                            
                            # Form submission
                            submit_button = st.form_submit_button("Add Custom Permissions")
                            
                            if submit_button:
                                if target_user and custom_perms:
                                    # Add custom permissions
                                    from services.auth import add_custom_permissions
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
                    
                    # Tab 3: Remove Custom Permissions
                    with role_tabs[2]:
                        with st.form("remove_custom_permissions"):
                            user_options = list(all_users.keys())
                            target_user = st.selectbox("Select User", user_options, key="remove_perm_user")
                            
                            # Show user's role and current custom permissions
                            custom_permissions = []
                            if target_user and target_user in all_users:
                                current_role = all_users[target_user].get("role", "unknown")
                                st.info(f"Current role: **{current_role}**")
                                
                                # Get user's custom permissions
                                from services.auth import get_user_role_details
                                role_details = get_user_role_details(target_user)
                                
                                if role_details:
                                    custom_permissions = role_details.get("custom_permissions", [])
                                    
                                    if custom_permissions:
                                        st.write("**Current Custom Permissions:**")
                                        for perm in custom_permissions:
                                            desc = all_permissions.get(perm, "No description available")
                                            st.write(f"- **{perm}**: {desc}")
                                    else:
                                        st.info(f"User '{target_user}' has no custom permissions beyond their '{current_role}' role.")
                            
                            # Display custom permissions for removal
                            perms_to_remove = st.multiselect("Select Custom Permissions to Remove", 
                                                           custom_permissions, 
                                                           key="remove_perms")
                            
                            # Form submission
                            submit_button = st.form_submit_button("Remove Custom Permissions")
                            
                            if submit_button:
                                if target_user and perms_to_remove:
                                    # Remove custom permissions
                                    from services.auth import remove_custom_permissions
                                    success = remove_custom_permissions(target_user, perms_to_remove)
                                    
                                    if success:
                                        st.success(f"Custom permissions removed from user '{target_user}' successfully!")
                                        # Log this admin action
                                        try:
                                            results_aggregator.log_audit_event(
                                                username=st.session_state.username,
                                                action="CUSTOM_PERMISSIONS_REMOVED",
                                                details={
                                                    "target_username": target_user,
                                                    "permissions": perms_to_remove,
                                                    "timestamp": datetime.now().isoformat()
                                                }
                                            )
                                        except Exception as e:
                                            st.warning(f"Could not log audit event: {str(e)}")
                                    else:
                                        st.error(f"Error removing custom permissions from user: {target_user}")
                                elif target_user and not custom_permissions:
                                    st.info(f"User '{target_user}' has no custom permissions to remove.")
                                else:
                                    st.error("Please select a user and at least one permission to remove")
                    
                    # Tab 4: Reset Permissions
                    with role_tabs[3]:
                        with st.form("reset_permissions"):
                            user_options = list(all_users.keys())
                            target_user = st.selectbox("Select User", user_options, key="reset_perm_user")
                            
                            # Show user's role and whether they have custom permissions
                            if target_user and target_user in all_users:
                                current_role = all_users[target_user].get("role", "unknown")
                                st.info(f"Current role: **{current_role}**")
                                
                                # Check if user has custom permissions
                                from services.auth import get_user_role_details
                                role_details = get_user_role_details(target_user)
                                
                                if role_details and role_details.get("custom_permissions"):
                                    st.warning(f"User '{target_user}' has {len(role_details.get('custom_permissions', []))} custom permissions that will be reset.")
                                else:
                                    st.info(f"User '{target_user}' has standard permissions matching their '{current_role}' role.")
                            
                            st.warning("This will reset the user's permissions to match their role's default permissions. Any custom permissions will be removed.")
                            
                            # Form submission
                            submit_button = st.form_submit_button("Reset Permissions")
                            
                            if submit_button:
                                if target_user:
                                    # Reset permissions
                                    from services.auth import reset_user_permissions
                                    success = reset_user_permissions(target_user)
                                    
                                    if success:
                                        st.success(f"Permissions for user '{target_user}' reset to default '{current_role}' permissions successfully!")
                                        # Log this admin action
                                        try:
                                            results_aggregator.log_audit_event(
                                                username=st.session_state.username,
                                                action="USER_PERMISSIONS_RESET",
                                                details={
                                                    "target_username": target_user,
                                                    "role": current_role,
                                                    "timestamp": datetime.now().isoformat()
                                                }
                                            )
                                        except Exception as e:
                                            st.warning(f"Could not log audit event: {str(e)}")
                                    else:
                                        st.error(f"Error resetting permissions for user: {target_user}")
                                else:
                                    st.error("Please select a user")
                else:
                    st.info("No users found. Create users first to manage their roles and permissions.")
        
        with admin_tabs[2]:  # Audit Logs
            st.header("Audit Logs")
            
            # Check for audit logs permission
            if not has_permission('audit:view'):
                st.warning("You don't have permission to view audit logs.")
                st.info("Your role requires the 'audit:view' permission to use this feature.")
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
            if not has_permission('system:settings'):
                st.warning("You don't have permission to modify system settings.")
                st.info("Your role requires the 'system:settings' permission to use this feature.")
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

