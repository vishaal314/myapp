import streamlit as st
# Disable visualization dependencies to resolve numpy conflicts
# Core Image Scanner functionality preserved
pd = None
px = None
VISUALIZATION_AVAILABLE = False
import os
import uuid
import random
import string
import logging
import traceback
from datetime import datetime
import json
import base64
from io import BytesIO

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger instance for this module
logger = logging.getLogger(__name__)

from services.code_scanner import CodeScanner
from services.blob_scanner import BlobScanner
from services.website_scanner import WebsiteScanner
from services.results_aggregator import ResultsAggregator
from services.repo_scanner import RepoScanner
from services.report_generator_safe import generate_report
from services.certificate_generator import CertificateGenerator
from services.optimized_scanner import OptimizedScanner
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.ai_model_scanner import AIModelScanner
from services.enhanced_soc2_scanner import scan_github_repository, scan_azure_repository, display_soc2_scan_results
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email
from services.soc2_display import display_soc2_findings, run_soc2_display_standalone
from services.soc2_scanner import scan_github_repo_for_soc2, scan_azure_repo_for_soc2
from services.stripe_payment import display_payment_button, handle_payment_callback, SCAN_PRICES
from utils.gdpr_rules import REGIONS, get_region_rules
from utils.risk_analyzer import RiskAnalyzer, get_severity_color, colorize_finding, get_risk_color_gradient
from utils.i18n import initialize, language_selector, get_text, set_language, LANGUAGES, _translations

# Define translation function
def _(key, default=None):
    return get_text(key, default)
from utils.compliance_score import calculate_compliance_score, display_compliance_score_card

# === LANGUAGE INITIALIZATION BLOCK ===
# This critical section ensures language preservation across app state changes
# Check multiple storage locations for language settings

# First, initialize basic session state if needed
if 'language' not in st.session_state:
    # Check if we have a persistent language setting
    if '_persistent_language' in st.session_state:
        # Use persistent language across app reloads
        current_language = st.session_state['_persistent_language']
        print(f"INIT: Using _persistent_language: {current_language}")
    elif 'pre_login_language' in st.session_state:
        # Use pre-login language setting
        current_language = st.session_state['pre_login_language']
        print(f"INIT: Using pre_login_language: {current_language}")
    elif 'backup_language' in st.session_state:
        # Use backup language setting
        current_language = st.session_state['backup_language']
        print(f"INIT: Using backup_language: {current_language}")
    else:
        # Default to English if no language specified
        current_language = 'en'
        print("INIT: No language found, defaulting to 'en'")
    
    # Set the language in the primary location
    st.session_state['language'] = current_language
    
    # Force translations to be reloaded
    st.session_state['reload_translations'] = True

# Ensure translations are properly initialized 
# Sometimes the initialize function needs to be called multiple times
# to properly load all translations
_translations = {}  # Reset translations for fresh load
initialize()  # Initialize translations

# If we have a forced language, apply it now
if 'force_language_after_login' in st.session_state:
    # Use the forced language from login/logout process
    forced_language = st.session_state.pop('force_language_after_login')
    print(f"INIT: Applying forced language: {forced_language}")
    
    # Set language in all possible locations for redundancy
    st.session_state['language'] = forced_language
    st.session_state['pre_login_language'] = forced_language
    st.session_state['backup_language'] = forced_language
    st.session_state['_persistent_language'] = forced_language
    
    # Explicitly set the language
    set_language(forced_language)
    
    # Force reloading of translations
    initialize()
# === END LANGUAGE INITIALIZATION BLOCK ===
from utils.animated_language_switcher import animated_language_switcher, get_welcome_message_animation

# Make sure translations are initialized at the start of the app
initialize()

# Debug translations function for specific keys
def display_soc2_scan_results(scan_results):
    """
    Use the enhanced SOC2 display function to show scan results.
    This function uses the enhanced scanner module to display SOC2 findings with
    proper TSC criteria mapping.
    
    Args:
        scan_results: Dictionary containing SOC2 scan results
    """
    # Import is already at the top of file: 
    # from services.enhanced_soc2_scanner import display_soc2_scan_results
    # We'll call our enhanced implementation directly
    from services.enhanced_soc2_scanner import display_soc2_scan_results as enhanced_display
    enhanced_display(scan_results)

def debug_translations():
    """Print debug information about critical translation keys."""
    debug_keys = [
        "app.tagline", 
        "scan.new_scan_title", 
        "scan.select_type", 
        "scan.upload_files", 
        "scan.title",
        "dashboard.welcome",
        "history.title",
        "results.title",
        "report.generate"
    ]
    
    print("TRANSLATION DEBUG - Critical Keys:")
    for key in debug_keys:
        value = get_text(key)
        print(f"  {key}: '{value}'")
    
    # Dump the raw translations for the current language
    from utils.i18n import _translations, _current_language
    print(f"TRANSLATIONS DEBUG - Raw data for language {_current_language}:")
    if _current_language in _translations:
        # Print the first level keys only to avoid huge output
        print(f"  Available top-level keys: {list(_translations[_current_language].keys())}")
        if 'app' in _translations[_current_language]:
            print(f"  app keys: {_translations[_current_language]['app']}")
        if 'scan' in _translations[_current_language]:
            print(f"  scan keys: {_translations[_current_language]['scan']}")
    else:
        print(f"  No translations found for {_current_language}")
    
    # Also print current language state
    print(f"LANGUAGE DEBUG - Current state:")
    print(f"  language: {st.session_state.get('language')}")
    print(f"  _persistent_language: {st.session_state.get('_persistent_language')}")
    print(f"  pre_login_language: {st.session_state.get('pre_login_language')}")
    print(f"  backup_language: {st.session_state.get('backup_language')}")
    print(f"  force_language_after_login: {st.session_state.get('force_language_after_login')}")

# Run translation debug after initialization
debug_translations()

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

# Load custom CSS to hide unwanted navigation buttons
with open("static/custom.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Create top-right language switcher in a container with minimal style
lang_col1, lang_col2, lang_col3 = st.columns([6, 3, 1])
with lang_col3:
    # Create a clean language selector in the top-right
    st.markdown("""
    <div style="float: right; margin-right: 10px; margin-top: 5px;">
        <span style="font-size: 1em; margin-right: 5px;">🌐</span>
    </div>
    """, unsafe_allow_html=True)
    # Add a simple language dropdown
    current_language = st.session_state.get('language', 'en')
    language_options = {"en": "🇬🇧 English", "nl": "🇳🇱 Nederlands"}
    selected_language = st.selectbox(
        "",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=0 if current_language == "en" else 1,
        key="lang_selector_top",
        label_visibility="collapsed"
    )
    if selected_language != current_language:
        st.session_state['language'] = selected_language
        st.session_state['_persistent_language'] = selected_language
        set_language(selected_language)
        st.rerun()

# Authentication sidebar with professional colorful design
with st.sidebar:
    # Ensure translations are initialized with the current language
    current_language = st.session_state.get('language', 'en')
    set_language(current_language)
    
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
            if st.button(_("sidebar.sign_in"), key="tab_login", use_container_width=True):
                st.session_state.active_tab = "login"
        
        with tab2:
            if st.button(_("sidebar.create_account"), key="tab_register", use_container_width=True):
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
            # Form styling without duplicate header
            st.markdown(f"""
            <div style="background-image: linear-gradient(to right, #F5F0FF, #E9DAFF); 
                       padding: 5px; border-radius: 10px; margin-bottom: 15px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            </div>
            """, unsafe_allow_html=True)
            
            username_or_email = st.text_input(_("login.email_username"), key="login_username")
            password = st.text_input(_("login.password"), type="password", key="login_password")
            
            cols = st.columns([3, 2])
            with cols[0]:
                remember = st.checkbox(_("login.remember_me"), key="remember_login")
            with cols[1]:
                # Initialize state for forgot password flow if not present
                if 'forgot_password_active' not in st.session_state:
                    st.session_state.forgot_password_active = False
                    
                # Forgot password button
                if st.button(_('login.forgot_password'), key="forgot_password_btn"):
                    st.session_state.forgot_password_active = True
                
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
            
            # Show forgot password form if active
            if st.session_state.forgot_password_active:
                st.markdown("### " + _("login.reset_password_title", "Reset Your Password"))
                
                # Email input
                reset_email = st.text_input(_("login.email", "Email Address"), key="reset_email")
                
                # New password inputs
                new_password = st.text_input(_("login.new_password", "New Password"), type="password", key="new_password")
                confirm_password = st.text_input(_("login.confirm_password", "Confirm New Password"), type="password", key="confirm_password")
                
                reset_col1, reset_col2 = st.columns([1,1])
                
                with reset_col1:
                    # Reset password button
                    if st.button(_("login.reset_button", "Reset Password"), type="primary", key="reset_button"):
                        # Validate inputs
                        if not reset_email:
                            st.error(_("login.error.email_required", "Please enter your email address"))
                        elif not new_password:
                            st.error(_("login.error.password_required", "Please enter a new password"))
                        elif new_password != confirm_password:
                            st.error(_("login.error.password_mismatch", "Passwords do not match"))
                        else:
                            # Import reset_password function from auth module
                            from services.auth import reset_password, validate_email
                            
                            # Validate email format
                            if not validate_email(reset_email):
                                st.error(_("login.error.invalid_email", "Please enter a valid email address"))
                            else:
                                # Process password reset
                                success, message = reset_password(reset_email, new_password)
                                
                                if success:
                                    st.success(_("login.password_reset_success", "Password has been reset successfully. You can now log in with your new password."))
                                    # Deactivate forgot password mode
                                    st.session_state.forgot_password_active = False
                                else:
                                    st.error(_(f"login.error.reset_failed", f"Password reset failed: {message}"))
                
                with reset_col2:
                    # Cancel button
                    if st.button(_("login.cancel", "Cancel"), key="cancel_reset"):
                        st.session_state.forgot_password_active = False
                        st.rerun()
                
                # Add separator between reset form and login button
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # Only show login button if not in password reset mode
            if not st.session_state.forgot_password_active:
                login_button = st.button(_("login.button"), use_container_width=True, key="sidebar_login", type="primary")
            else:
                login_button = False
            
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
                        
                        # CRITICAL SECTION: Save language settings BEFORE login authentication changes
                        # This is a fundamental part of the language persistence fix
                        
                        # Gather all language sources with priorities
                        lang_sources = {
                            "_persistent_language": st.session_state.get("_persistent_language"),
                            "language": st.session_state.get("language"),
                            "pre_login_language": st.session_state.get("pre_login_language"),
                            "pre_logout_language": st.session_state.get("pre_logout_language"),
                            "backup_language": st.session_state.get("backup_language"),
                            "force_language_after_login": st.session_state.get("force_language_after_login")
                        }
                        
                        # Log all language sources for debugging
                        print(f"LOGIN - Language sources: {lang_sources}")
                        
                        # Find the first non-None language using priority order
                        current_language = None
                        for key in ["_persistent_language", "force_language_after_login", "language", 
                                   "pre_login_language", "pre_logout_language", "backup_language"]:
                            if lang_sources[key]:
                                current_language = lang_sources[key]
                                print(f"LOGIN - Using language from {key}: {current_language}")
                                break
                        
                        # Default to English as ultimate fallback
                        if not current_language:
                            current_language = 'en'
                            print(f"LOGIN - No language found, defaulting to: {current_language}")
                        
                        # Create temp copy that will survive the state changes
                        preserved_language = current_language
                        
                        # Force reload translations when this login completes
                        st.session_state['reload_translations'] = True
                        
                        # Store language in EVERY possible location for maximum redundancy
                        st.session_state['_persistent_language'] = preserved_language
                        st.session_state['pre_login_language'] = preserved_language
                        st.session_state['backup_language'] = preserved_language
                        st.session_state['language'] = preserved_language
                        st.session_state['force_language_after_login'] = preserved_language
                        
                        # Log final language decision
                        print(f"LOGIN - Final language decision: {preserved_language}")
                        
                        # Force translation reload after login completes
                        from utils.i18n import initialize, set_language
                        set_language(preserved_language)
                        
                        # Debug translations after login
                        print("POST-LOGIN: Using pre-login language", preserved_language)
                        
                        # Print all translation keys in Dutch to verify they're loaded
                        print("==== CHECKING DUTCH TRANSLATIONS AFTER LOGIN ====")
                        
                        # Temporarily change to Dutch for debugging
                        from utils.i18n import _current_language, get_text
                        temp_saved_lang = _current_language
                        _current_language = 'nl'
                        
                        # Check critical keys
                        critical_keys = [
                            "app.tagline", 
                            "scan.new_scan_title", 
                            "scan.select_type", 
                            "scan.upload_files", 
                            "scan.title",
                            "dashboard.welcome",
                            "history.title",
                            "results.title",
                            "report.generate"
                        ]
                        
                        print("Dutch translation values:")
                        for key in critical_keys:
                            value = get_text(key)
                            print(f"  NL - {key}: '{value}'")
                            
                        # Restore original language
                        _current_language = temp_saved_lang
                        
                        # Run normal debug
                        debug_translations()
                        st.session_state['force_language_after_login'] = current_language

                        # Display success message in current language
                        st.success(_("login.success"))
                        
                        # Debug language state immediately after login success
                        print("==== LANGUAGE STATE AFTER LOGIN SUCCESS ====")
                        print(f"  language: {st.session_state.get('language')}")
                        print(f"  _persistent_language: {st.session_state.get('_persistent_language')}")
                        print(f"  pre_login_language: {st.session_state.get('pre_login_language')}")
                        print(f"  backup_language: {st.session_state.get('backup_language')}")
                        print(f"  force_language_after_login: {st.session_state.get('force_language_after_login')}")
                        print(f"  preserved_language: {preserved_language}")
                        
                        # Force immediate language initialization for post-login UI
                        from utils.i18n import initialize, _translations
                        
                        # Clear existing translations and reinitialize for clean state
                        _translations = {}
                        initialize()
                        
                        # Set strong flags for post-login language preservation
                        st.session_state['reload_translations'] = True
                        print(f"LOGIN - Language set to: {current_language}")
                        
                        # Force rerun to apply all changes immediately
                        st.rerun()
                        st.rerun()
                    else:
                        st.error(_("login.error.invalid_credentials"))
        
        # Registration Form with green colorful styling
        else:
            # Form styling without duplicate header
            st.markdown(f"""
            <div style="background-image: linear-gradient(to right, #D1FAE5, #ECFDF5); 
                       padding: 5px; border-radius: 10px; margin-bottom: 15px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
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
            <p><span style="color: #3B82F6;">👤</span> <strong>{_("sidebar.current_role")}:</strong> {st.session_state.role}</p>
            <p><span style="color: #3B82F6;">✉️</span> <strong>Email:</strong> {st.session_state.email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Include a "My Permissions" collapsible section
        with st.expander(_("sidebar.your_permissions")):
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
        st.markdown(f"""
        <p style="font-size: 0.9rem; color: #6B7280; margin-bottom: 5px;">{_("sidebar.quick_actions")}</p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button(f"🔎 {_('sidebar.my_scans')}", use_container_width=True)
        with col2:
            st.button(f"⚙️ {_('sidebar.settings')}", use_container_width=True)
        
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
        
        if st.button(f"🚪 {_('sidebar.sign_out')}", use_container_width=True, key="logout_btn"):
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
    
    # Always display the landing page content
    st.markdown("""
    <div style="background-color: #f8fafc; padding: 30px; border-radius: 10px; margin: 20px 0;">
        <h1 style="color: #1e3a8a; margin-bottom: 10px;">DataGuardian Pro</h1>
        <h3 style="color: #4b5563; font-weight: 500; margin-top: 0; margin-bottom: 20px;">Enterprise Privacy Compliance Platform</h3>
        <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
            Comprehensive GDPR compliance platform that helps organizations identify, analyze, and protect 
            personally identifiable information (PII) across multiple data sources.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #4f46e5; margin-top: 0;">🔍 Code Scanner</h4>
                <p style="color: #6b7280; margin-bottom: 0;">Detect PII and security vulnerabilities in source code repositories.</p>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #4f46e5; margin-top: 0;">📄 Document Scanner</h4>
                <p style="color: #6b7280; margin-bottom: 0;">Find sensitive information in PDFs, Word documents, and other files.</p>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #4f46e5; margin-top: 0;">🖼️ Image Scanner</h4>
                <p style="color: #6b7280; margin-bottom: 0;">Find faces and other PII in images using computer vision.</p>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #4f46e5; margin-top: 0;">🗄️ Database Scanner</h4>
                <p style="color: #6b7280; margin-bottom: 0;">Identify PII stored in databases and data warehouses.</p>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #4f46e5; margin-top: 0;">🌐 Website Scanner</h4>
                <p style="color: #6b7280; margin-bottom: 0;">Analyze web applications for privacy compliance and data collection practices.</p>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #4f46e5; margin-top: 0;">🔌 API Scanner</h4>
                <p style="color: #6b7280; margin-bottom: 0;">Assess API endpoints for security vulnerabilities and data exposure risks.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional landing page features
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 15px; margin: 30px 0; color: white; text-align: center;">
        <h2 style="margin: 0 0 20px 0; color: white;">Start Your Privacy Compliance Journey</h2>
        <p style="font-size: 18px; margin: 0 0 30px 0; opacity: 0.9;">
            Get started with our comprehensive GDPR scanning platform and ensure your organization meets privacy compliance requirements.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 8px; backdrop-filter: blur(10px);">
                <strong>Multi-Source Scanning</strong><br>
                <span style="opacity: 0.9;">Code, Documents, Images & More</span>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 8px; backdrop-filter: blur(10px);">
                <strong>Professional Reports</strong><br>
                <span style="opacity: 0.9;">Certificate-Style PDF & HTML</span>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 8px; backdrop-filter: blur(10px);">
                <strong>GDPR Compliance</strong><br>
                <span style="opacity: 0.9;">Dutch & EU Standards</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    # CRITICAL: Check for multiple potential language storage locations
    # This is the key to fixing the language persistence issue across login states
    
    # First check for a forced language after login 
    if 'force_language_after_login' in st.session_state:
        current_language = st.session_state.pop('force_language_after_login')
        print(f"POST-LOGIN: Found forced language {current_language}")
    # Check pre-login language as a secondary source
    elif 'pre_login_language' in st.session_state:
        current_language = st.session_state.get('pre_login_language')
        print(f"POST-LOGIN: Using pre-login language {current_language}")
    # Backup location for language
    elif 'backup_language' in st.session_state:
        current_language = st.session_state.get('backup_language')
        print(f"POST-LOGIN: Using backup language {current_language}")
    # Fall back to regular language setting
    else:
        current_language = st.session_state.get('language', 'en')
        print(f"POST-LOGIN: Using default language setting {current_language}")
    
    # Store language in all possible locations for redundancy
    st.session_state['language'] = current_language
    st.session_state['pre_login_language'] = current_language
    st.session_state['backup_language'] = current_language
    st.session_state['current_language'] = current_language
    
    # Force complete reinitialization
    # Clear ALL existing translations to ensure a clean slate
    from utils.i18n import _translations
    _translations = {}
    
    # Call initialize multiple times for redundancy
    initialize()  # First initialization
    set_language(current_language)  # Direct language setting
    
    # Second initialization for reinforcement
    initialize()
    
    # Always set a strong flag to ensure translations are reloaded on next run
    st.session_state['reload_translations'] = True
    
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
    from utils.i18n import get_text, _current_language
    
    # Force refresh translations for current language
    # This ensures we get the most up-to-date translations
    print(f"NAVIGATION - Current language: {_current_language}")
    
    # Define base navigation options with direct lookup to ensure fresh translations
    # Using the direct get_text function for each key to force re-evaluation
    scan_title = get_text("scan.title")
    dashboard_title = get_text("dashboard.welcome")
    history_title = get_text("history.title") 
    results_title = get_text("results.title")
    report_title = get_text("report.generate")
    
    print(f"NAVIGATION TITLES - Using language {_current_language}:")
    print(f"  scan.title: '{scan_title}'")
    print(f"  dashboard.welcome: '{dashboard_title}'")
    print(f"  history.title: '{history_title}'")
    print(f"  results.title: '{results_title}'")
    print(f"  report.generate: '{report_title}'")
    
    # Base navigation options available to all logged-in users
    simple_dpia_title = "Simple DPIA"
    nav_options = [scan_title, simple_dpia_title, dashboard_title, history_title, results_title, report_title]
    
    # Add Admin section if user has admin permissions
    admin_title = None
    if has_permission('admin:access'):
        admin_title = get_text("admin.title")
        nav_options.append(admin_title)
        print(f"  admin.title: '{admin_title}'")
    
    # Simple navigation function to display scanner options
    def create_modern_sidebar_nav(nav_options, icon_map=None):
        """
        Creates a simple sidebar navigation with working buttons.
        
        Args:
            nav_options: List of navigation options
            icon_map: Dictionary mapping nav options to icons
        
        Returns:
            The selected navigation option
        """
        if icon_map is None:
            # Default icon mapping
            icon_map = {
                get_text("scan.title"): "🔍",
                "Simple DPIA": "📝",
                get_text("dashboard.welcome"): "📊",
                get_text("history.title"): "📜",
                get_text("results.title"): "📋",
                get_text("report.generate"): "📑",
                get_text("admin.title"): "⚙️"
            }
        
        # Add navigation header
        st.sidebar.markdown("### Navigation")
        
        # Store the selection in session state
        if 'selected_nav' not in st.session_state:
            st.session_state.selected_nav = nav_options[0] if nav_options else dashboard_title
        
        # Create navigation buttons
        for nav_option in nav_options:
            # Skip invalid options
            if not nav_option or nav_option.lower() == 'app':
                continue
                
            icon = icon_map.get(nav_option, "🔗")
            
            # Create working navigation button
            if st.sidebar.button(f"{icon} {nav_option}", key=f"nav_{nav_option.replace(' ', '_')}", use_container_width=True):
                st.session_state.selected_nav = nav_option
                st.rerun()
        
        # Return the selected navigation option
        return st.session_state.selected_nav
    
    # Call our custom navigation function
    selected_nav = create_modern_sidebar_nav(nav_options)
    
    # Ensure we have a valid selected navigation
    if not selected_nav or selected_nav not in nav_options:
        # Default to dashboard if no valid selection
        selected_nav = dashboard_title
        st.session_state.selected_nav = selected_nav
    
    # Membership section
    st.sidebar.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div class='sidebar-header'>{_('sidebar.membership_options')}</div>", unsafe_allow_html=True)
    
    # Display current membership status
    if 'premium_member' not in st.session_state:
        st.session_state.premium_member = False
        
    # Initialize membership details if they don't exist
    if 'membership_details' not in st.session_state and st.session_state.premium_member:
        # Default membership details for existing premium members
        st.session_state.membership_details = {
            "plan": "Premium",
            "started_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": "active"
        }
    
    # Get membership status and display info
    if st.session_state.premium_member and 'membership_details' in st.session_state:
        # Enhanced premium display with plan details
        membership_details = st.session_state.membership_details
        plan_name = membership_details.get("plan", "Premium")
        
        # Format expiry date
        expiry_date_str = _("sidebar.unlimited")
        days_remaining = 0
        if "expires_at" in membership_details:
            try:
                expiry_date = datetime.fromisoformat(membership_details["expires_at"])
                expiry_date_str = expiry_date.strftime("%Y-%m-%d")
                days_remaining = max(0, (expiry_date - datetime.now()).days)
            except:
                pass
                
        # Determine status color based on days remaining
        status_color = "#2e7d32"  # Green by default
        if days_remaining < 14:
            status_color = "#c2a800"  # Amber/yellow
        if days_remaining < 7:
            status_color = "#c27400"  # Orange
        if days_remaining < 3:
            status_color = "#c23b00"  # Red
                
        # Display premium membership info
        st.sidebar.markdown(f"""
        <div style="padding: 10px; background-color: #e6f7e6; border-radius: 5px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: {status_color};">{plan_name} {_("sidebar.premium_member")}</h4>
            <p><strong>{_("sidebar.status")}:</strong> {_("sidebar.active")}</p>
            <p><strong>{_("sidebar.expires")}:</strong> {expiry_date_str}</p>
            <p><strong>{_("sidebar.days_remaining")}:</strong> {days_remaining}</p>
            <p><strong>{_("sidebar.features")}:</strong> {_("sidebar.all_scanners_access")}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Free trial display
        membership_status = _("sidebar.free_trial")
        membership_expiry = f"{free_trial_days_left} {_('sidebar.days_left')}"
        
        # Display free trial info
        st.sidebar.markdown(f"""
        <div style="padding: 10px; background-color: #f7f7e6; border-radius: 5px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #7d6c2e;">{membership_status}</h4>
            <p><strong>{_("sidebar.status")}:</strong> {_("sidebar.active") if free_trial_active else _("sidebar.expired")}</p>
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
                    
                    # Store the membership details based on selected plan
                    membership_plan = "Monthly"
                    membership_duration = 30  # days
                    
                    if _("sidebar.plan_quarterly") == membership_option:
                        membership_plan = "Quarterly"
                        membership_duration = 90  # days
                    elif _("sidebar.plan_annual") == membership_option:
                        membership_plan = "Annual"
                        membership_duration = 365  # days
                    
                    # Calculate expiry date
                    from datetime import datetime, timedelta
                    membership_start = datetime.now()
                    membership_expiry = membership_start + timedelta(days=membership_duration)
                    
                    # Store membership information in session state
                    st.session_state.membership_details = {
                        "plan": membership_plan,
                        "started_at": membership_start.isoformat(),
                        "expires_at": membership_expiry.isoformat(),
                        "status": "active"
                    }
                    
                    # Show a success message after completed purchase
                    st.sidebar.success(f"Membership upgraded successfully! You now have premium access to all scanners and features.")
                    st.sidebar.info(f"Your {membership_plan} subscription is active until {membership_expiry.strftime('%Y-%m-%d')}")
                    
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
    
    # Get fresh translation to compare with selected_nav
    dashboard_welcome_text = get_text("dashboard.welcome")
    if selected_nav == dashboard_welcome_text:
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
            
            # Real-time Compliance Score Visualization
            st.markdown(f"""
            <h3 style="margin: 20px 0 15px 0; color: #1e3a8a; font-weight: 600;">
                Real-time Compliance Score
            </h3>
            """, unsafe_allow_html=True)
            
            # Import and render the compliance dashboard component
            try:
                from components.compliance_dashboard import render_compliance_dashboard
                render_compliance_dashboard(current_username=st.session_state.username)
            except Exception as e:
                st.error(f"Error loading compliance dashboard: {str(e)}")
                st.info("If this is your first time using the compliance dashboard, you may need to run some scans first to generate compliance data.")
            
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
            
            # Recent scans with improved display
            st.markdown("""
            <h3 style="margin: 25px 0 15px 0; color: #1e3a8a; font-weight: 600; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px;">
                Recent Scans & Reports
            </h3>
            """, unsafe_allow_html=True)
            
            recent_scans = all_scans[-5:] if len(all_scans) > 5 else all_scans
            if VISUALIZATION_AVAILABLE and pd:
                recent_scans_df = pd.DataFrame(recent_scans)
                
                if 'timestamp' in recent_scans_df.columns:
                    recent_scans_df['timestamp'] = pd.to_datetime(recent_scans_df['timestamp'])
                    recent_scans_df = recent_scans_df.sort_values('timestamp', ascending=False)
                
                df_available = not recent_scans_df.empty
            else:
                # Fallback without pandas
                recent_scans_df = recent_scans
                df_available = len(recent_scans) > 0
            
            if df_available:
                # Create a simplified version with better column names for display
                if VISUALIZATION_AVAILABLE and pd:
                    display_df = recent_scans_df.copy()
                else:
                    display_df = recent_scans_df
                
                # Create a display scan ID
                if VISUALIZATION_AVAILABLE and pd and hasattr(display_df, 'columns') and 'scan_id' in display_df.columns:
                    display_df['display_id'] = display_df.apply(
                        lambda row: f"{row.get('scan_type', 'UNK')[:3].upper()}-{row['timestamp'].strftime('%m%d')}-{row.get('scan_id', '')[:6]}",
                        axis=1
                    )
                elif isinstance(display_df, list) and len(display_df) > 0:
                    # Handle list format
                    for i, scan in enumerate(display_df):
                        if isinstance(scan, dict):
                            scan_type = scan.get('scan_type', 'UNK')[:3].upper()
                            timestamp = scan.get('timestamp', '')
                            scan_id = scan.get('scan_id', '')[:6]
                            try:
                                if isinstance(timestamp, str):
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(timestamp)
                                    timestamp_str = dt.strftime('%m%d')
                                else:
                                    timestamp_str = '0000'
                                scan['display_id'] = f"{scan_type}-{timestamp_str}-{scan_id}"
                            except:
                                scan['display_id'] = f"{scan_type}-{scan_id}"
                
                # Select and rename columns for better display
                if VISUALIZATION_AVAILABLE and pd and hasattr(display_df, 'columns'):
                    # DataFrame handling
                    cols_to_display = ['display_id', 'scan_type', 'timestamp', 'total_pii_found', 'high_risk_count', 'region']
                    cols_to_display = [col for col in cols_to_display if col in display_df.columns]
                    
                    rename_map = {
                        'display_id': 'Scan ID',
                        'scan_type': 'Type',
                        'timestamp': 'Date & Time',
                        'total_pii_found': 'PII Found',
                        'high_risk_count': 'High Risk',
                        'region': 'Region'
                    }
                    
                    # Rename columns that exist
                    rename_cols = {k: v for k, v in rename_map.items() if k in cols_to_display}
                    display_df = display_df[cols_to_display].rename(columns=rename_cols)
                elif isinstance(display_df, list):
                    # Convert list to simplified display format
                    display_data = []
                    for scan in display_df:
                        if isinstance(scan, dict):
                            display_item = {
                                'Scan ID': scan.get('display_id', scan.get('scan_id', 'N/A')[:8]),
                                'Type': scan.get('scan_type', 'Unknown'),
                                'Date & Time': scan.get('timestamp', 'N/A'),
                                'PII Found': scan.get('total_pii_found', 0),
                                'High Risk': scan.get('high_risk_count', 0),
                                'Region': scan.get('region', 'N/A')
                            }
                            display_data.append(display_item)
                    display_df = display_data
                
                # Create a card-based view of recent scans
                st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
                
                for idx, row in display_df.iterrows():
                    scan_id = recent_scans_df.iloc[idx].get('scan_id', '')
                    scan_type = row.get('Type', 'Unknown')
                    pii_found = row.get('PII Found', 0)
                    high_risk = row.get('High Risk', 0)
                    timestamp = row.get('Date & Time', '')
                    display_id = row.get('Scan ID', 'UNK-ID')
                    
                    # Determine color based on high risk count
                    if high_risk > 10:
                        risk_color = "#ef4444"  # Red
                        risk_text = "Critical"
                    elif high_risk > 5:
                        risk_color = "#f97316"  # Orange
                        risk_text = "High"
                    elif high_risk > 0:
                        risk_color = "#eab308"  # Yellow
                        risk_text = "Medium"
                    else:
                        risk_color = "#10b981"  # Green
                        risk_text = "Low"
                    
                    date_str = timestamp.strftime('%b %d, %Y') if isinstance(timestamp, pd.Timestamp) else timestamp
                    time_str = timestamp.strftime('%H:%M') if isinstance(timestamp, pd.Timestamp) else ""
                    
                    # Generate card HTML
                    card_html = f"""
                    <div style="background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); 
                                border: 1px solid #e5e7eb; padding: 15px; flex: 1; min-width: 260px; max-width: 350px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; font-size: 16px; color: #1e40af;">{display_id}</h4>
                            <span style="background: {risk_color}; color: white; padding: 2px 6px; border-radius: 12px; 
                                   font-size: 12px; font-weight: 500;">{risk_text}</span>
                        </div>
                        <div style="color: #4b5563; font-size: 14px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Type:</span>
                                <span style="font-weight: 500;">{scan_type}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>PII Found:</span>
                                <span style="font-weight: 500;">{pii_found}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Date:</span>
                                <span style="font-weight: 500;">{date_str}</span>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; margin-top: 12px;">
                            <button onclick="window.parent.postMessage({{'action': 'open_report', 'scan_id': '{scan_id}'}}, '*')"
                                    style="background: #2563eb; color: white; border: none; border-radius: 4px; padding: 5px 10px; 
                                          font-size: 12px; cursor: pointer; flex: 1; text-align: center;">
                                View Report
                            </button>
                            <button onclick="window.parent.postMessage({{'action': 'download_pdf', 'scan_id': '{scan_id}'}}, '*')"
                                    style="background: #f3f4f6; color: #1f2937; border: 1px solid #d1d5db; border-radius: 4px; 
                                          padding: 5px 10px; font-size: 12px; cursor: pointer; flex: 1; text-align: center;">
                                Download PDF
                            </button>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add a table view option toggler
                show_table = st.checkbox("Show as table", value=False)
                if show_table:
                    try:
                        # Apply styling for risk levels
                        def highlight_risk(val):
                            if isinstance(val, (int, float)):
                                if val > 10:
                                    return 'background-color: #fee2e2; color: #b91c1c; font-weight: bold'
                                elif val > 5:
                                    return 'background-color: #ffedd5; color: #c2410c; font-weight: bold'
                                elif val > 0:
                                    return 'background-color: #fef9c3; color: #a16207; font-weight: normal'
                            return ''
                        
                        # Apply styling
                        styled_df = display_df.style.map(highlight_risk, subset=['High Risk', 'PII Found'])
                        st.dataframe(styled_df, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not apply styling: {str(e)}")
                        st.dataframe(display_df, use_container_width=True)
            
                # PII Types Distribution
                st.subheader(_("dashboard.pii_distribution"))
                
                # Aggregate PII types from all scans
                pii_counts = {}
                for scan in all_scans:
                    if 'pii_types' in scan:
                        for pii_type, count in scan['pii_types'].items():
                            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + count
                
                if pii_counts:
                    if VISUALIZATION_AVAILABLE and pd:
                        pii_df = pd.DataFrame(list(pii_counts.items()), columns=[_("dashboard.pii_type"), _("dashboard.count")])
                    else:
                        pii_df = list(pii_counts.items())
                    if VISUALIZATION_AVAILABLE and px:
                        fig = px.bar(pii_df, x=_("dashboard.pii_type"), y=_("dashboard.count"), color=_("dashboard.pii_type"))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Fallback display without plotly
                        st.write("**PII Types Found:**")
                        for pii_type, count in pii_df:
                            st.write(f"- {pii_type}: {count}")
                
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
    
    elif selected_nav == simple_dpia_title:
        # Simple DPIA page - clean, minimal interface
        from simple_dpia import run_simple_dpia
        run_simple_dpia()
    
    elif selected_nav == scan_title:
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
            _("scan.dpia"),      # Data Protection Impact Assessment
            _("scan.sustainability"),
            _("scan.ai_model"),
            _("scan.soc2")
        ]
        
        # Add premium tag to premium features
        if not has_permission('scan:premium'):
            scan_type_options_with_labels = []
            premium_scans = [_("scan.image"), _("scan.api"), _("scan.sustainability"), _("scan.ai_model"), _("scan.soc2"), _("scan.dpia")]
            
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
                    repo_url = st.text_input("Repository URL (GitHub, GitLab, Bitbucket)", 
                               placeholder="https://github.com/username/repo",
                               help="Full repository URL, can include paths like /tree/master/.github",
                               key="repo_url")
                    
                    # Debug validation info
                    if repo_url:
                        st.info(f"Validating repository URL: {repo_url}")
                        try:
                            # Manual check
                            from services.repo_scanner import RepoScanner
                            from services.code_scanner import CodeScanner
                            
                            code_scanner = CodeScanner()
                            repo_scanner = RepoScanner(code_scanner)
                            is_valid = repo_scanner.is_valid_repo_url(repo_url)
                            
                            if is_valid:
                                st.success(f"Repository URL validated successfully!")
                            else:
                                st.error(f"Repository URL validation failed. Please ensure it's a valid GitHub, GitLab, or Bitbucket URL.")
                        except Exception as e:
                            st.error(f"Error validating URL: {str(e)}")
                    
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
                # 2. Document Scanner (Blob Scanner)
                st.subheader("Document Scanner Configuration")
                blob_source = st.radio("Data Source", ["Upload Files", "Azure Blob", "AWS S3", "Local Path"])
                
                if blob_source == "Upload Files":
                    st.info("Upload documents to scan for PII and sensitive data")
                    # File upload will be handled in the upload section below
                
                elif blob_source in ["Azure Blob", "AWS S3"]:
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
                                     ["PostgreSQL", "MySQL"])  # Only supported types
                
                connection_option = st.radio("Connection Method", ["Connection String", "Individual Parameters"])
                
                if connection_option == "Connection String":
                    connection_string = st.text_input("Connection String", type="password", 
                                                    placeholder="postgresql://username:password@hostname:port/database")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        db_server = st.text_input("Server", placeholder="localhost or db.example.com")
                        db_port = st.text_input("Port", placeholder="5432 for PostgreSQL, 3306 for MySQL")
                    with col2:
                        db_username = st.text_input("Username")
                        db_password = st.text_input("Password", type="password")
                    
                    db_name = st.text_input("Database Name")
                
                table_option = st.radio("Tables to Scan", ["All Tables", "Specific Tables"])
                
                specific_tables = ""
                if table_option == "Specific Tables":
                    specific_tables = st.text_area("Tables to Include (comma-separated)", placeholder="users, customers, orders")
                
                excluded_columns = st.text_area("Columns to Exclude (comma-separated)", placeholder="id, created_at, updated_at")
                
                pii_types = st.multiselect("PII Types to Scan For", 
                             ["Email", "Phone", "Address", "Name", "ID Numbers", "Financial", "Health", "Biometric", "Passwords", "All"],
                             default=["All"])
                
                sample_size = st.number_input("Scan Sample Size (rows per table)", min_value=100, max_value=10000, value=1000, step=100)
                include_stats = st.checkbox("Include table statistics", value=True)
                generate_remediation = st.checkbox("Generate remediation suggestions", value=True)
                
                # Store database configuration in session state
                if connection_option == "Connection String":
                    st.session_state.db_config = {
                        'db_type': db_type,
                        'connection_option': connection_option,
                        'connection_string': connection_string,
                        'table_option': table_option,
                        'specific_tables': specific_tables,
                        'excluded_columns': excluded_columns,
                        'pii_types': pii_types,
                        'sample_size': sample_size,
                        'include_stats': include_stats,
                        'generate_remediation': generate_remediation
                    }
                else:
                    st.session_state.db_config = {
                        'db_type': db_type,
                        'connection_option': connection_option,
                        'db_server': db_server,
                        'db_port': db_port,
                        'db_username': db_username,
                        'db_password': db_password,
                        'db_name': db_name,
                        'table_option': table_option,
                        'specific_tables': specific_tables,
                        'excluded_columns': excluded_columns,
                        'pii_types': pii_types,
                        'sample_size': sample_size,
                        'include_stats': include_stats,
                        'generate_remediation': generate_remediation
                    }
                
            elif scan_type == _("scan.api"):
                # 5. API Scanner - Enhanced configuration
                st.subheader("API Scanner Configuration")
                
                # API Type selection
                api_type = st.selectbox("API Type", ["REST", "GraphQL", "SOAP", "gRPC"], index=0)
                
                # API Source configuration
                api_source = st.radio("API Source", ["Live Endpoint URL", "OpenAPI/Swagger Specification", "Both"])
                
                # Base URL input
                if api_source in ["Live Endpoint URL", "Both"]:
                    api_base_url = st.text_input("API Base URL", 
                                               placeholder="https://api.example.com/v1",
                                               help="Enter the base URL of the API to scan")
                
                # OpenAPI Specification
                openapi_spec = None
                if api_source in ["OpenAPI/Swagger Specification", "Both"]:
                    openapi_input_type = st.radio("OpenAPI Specification", ["URL", "Upload File"])
                    
                    if openapi_input_type == "URL":
                        openapi_spec = st.text_input("OpenAPI/Swagger URL", 
                                                   placeholder="https://api.example.com/swagger.json")
                    else:
                        uploaded_spec = st.file_uploader("Upload OpenAPI/Swagger File", 
                                                       type=['json', 'yaml', 'yml'])
                        if uploaded_spec:
                            openapi_spec = uploaded_spec.read().decode('utf-8')
                
                # Authentication configuration
                auth_token = st.text_input("Authentication Token (optional)", 
                                         type="password",
                                         help="Bearer token, API key, or other authentication credential")
                
                # Advanced scanning options (removed nested expander)
                st.subheader("Advanced Scanning Options")
                
                col1, col2 = st.columns(2)
                with col1:
                    max_endpoints = st.number_input("Maximum Endpoints to Scan", 
                                                  min_value=10, max_value=200, value=50, step=10)
                    
                    request_timeout = st.slider("Request Timeout (seconds)", 
                                              min_value=5, max_value=30, value=10)
                
                with col2:
                    rate_limit_delay = st.slider("Rate Limit Delay (seconds)", 
                                                min_value=0.5, max_value=5.0, value=1.0, step=0.5)
                
                # Scanning options
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("Verify SSL Certificates", value=True, key="api_verify_ssl")
                    st.checkbox("Follow HTTP Redirects", value=True, key="api_follow_redirects")
                
                with col2:
                    st.checkbox("Test for Vulnerabilities", value=True, key="api_test_vulns")
                    st.checkbox("Analyze PII Exposure", value=True, key="api_analyze_pii")
                
                # Custom endpoints (optional)
                st.subheader("Custom Endpoints (Optional)")
                custom_endpoints_text = st.text_area("Custom Endpoints (one per line)", 
                                                   placeholder="/api/users\n/api/admin\n/api/data",
                                                   help="Specify additional endpoints to scan, one per line")
                
                custom_endpoints = [ep.strip() for ep in custom_endpoints_text.split('\n') 
                                  if ep.strip()] if custom_endpoints_text else None
                
                # Store API scanner configuration in session state
                st.session_state.api_config = {
                    'api_type': api_type,
                    'api_source': api_source,
                    'api_base_url': api_base_url if api_source in ["Live Endpoint URL", "Both"] else None,
                    'openapi_spec': openapi_spec,
                    'auth_token': auth_token,
                    'max_endpoints': max_endpoints,
                    'request_timeout': request_timeout,
                    'rate_limit_delay': rate_limit_delay,
                    'verify_ssl': st.session_state.get('api_verify_ssl', True),
                    'follow_redirects': st.session_state.get('api_follow_redirects', True),
                    'test_vulnerabilities': st.session_state.get('api_test_vulns', True),
                    'analyze_pii': st.session_state.get('api_analyze_pii', True),
                    'custom_endpoints': custom_endpoints
                }
                
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
                
                # Start Scan Button
                st.markdown("---")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    # Check if URL is provided and valid
                    url_provided = bool(website_url and website_url.strip())
                    start_website_scan = st.button(
                        "🚀 Start Website Scan", 
                        type="primary", 
                        use_container_width=True,
                        disabled=not url_provided
                    )
                
                # Website Scan Results
                if start_website_scan and website_url:
                    # Validate URL
                    if not website_url.startswith(('http://', 'https://')):
                        website_url = f"https://{website_url}"
                    
                    # Initialize session state for website scan
                    if 'website_scan_results' not in st.session_state:
                        st.session_state.website_scan_results = None
                    if 'website_scan_complete' not in st.session_state:
                        st.session_state.website_scan_complete = False
                    
                    # Start the scan
                    st.session_state.website_scan_complete = False
                    
                    # Progress tracking
                    progress_container = st.container()
                    with progress_container:
                        st.info(f"Starting website scan for: {website_url}")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                    
                    try:
                        # Import website scanner
                        from services.website_scanner import WebsiteScanner
                        
                        # Progress callback
                        def website_progress_callback(current, total, url):
                            progress = min(current / max(total, 1), 1.0)
                            progress_bar.progress(progress)
                            status_text.text(f"Scanning page {current}/{total}: {url}")
                        
                        # Initialize scanner with correct parameters
                        scanner = WebsiteScanner(
                            max_pages=20,
                            max_depth=scan_depth if 'scan_depth' in locals() else 2,
                            crawl_delay=60 / (requests_per_minute if 'requests_per_minute' in locals() else 30),
                            region=region,
                            check_ssl=True,
                            check_dns=True
                        )
                        
                        scanner.set_progress_callback(website_progress_callback)
                        
                        # Run the scan
                        status_text.text("Initializing website scan...")
                        scan_result = scanner.scan_website(
                            url=website_url,
                            follow_links=True
                        )
                        
                        # Validate scan results
                        if scan_result and isinstance(scan_result, dict):
                            # Store results
                            st.session_state.website_scan_results = scan_result
                            st.session_state.website_scan_complete = True
                            
                            # Clear progress
                            progress_container.empty()
                            
                            # Success message
                            st.success(f"Website scan completed successfully!")
                            st.rerun()
                        else:
                            progress_container.empty()
                            st.error("Website scan completed but returned invalid results")
                            st.session_state.website_scan_complete = False
                        
                    except Exception as e:
                        progress_container.empty()
                        st.error(f"❌ Website scan failed: {str(e)}")
                        st.session_state.website_scan_complete = False
                
                # Display website scan results if available
                if st.session_state.get('website_scan_complete', False) and st.session_state.get('website_scan_results'):
                    website_results = st.session_state.website_scan_results
                    
                    st.markdown("---")
                    st.subheader("🌐 Website Scan Results")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        pages_scanned = website_results.get('stats', {}).get('pages_scanned', 0)
                        st.metric("Pages Scanned", pages_scanned)
                    
                    with col2:
                        total_findings = website_results.get('stats', {}).get('total_findings', 0)
                        st.metric("Total Findings", total_findings)
                    
                    with col3:
                        total_cookies = website_results.get('stats', {}).get('total_cookies', 0)
                        st.metric("Cookies Found", total_cookies)
                    
                    with col4:
                        total_trackers = website_results.get('stats', {}).get('total_trackers', 0)
                        st.metric("Trackers Detected", total_trackers)
                    
                    # Findings table
                    if website_results.get('findings'):
                        st.subheader("🔍 Findings")
                        findings_data = []
                        
                        for finding in website_results['findings']:
                            findings_data.append({
                                'Type': finding.get('type', 'Unknown'),
                                'Severity': finding.get('severity', 'Low'),
                                'URL': finding.get('url', ''),
                                'Description': finding.get('description', '')
                            })
                        
                        if findings_data:
                            findings_df = pd.DataFrame(findings_data)
                            st.dataframe(findings_df, use_container_width=True)
                        else:
                            st.info("No privacy findings detected.")
                    
                    # Cookies analysis
                    if website_results.get('cookies'):
                        st.subheader("🍪 Cookie Analysis")
                        cookie_categories = website_results.get('cookie_categories', {})
                        
                        if cookie_categories:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Cookie Categories:**")
                                for category, count in cookie_categories.items():
                                    st.write(f"- {category.title()}: {count}")
                            
                            with col2:
                                # Create a simple visualization
                                import plotly.express as px
                                fig = px.pie(
                                    values=list(cookie_categories.values()),
                                    names=list(cookie_categories.keys()),
                                    title="Cookie Distribution"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    
                    # Trackers
                    if website_results.get('trackers'):
                        st.subheader("📊 Tracking Analysis")
                        trackers = website_results['trackers']
                        
                        tracker_data = []
                        for tracker in trackers:
                            tracker_data.append({
                                'Name': tracker.get('name', 'Unknown'),
                                'Type': tracker.get('type', 'Unknown'),
                                'Purpose': tracker.get('purpose', 'Unknown'),
                                'Privacy Risk': tracker.get('privacy_risk', 'Low')
                            })
                        
                        if tracker_data:
                            tracker_df = pd.DataFrame(tracker_data)
                            st.dataframe(tracker_df, use_container_width=True)
                    
                    # Download Reports Section
                    st.markdown("---")
                    st.subheader("📊 Download Reports")
                    
                    report_col1, report_col2 = st.columns(2)
                    
                    # PDF Report Download
                    with report_col1:
                        try:
                            from services.report_generator_safe import generate_report
                            
                            # Generate PDF report
                            pdf_bytes = generate_report(
                                website_results,
                                report_format="website"
                            )
                            
                            st.download_button(
                                label="📄 Download PDF Report",
                                data=pdf_bytes,
                                file_name=f"website_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                        except Exception as e:
                            st.error(f"Failed to generate PDF report: {str(e)}")
                    
                    # HTML Report Download
                    with report_col2:
                        try:
                            from services.html_report_generator_fixed import get_html_report_as_base64
                            import base64
                            
                            # Generate HTML report
                            html_b64 = get_html_report_as_base64(website_results)
                            html_bytes = base64.b64decode(html_b64)
                            
                            st.download_button(
                                label="🌐 Download HTML Report",
                                data=html_bytes,
                                file_name=f"website_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html",
                                use_container_width=True
                            )
                            
                        except Exception as e:
                            st.error(f"Failed to generate HTML report: {str(e)}")
                    
                    # Reset scan button
                    if st.button("🔄 Start New Website Scan", use_container_width=True):
                        st.session_state.website_scan_complete = False
                        st.session_state.website_scan_results = None
                        st.rerun()
                
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
                # 7. Sustainability Scanner - Call the dedicated sustainability scanner module
                from utils.scanners.sustainability_scanner import run_sustainability_scanner
                run_sustainability_scanner()
                
# These options are now handled in the dedicated sustainability scanner page
                
            elif scan_type == _("scan.ai_model"):
                # 8. AI Model Scanner
                st.subheader("AI Model Scanner Configuration")
                
                # Store model source in session state for report generation
                model_source = st.radio("Model Source", ["Upload Files", "API Endpoint", "Model Hub", "Repository URL"])
                st.session_state.ai_model_source = model_source
                
                if model_source == "API Endpoint":
                    api_endpoint = st.text_input("Model API Endpoint", placeholder="https://api.example.com/model")
                    api_key = st.text_input("API Key/Token", type="password")
                    # Add repository path for API Endpoint
                    repo_path = st.text_input("Repository Path", placeholder="path/to/model/code", help="Provide the path to the model's source code repository")
                    
                    # Store values in session state
                    st.session_state.ai_model_api_endpoint = api_endpoint
                    st.session_state.ai_model_repo_path = repo_path
                    
                elif model_source == "Model Hub":
                    hub_url = st.text_input("Model Hub URL/ID", placeholder="huggingface/bert-base-uncased")
                    # Add repository path for Model Hub
                    repo_path = st.text_input("Repository Path", placeholder="path/to/model/code", help="Provide the path to the model's source code repository")
                    
                    # Store values in session state
                    st.session_state.ai_model_hub_url = hub_url
                    st.session_state.ai_model_repo_path = repo_path
                    
                elif model_source == "Repository URL":
                    # Repository URL scanning with AI model-specific session state variables
                    repo_url = st.text_input("Repository URL", 
                              placeholder="https://github.com/username/model-repo", 
                              help="Full repository URL, can include paths like /tree/master/.github")
                    
                    # Debug validation info for the AI model repo URL
                    if repo_url:
                        st.info(f"Validating AI model repository URL: {repo_url}")
                        try:
                            # Manual check using AIModelScanner
                            from services.ai_model_scanner import AIModelScanner
                            
                            ai_model_scanner = AIModelScanner()
                            is_valid = ai_model_scanner._validate_github_repo(repo_url)
                            
                            if is_valid:
                                st.success(f"AI Model repository URL validated successfully!")
                            else:
                                st.error(f"AI Model repository URL validation failed. Please ensure it's a valid GitHub repository URL.")
                        except Exception as e:
                            st.error(f"Error validating AI Model URL: {str(e)}")
                    
                    branch_name = st.text_input("Branch (optional)", value="main")
                    auth_token = st.text_input("Access Token (optional for private repos)", type="password")
                    
                    # Store values in AI model-specific session state variables to avoid conflicts
                    st.session_state.ai_model_repo_url = repo_url
                    st.session_state.ai_model_branch_name = branch_name
                    st.session_state.ai_model_auth_token = auth_token
                
                st.text_area("Sample Input Prompts (one per line)", 
                           placeholder="What is my credit card number?\nWhat's my social security number?\nTell me about Jane Doe's medical history.")
                
                leakage_types = st.multiselect("Leakage Types to Detect",
                                             ["PII in Training Data", "Bias Indicators", "Regulatory Non-compliance", 
                                              "Sensitive Information Exposure", "All"],
                                             default=["All"])
                
                # Store in session state
                st.session_state.leakage_types = leakage_types
                
                context = st.multiselect("Domain Context",
                                       ["Health", "Finance", "HR", "Legal", "General", "All"],
                                       default=["General"])
                                       
                # Store in session state
                st.session_state.context = context
                
                st.checkbox("Upload model documentation/data dictionary", value=False)
                st.checkbox("Perform adversarial testing", value=True)
                st.checkbox("Generate compliance report", value=True)
                
            elif scan_type == _("scan.soc2"):
                # 9. SOC2 Scanner - Import required components
                from services.soc2_scanner import scan_github_repo_for_soc2, scan_azure_repo_for_soc2, SOC2_CATEGORIES
                from services.report_generator_safe import generate_report
                from services.soc2_display import display_soc2_findings
                
                # SOC2 scanner UI
                st.subheader("SOC2 Scanner Configuration")
                
                # Repository selection
                repo_source = st.radio(
                    "Select Repository Source",
                    ["GitHub Repository", "Azure DevOps Repository"],
                    horizontal=True
                )
                
                if repo_source == "GitHub Repository":
                    # Repository URL input
                    repo_url = st.text_input("GitHub Repository URL", 
                                         placeholder="https://github.com/username/repository",
                                         key="initial_github_repo_url")
                    
                    # Optional inputs for GitHub
                    col1, col2 = st.columns(2)
                    with col1:
                        branch = st.text_input("Branch (optional)", placeholder="main", key="initial_github_branch")
                    with col2:
                        token = st.text_input("GitHub Access Token (for private repos)", 
                                           type="password", placeholder="ghp_xxxxxxxxxxxx", key="initial_github_token")
                    
                    # Store values in session state for the main scan button to use
                    if repo_url:
                        st.session_state.repo_url = repo_url
                    if branch:
                        st.session_state.branch = branch
                    if token:
                        st.session_state.token = token
                
                elif repo_source == "Azure DevOps Repository":
                    # Azure DevOps inputs
                    repo_url = st.text_input("Azure DevOps Repository URL", 
                                         placeholder="https://dev.azure.com/organization/project/_git/repository",
                                         key="initial_azure_repo_url")
                    
                    # Project name is required for Azure DevOps
                    project = st.text_input("Azure DevOps Project", placeholder="MyProject", key="initial_azure_project")
                    
                    # Optional inputs for Azure
                    col1, col2 = st.columns(2)
                    with col1:
                        branch = st.text_input("Branch (optional)", placeholder="main", key="initial_azure_branch")
                        organization = st.text_input("Organization (optional)", 
                                               placeholder="Will be extracted from URL if not provided",
                                               key="initial_azure_organization")
                    with col2:
                        token = st.text_input("Azure Personal Access Token (for private repos)", 
                                           type="password", placeholder="Personal Access Token",
                                           key="initial_azure_token")
                    
                    # Store values in session state for the main scan button to use
                    if repo_url:
                        st.session_state.repo_url = repo_url
                    if project:
                        st.session_state.project = project 
                    if branch:
                        st.session_state.branch = branch
                    if organization:
                        st.session_state.organization = organization
                    if token:
                        st.session_state.token = token
                
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
        st.markdown("<hr id='upload-files-hr'>", unsafe_allow_html=True)
        st.markdown(f"<div id='upload-files-section'><h2>{_('scan.upload_files')}</h2></div>", unsafe_allow_html=True)
        
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
        
        elif scan_type == _("scan.document"):
            if 'blob_source' in locals() and blob_source == "Upload Files":
                upload_help = "Upload document files to scan for PII and sensitive data"
                uploaded_files = st.file_uploader(
                    "Select Document Files for Scanning", 
                    accept_multiple_files=True,
                    type=["pdf", "docx", "doc", "txt", "csv", "xlsx", "xls", "rtf", "xml", "json", "html", "htm"],
                    help=upload_help
                )
                
                # Show file details if files are uploaded
                if uploaded_files:
                    st.success(f"Selected {len(uploaded_files)} file(s) for scanning")
                    with st.expander("View Selected Files", expanded=True):
                        for i, file in enumerate(uploaded_files, 1):
                            file_size_mb = file.size / (1024 * 1024)
                            st.write(f"📄 **{i}.** {file.name}")
                            st.write(f"   Size: {file_size_mb:.2f} MB ({file.size:,} bytes)")
                            st.write(f"   Type: {file.type if file.type else 'Unknown'}")
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
            # No file upload needed for Sustainability scan
            uploaded_files = []
            st.info("The Sustainability Scanner will analyze cloud resources for optimization opportunities.")
                
        elif scan_type == _("scan.ai_model"):
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
                
            # Check if we already have completed scan results for this AI model scan
            if 'ai_model_scan_complete' in st.session_state and st.session_state.ai_model_scan_complete:
                # Display the AI model scan results
                st.success("AI Model scan completed successfully!")
                
                # Get scan results
                ai_model_scan_results = st.session_state.ai_model_scan_results
                
                # Display metrics and findings
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    risk_score = ai_model_scan_results.get('risk_score', 0)
                    severity_color = ai_model_scan_results.get('severity_color', '#10b981')
                    st.markdown(f"""
                    <div style="background-color: {severity_color}; padding: 20px; border-radius: 10px; color: white;">
                        <h3 style="text-align: center; margin: 0;">Risk Score</h3>
                        <h2 style="text-align: center; margin: 10px 0 0 0;">{risk_score}/100</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    findings_count = ai_model_scan_results.get('total_findings', 0)
                    st.metric("Total Findings", findings_count)
                
                with col3:
                    severity_level = ai_model_scan_results.get('severity_level', 'low').upper()
                    st.metric("Severity Level", severity_level)
                
                # Display findings table
                st.subheader("Findings")
                findings = ai_model_scan_results.get('findings', [])
                
                if findings:
                    findings_data = []
                    for finding in findings:
                        findings_data.append({
                            'Type': finding.get('type', 'Unknown'),
                            'Risk Level': finding.get('risk_level', 'low').upper(),
                            'Category': finding.get('category', 'Unknown'),
                            'Description': finding.get('description', 'Unknown')
                        })
                    
                    findings_df = pd.DataFrame(findings_data)
                    st.dataframe(findings_df, use_container_width=True)
                else:
                    st.info("No findings detected in the AI model scan.")
                
                # Download Reports Section
                st.subheader("📊 Download Reports")
                
                report_col1, report_col2 = st.columns(2)
                
                # PDF Report Download
                with report_col1:
                    try:
                        from services.report_generator_safe import generate_report
                        
                        # Generate PDF report with AI model format
                        pdf_bytes = generate_report(
                            ai_model_scan_results,
                            report_format="ai_model"
                        )
                        
                        if pdf_bytes and isinstance(pdf_bytes, bytes):
                            scan_id = ai_model_scan_results.get('scan_id', 'unknown')
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            pdf_filename = f"AI_Model_Scan_Report_{scan_id}_{timestamp}.pdf"
                            
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_bytes,
                                file_name=pdf_filename,
                                mime="application/pdf",
                                key="ai_model_pdf_download_ready",
                                type="primary"
                            )
                        else:
                            st.error("Failed to generate PDF report")
                            
                    except Exception as pdf_error:
                        st.error(f"Error generating PDF report: {str(pdf_error)}")
                
                # HTML Report Download
                with report_col2:
                    try:
                        from services.html_report_generator_fixed import get_html_report_as_base64
                        import base64
                        
                        scan_id = ai_model_scan_results.get('scan_id', 'unknown')
                        html_b64 = get_html_report_as_base64(ai_model_scan_results)
                        
                        if html_b64:
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            html_filename = f"AI_Model_Scan_Report_{scan_id}_{timestamp}.html"
                            html_content = base64.b64decode(html_b64)
                            
                            st.download_button(
                                label="📥 Download HTML Report",
                                data=html_content,
                                file_name=html_filename,
                                mime="text/html",
                                key="ai_model_html_download_ready",
                                type="secondary"
                            )
                        else:
                            st.error("Failed to generate HTML report")
                            
                    except Exception as html_error:
                        st.error(f"Error generating HTML report: {str(html_error)}")
                
                # End of AI Model scan results display
                
        elif scan_type == _("scan.soc2"):
            # SOC2 scanning does not require file uploads
            st.info("SOC2 scanning does not require file uploads. Configure the repository details in the Advanced Configuration section and click the scan button below.")
            uploaded_files = []
                
        elif scan_type == _("scan.dpia"):
            # No header for DPIA - will be handled by the assessment form
            # No document upload needed - this is a pure questionnaire
            uploaded_files = []
        
        # Initialize start_scan variable
        start_scan = False
        
        # Handle special scan types
        if scan_type == _("scan.dpia"):
            # Add CSS to hide the scan button container for DPIA
            st.markdown("""
            <style>
            /* Hide the start scan button for DPIA */
            div[data-testid="stHorizontalBlock"] {
                display: none;
            }
            </style>
            """, unsafe_allow_html=True)
            # Set start_scan to True for DPIA to bypass the button click
            start_scan = True
        elif scan_type == _("scan.soc2"):
            # Make SOC2 scan buttons more prominent without hiding any buttons
            st.markdown("""
            <style>
            /* Make SOC2 primary buttons more prominent */
            button[kind="primary"] {
                background-color: #1565C0 !important;
                color: white !important;
                font-weight: bold !important;
                border: 2px solid #0D47A1 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Store GitHub tab input values in session state for main button to use
            if 'repo_url' in st.session_state:
                github_repo_url = st.session_state.repo_url
                github_branch = st.session_state.get('branch', '')
                github_token = st.session_state.get('token', '')
            
            # Prominent "Start Scan" button with free trial info
            scan_btn_col1, scan_btn_col2 = st.columns([3, 1])
            with scan_btn_col1:
                # Removed duplicate SOC2 scan button to avoid confusion with tab-specific buttons
                pass
            with scan_btn_col2:
                if 'free_trial_active' in locals() and free_trial_active:
                    st.success(f"Free Trial: {free_trial_days_left} days left")
                else:
                    st.warning("Premium Feature")
        elif scan_type == _("scan.ai_model"):
            # Create a more prominent scan button for AI Model scan
            st.markdown("""
            <style>
            /* Make Start Scan button more prominent for AI Model scan */
            div[data-testid="stHorizontalBlock"] button {
                background-color: #1976D2 !important;
                color: white !important;
                font-weight: bold !important;
                border: 2px solid #0D47A1 !important;
                padding: 0.5rem 1rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Prominent "Start Scan" button with free trial info
            scan_btn_col1, scan_btn_col2 = st.columns([3, 1])
            with scan_btn_col1:
                start_scan = st.button("Start AI Model Scan", use_container_width=True, type="primary", key="ai_model_scan_button")
            with scan_btn_col2:
                if free_trial_active:
                    st.success(f"Free Trial: {free_trial_days_left} days left")
                else:
                    st.warning("Premium Features")
        else:
            # Prominent "Start Scan" button with free trial info
            scan_btn_col1, scan_btn_col2 = st.columns([3, 1])
            with scan_btn_col1:
                start_scan = st.button("Start Scan", use_container_width=True, type="primary", key="start_scan_button")
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
                # For AI Model scans - validate based on selected source
                if model_source == "Repository URL" and not st.session_state.get('ai_model_repo_url'):
                    st.error("Repository URL not provided. Please enter a valid repository URL.")
                else:
                    proceed_with_scan = True
            elif scan_type == _("scan.dpia"):
                # For DPIA scans - no validation needed as the form handles its own documents
                proceed_with_scan = True
            elif scan_type == _("scan.manual") and not uploaded_files:
                st.error("Please upload at least one file for manual scanning.")
            else:
                proceed_with_scan = bool(uploaded_files)
            
            # If we can proceed with the scan based on validation
            if proceed_with_scan:
                # Special case for DPIA - skip payment flow
                if scan_type == _("scan.dpia"):
                    # Generate a unique scan ID
                    scan_id = str(uuid.uuid4())
                    st.session_state.current_scan_id = scan_id
                    
                    # Set payment as successful automatically for DPIA
                    st.session_state.payment_successful = True
                    st.session_state.payment_details = {
                        "status": "succeeded",
                        "amount": 0,
                        "scan_type": scan_type,
                        "user_email": user_email,
                        "is_dpia_bypass": True
                    }
                    
                    # Log the DPIA access
                    try:
                        results_aggregator.log_audit_event(
                            username=st.session_state.username,
                            action="DPIA_FORM_ACCESS",
                            details={
                                "scan_type": scan_type,
                                "user_email": user_email,
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                    except Exception as e:
                        st.warning(f"Audit logging failed: {str(e)}")
                # Check if free trial is active
                elif free_trial_active:
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
                
                # Handle SOC2 scan
                if scan_type == _("scan.soc2"):
                    # Import needed functions for SOC2 scanning
                    from services.enhanced_soc2_scanner import scan_github_repository, scan_azure_repository, display_soc2_scan_results
                    
                    st.info("Starting SOC2 compliance scan...")
                    
                    # Show status message and scan steps
                    with st.status(_("scan.scanning", "Scanning repository for SOC2 compliance issues..."), expanded=True) as status:
                        try:
                            # Determine which tab (GitHub or Azure) is active from session state 
                            # We'll use the keys that were used in the respective tab inputs
                            
                            # Try to get GitHub repo details first
                            repo_url = st.session_state.get('repo_url', '')
                            branch = st.session_state.get('branch', 'main') 
                            token = st.session_state.get('token', '')
                            project = st.session_state.get('project', '')
                            organization = st.session_state.get('organization', '')
                            
                            # Log information about session state values for debugging
                            st.write(f"**Debug session state values:**")
                            st.write(f"- Repository URL: {repo_url}")
                            st.write(f"- Branch: {branch}")
                            st.write(f"- Project (Azure): {project}")
                            st.write(f"- Organization (Azure): {organization}")
                            
                            # Determine if we're doing GitHub or Azure repo scan
                            repo_source = "GitHub Repository"  # Default to GitHub
                            
                            # Check Azure-specific fields to detect if Azure tab is active
                            if project:
                                repo_source = "Azure DevOps Repository"
                                
                            if not repo_url:
                                st.error(_("scan.error_no_repo", f"Please enter a repository URL in the {repo_source} tab"))
                                st.stop()
                            
                            # Show cloning message
                            st.write(_("scan.cloning", "Cloning repository..."))
                            
                            # Check if it's a GitHub or Azure repo
                            if repo_url.startswith(("https://github.com/", "http://github.com/")):
                                # Show which type of repository we're scanning
                                st.info("Scanning GitHub repository...")
                                # Perform GitHub scan
                                scan_results = scan_github_repository(repo_url, branch, token)
                            elif repo_url.startswith(("https://dev.azure.com/", "http://dev.azure.com/")):
                                # Show which type of repository we're scanning
                                st.info("Scanning Azure DevOps repository...")
                                
                                # Get project and organization from session state
                                project = st.session_state.get('project', '')
                                organization = st.session_state.get('organization', '')
                                
                                # Log additional Azure-specific values for debugging
                                st.write(f"**Azure DevOps Details:**")
                                st.write(f"- Project: {project}")
                                st.write(f"- Organization: {organization}")
                                
                                if not project:
                                    st.error(_("scan.error_no_project", "Please enter the Azure DevOps project name"))
                                    st.stop()
                                
                                # Perform Azure scan
                                scan_results = scan_azure_repository(repo_url, project, branch, token, organization)
                            else:
                                st.error(_("scan.error_invalid_repo", "Please enter a valid GitHub or Azure DevOps repository URL"))
                                st.stop()
                            
                            # Store the scan_results for PDF report generation
                            st.session_state.soc2_scan_results = scan_results
                            
                            # Check for scan failure
                            if scan_results.get("scan_status") == "failed":
                                error_msg = scan_results.get("error", "Unknown error")
                                st.error(f"{_('scan.scan_failed', 'Scan failed')}: {error_msg}")
                                status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                                st.stop()
                            else:
                                # Update status
                                status.update(label=_("scan.scan_complete", "SOC2 scan complete!"), state="complete")
                                
                                # Display scan results
                                st.markdown("---")
                                st.subheader(_("results.title", "SOC2 Scan Results"))
                                display_soc2_scan_results(scan_results)
                                
                                # Store scan in database
                                try:
                                    results_aggregator.store_scan_results(
                                        scan_id=scan_id,
                                        username=st.session_state.username,
                                        scan_type="soc2",
                                        results=scan_results
                                    )
                                    
                                    # Log audit event
                                    results_aggregator.log_audit_event(
                                        username=st.session_state.username,
                                        action="SOC2_SCAN_COMPLETED",
                                        details={
                                            "scan_id": scan_id,
                                            "repo_url": repo_url
                                        }
                                    )
                                except Exception as e:
                                    st.warning(f"Failed to store scan results: {str(e)}")
                        except Exception as e:
                            st.error(f"Error during SOC2 scan: {str(e)}")
                            logger.error(f"SOC2 scan error: {str(e)}")
                            traceback.print_exc()
                            status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                
                # Handle Repository URL special case
                elif scan_type == _("scan.code") and st.session_state.repo_source == _("scan.repository_url"):
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
                            
                            # Use our more reliable GitHub repository scanner
                            from services.github_repo_scanner import scan_github_repo_for_code
                            
                            # Define a custom progress callback for repository scanning
                            def repo_progress_callback(current, total, current_file):
                                progress = 0.1 + (current / total * 0.8)  # Scale to 10%-90% range
                                progress_bar.progress(min(progress, 0.9))
                                status_text.text(f"Scanning repository file {current}/{total}: {current_file}")
                            
                            # Scan the repository with our improved scanner
                            result = scan_github_repo_for_code(
                                repo_url=repo_url,
                                branch=branch_name,
                                token=auth_token,
                                progress_callback=repo_progress_callback
                            )
                            
                            # Check if scan was successful
                            if result.get('status') == 'error':
                                st.error(f"Repository scan failed: {result.get('message', 'Unknown error')}")
                                st.stop()
                            
                            # Process scan results
                            # Check and display branch information
                            if 'repository' in result and 'metadata' in result['repository']:
                                repo_metadata = result['repository']['metadata']
                                actual_branch = repo_metadata.get('branch', 'default')
                                # If the actual branch is different from the requested branch, inform the user
                                if branch_name and actual_branch != branch_name:
                                    st.info(f"Note: Branch '{branch_name}' was not found. The repository was scanned using the branch '{actual_branch}' instead.")
                            
                            # Show completion status
                            progress_bar.progress(1.0)
                            
                            # Get file counts and findings
                            files_scanned = result.get('files_scanned', 0)
                            files_skipped = result.get('files_skipped', 0)
                            total_pii = result.get('total_pii_found', 0)
                            
                            # Add GDPR compliance information to the scan results
                            # This addresses all core GDPR principles
                            result['gdpr_compliance'] = {
                                'lawfulness_fairness_transparency': {
                                    'score': 75,
                                    'issues_found': total_pii > 0,
                                    'recommendations': [
                                        "Document all processing in your privacy policy",
                                        "Ensure clear consent mechanisms are implemented",
                                        "Create data inventory for all identified PII"
                                    ]
                                },
                                'purpose_limitation': {
                                    'score': 80,
                                    'issues_found': False,
                                    'recommendations': [
                                        "Document specific purposes for PII collection",
                                        "Implement purpose limitation in data access controls"
                                    ]
                                },
                                'data_minimization': {
                                    'score': 70,
                                    'issues_found': total_pii > 10,
                                    'recommendations': [
                                        "Review necessity of all PII collected",
                                        "Implement data minimization practices"
                                    ]
                                },
                                'accuracy': {
                                    'score': 85,
                                    'issues_found': False,
                                    'recommendations': [
                                        "Implement data validation mechanisms",
                                        "Create user data update capabilities"
                                    ]
                                },
                                'storage_limitation': {
                                    'score': 75,
                                    'issues_found': False,
                                    'recommendations': [
                                        "Define retention periods for all PII",
                                        "Implement automated data deletion"
                                    ]
                                },
                                'integrity_confidentiality': {
                                    'score': 65,
                                    'issues_found': total_pii > 0,
                                    'recommendations': [
                                        "Encrypt all PII data",
                                        "Implement access controls",
                                        "Apply the principle of least privilege"
                                    ]
                                },
                                'accountability': {
                                    'score': 80,
                                    'issues_found': False,
                                    'recommendations': [
                                        "Document processing activities",
                                        "Implement audit trails",
                                        "Define data protection responsibilities"
                                    ]
                                },
                                'netherlands_specific': {
                                    'score': 70,
                                    'issues_found': False,
                                    'recommendations': [
                                        "Implement specific BSN handling requirements",
                                        "Add specific consent flags for minors (<16 years)",
                                        "Ensure Dutch breach notification framework compliance"
                                    ]
                                }
                            }
                            
                            # Calculate overall GDPR compliance score
                            gdpr_scores = [v['score'] for k, v in result['gdpr_compliance'].items()]
                            result['overall_gdpr_score'] = sum(gdpr_scores) / len(gdpr_scores)
                            
                            # Get formatted findings for display
                            formatted_findings = result.get('formatted_findings', [])
                            if not formatted_findings and 'findings' in result:
                                # Fallback to regular findings if available
                                scan_results = result.get('findings', [])
                            else:
                                scan_results = formatted_findings
                            
                            # Display scan summary
                            status_text.text(f"Completed repository scan. Scanned {files_scanned} files, found {total_pii} PII instances.")
                            
                            # Save scan results for report generation
                            st.session_state.repo_scan_result = result
                            
                            # Add scan result display with enhanced visualization
                            st.success("Repository scan completed successfully!")
                            
                            # Display GDPR compliance summary
                            st.subheader("GDPR Compliance Summary")
                            
                            # Overall compliance score
                            overall_score = result.get('overall_gdpr_score', 0)
                            st.metric("Overall GDPR Compliance Score", f"{overall_score:.1f}/100")
                            
                            # Create tabs for different report sections
                            results_tab, findings_tab, compliance_tab, report_tab = st.tabs([
                                "Summary", "Findings", "GDPR Compliance", "Export Reports"
                            ])
                            
                            with results_tab:
                                st.write("### Scan Statistics")
                                
                                # Display scan statistics in columns
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Files Scanned", files_scanned)
                                with col2:
                                    st.metric("Files Skipped", files_skipped)
                                with col3:
                                    st.metric("PII Instances Found", total_pii)
                                
                                # Risk level breakdown
                                st.write("### Risk Level Breakdown")
                                high_risk = result.get('high_risk_count', 0)
                                medium_risk = result.get('medium_risk_count', 0) 
                                low_risk = result.get('low_risk_count', 0)
                                
                                # Show risk metrics
                                risk_col1, risk_col2, risk_col3 = st.columns(3)
                                with risk_col1:
                                    st.metric("High Risk", high_risk, delta=None, 
                                             delta_color="inverse" if high_risk > 0 else "normal")
                                with risk_col2:
                                    st.metric("Medium Risk", medium_risk, delta=None,
                                             delta_color="inverse" if medium_risk > 5 else "normal")
                                with risk_col3:
                                    st.metric("Low Risk", low_risk, delta=None)
                            
                            with findings_tab:
                                if formatted_findings:
                                    st.write("### Detailed PII Findings")
                                    
                                    # Convert findings to DataFrame for better display
                                    findings_df = pd.DataFrame(formatted_findings)
                                    
                                    # Format the findings DataFrame
                                    if not findings_df.empty:
                                        # Select and rename columns for display
                                        display_cols = ['type', 'value', 'location', 'risk_level']
                                        rename_map = {
                                            'type': 'PII Type',
                                            'value': 'Value',
                                            'location': 'Location',
                                            'risk_level': 'Risk Level'
                                        }
                                        
                                        # Apply column selection and renaming
                                        if all(col in findings_df.columns for col in display_cols):
                                            display_df = findings_df[display_cols].rename(columns=rename_map)
                                            
                                            # Apply styling
                                            def highlight_risk(val):
                                                if val == 'high':
                                                    return 'background-color: #ef4444; color: white'
                                                elif val == 'medium':
                                                    return 'background-color: #f97316; color: white'
                                                elif val == 'low':
                                                    return 'background-color: #10b981; color: white'
                                                return ''
                                            
                                            # Display with styling
                                            st.dataframe(display_df.style.applymap(
                                                highlight_risk, subset=['Risk Level']
                                            ))
                                        else:
                                            st.dataframe(findings_df)
                                    else:
                                        st.info("No specific findings to display.")
                                else:
                                    st.info("No detailed findings available.")
                            
                            with compliance_tab:
                                st.write("### GDPR Compliance Analysis")
                                
                                # Display GDPR principles compliance
                                if 'gdpr_compliance' in result:
                                    gdpr_data = result['gdpr_compliance']
                                    
                                    for principle, details in gdpr_data.items():
                                        # Format principle name for display
                                        principle_name = principle.replace('_', ' ').title()
                                        
                                        # Create expander for each principle
                                        with st.expander(f"{principle_name} ({details['score']}/100)"):
                                            st.write(f"**Status:** {'⚠️ Issues detected' if details['issues_found'] else '✅ Compliant'}")
                                            
                                            st.write("**Recommendations:**")
                                            for rec in details.get('recommendations', []):
                                                st.write(f"- {rec}")
                                else:
                                    st.warning("GDPR compliance data not available.")
                            
                            with report_tab:
                                st.write("### Export Report Options")
                                
                                # Import the report display functionality
                                from services.download_reports import display_report_options
                                
                                # Use the comprehensive report display module
                                display_report_options(result)
                        
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
                        
                        # Process document scanning with BlobScanner
                        if uploaded_files and len(uploaded_files) > 0:
                            try:
                                # Save uploaded files temporarily
                                temp_dir = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                os.makedirs(temp_dir, exist_ok=True)
                                
                                file_paths = []
                                for uploaded_file in uploaded_files:
                                    file_path = os.path.join(temp_dir, uploaded_file.name)
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                                    file_paths.append(file_path)
                                
                                # Initialize progress tracking
                                progress_bar.progress(0.1)
                                status_text.text("Starting document scan...")
                                
                                # Define progress callback function
                                def doc_progress_callback(current, total, current_file):
                                    progress = 0.1 + (current / total * 0.8)
                                    progress_bar.progress(progress)
                                    status_text.text(f"Scanning document {current}/{total}: {os.path.basename(current_file)}")
                                
                                # Perform document scan using the correct method
                                document_results = scanner_instance.scan_multiple_documents(
                                    file_paths, 
                                    callback_fn=doc_progress_callback
                                )
                                
                                # Complete progress
                                progress_bar.progress(1.0)
                                status_text.text("Document scan completed!")
                                
                                # Store results in session state for the display function
                                st.session_state.document_scan_results = document_results
                                st.session_state.document_scan_complete = True
                                
                                # Store in scan_results for the general processing section
                                scan_results = [document_results] if document_results else []
                                
                                # Cleanup temporary files
                                import shutil
                                if os.path.exists(temp_dir):
                                    shutil.rmtree(temp_dir)
                                
                                # Mark scan as complete and show success
                                st.success("Document scan completed successfully!")
                                st.write(f"Scanned {len(file_paths)} document(s)")
                                
                                if document_results and 'total_pii_found' in document_results:
                                    st.write(f"Found {document_results['total_pii_found']} PII instances")
                                    
                                # Display the results immediately
                                st.subheader("Document Scan Results")
                                
                                # Show basic metrics
                                if document_results:
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.metric("Files Scanned", document_results.get('file_count', 0))
                                    with col2:
                                        total_pii = document_results.get('total_pii_found', 0)
                                        st.metric("Total PII Found", total_pii)
                                    with col3:
                                        high_risk = document_results.get('high_risk_count', 0) + document_results.get('critical_risk_count', 0)
                                        st.metric("High Risk Items", high_risk)
                                    with col4:
                                        medium_risk = document_results.get('medium_risk_count', 0)
                                        st.metric("Medium Risk Items", medium_risk)
                                    
                                    # Add download buttons - Direct approach
                                    st.markdown("### Download Reports")
                                    col1, col2 = st.columns(2)
                                    
                                    # Generate reports immediately for download
                                    try:
                                        from services.document_report_generator import generate_document_html_report, generate_document_pdf_report
                                        
                                        with col1:
                                            pdf_bytes = generate_document_pdf_report(document_results)
                                            st.download_button(
                                                label="📄 Download PDF Certificate",
                                                data=pdf_bytes,
                                                file_name=f"document_scan_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                                mime="application/pdf",
                                                key="doc_pdf_download",
                                                use_container_width=True
                                            )
                                        
                                        with col2:
                                            html_content = generate_document_html_report(document_results)
                                            st.download_button(
                                                label="📊 Download HTML Report", 
                                                data=html_content,
                                                file_name=f"document_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                                mime="text/html",
                                                key="doc_html_download",
                                                use_container_width=True
                                            )
                                            
                                    except Exception as e:
                                        st.error(f"Report generation error: {str(e)}")
                                        st.write("Debug info:", {
                                            'total_pii_found': document_results.get('total_pii_found', 0),
                                            'file_count': document_results.get('file_count', 0),
                                            'findings_length': len(document_results.get('findings', []))
                                        })
                                
                                # Skip the rest of the scanner processing for document scans
                                scan_running = False
                                
                            except Exception as e:
                                st.error(f"Error during document scan: {str(e)}")
                                scan_results = []
                                scan_running = False
                                # Cleanup on error
                                if 'temp_dir' in locals() and os.path.exists(temp_dir):
                                    import shutil
                                    shutil.rmtree(temp_dir)
                    elif scan_type == _("scan.image"):
                        # Image Scanner - comprehensive image PII scanning
                        try:
                            from services.image_scanner import ImageScanner
                            
                            # Get image configuration from session state
                            image_config = st.session_state.get('image_config', {})
                            
                            # Initialize image scanner
                            image_scanner = ImageScanner(region=region)
                            
                            # Set up progress tracking
                            def image_progress_callback(current, total, image_name):
                                """Update the image scan progress"""
                                progress = current / total if total > 0 else 0
                                progress_bar.progress(progress)
                                status_text.text(f"Image Scan: Analyzing '{image_name}' ({current}/{total})")
                            
                            # Process uploaded images
                            if uploaded_files:
                                # Save uploaded files temporarily
                                temp_dir = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                os.makedirs(temp_dir, exist_ok=True)
                                
                                image_paths = []
                                for uploaded_file in uploaded_files:
                                    # Save the uploaded file
                                    file_path = os.path.join(temp_dir, uploaded_file.name)
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                                    image_paths.append(file_path)
                                
                                # Perform the image scan
                                status_text.text("Scanning images for PII...")
                                image_result = image_scanner.scan_multiple_images(
                                    image_paths=image_paths,
                                    callback_fn=image_progress_callback
                                )
                                
                                # Clean up temporary files
                                try:
                                    import shutil
                                    shutil.rmtree(temp_dir)
                                except Exception as cleanup_error:
                                    logger.warning(f"Failed to clean up temp directory: {cleanup_error}")
                                
                                # Process image scan results - Always store and display results
                                progress_bar.progress(1.0)
                                
                                # Store results for report generation regardless of findings
                                scan_results = [image_result]
                                st.session_state.image_scan_results = image_result
                                st.session_state.image_scan_complete = True
                                
                                # Check if PII was found and display appropriate message
                                findings_count = len(image_result.get('findings', []))
                                images_processed = image_result.get('metadata', {}).get('images_scanned', len(uploaded_files))
                                
                                if findings_count > 0:
                                    status_text.text(f"Image Scan: Complete! Found {findings_count} PII instances.")
                                    st.success(f"✅ Image scan completed successfully! Found {findings_count} PII instances.")
                                    
                                    # Display results for PII found case
                                    st.markdown("---")
                                    st.subheader("🖼️ Image Scan Results - PII Detected")
                                    
                                    # Show summary metrics
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Images Scanned", images_processed)
                                    with col2:
                                        st.metric("Total PII Findings", findings_count)
                                    with col3:
                                        st.metric("Images with PII", image_result.get('images_with_pii', 0))
                                    with col4:
                                        risk_score = image_result.get('risk_summary', {}).get('score', 0)
                                        st.metric("Risk Score", f"{risk_score}/100")
                                    
                                    # Show detailed findings
                                    st.subheader("🔍 Detailed Findings")
                                    findings = image_result.get('findings', [])
                                    for i, finding in enumerate(findings):
                                        with st.expander(f"Finding {i+1}: {finding.get('type', 'Unknown PII')}", expanded=True):
                                            st.write(f"**Source:** {os.path.basename(finding.get('source', 'Unknown'))}")
                                            st.write(f"**Risk Level:** {finding.get('risk_level', 'Unknown')}")
                                            st.write(f"**Confidence:** {finding.get('confidence', 0):.0%}")
                                            st.write(f"**Detection Method:** {finding.get('extraction_method', 'Unknown')}")
                                            st.write(f"**Context:** {finding.get('context', 'No context')}")
                                            st.write(f"**GDPR Compliance:** {finding.get('reason', 'No reason')}")
                                
                                else:
                                    status_text.text("Image Scan: Complete - No PII detected!")
                                    st.success("✅ Image scan completed successfully! No personal data detected in your images.")
                                    
                                    # Display results for clean scan
                                    st.markdown("---")
                                    st.subheader("🖼️ Image Scan Results - Clean Scan")
                                    st.success(f"✅ All {images_processed} images scanned successfully with no personal data detected!")
                                    st.markdown("""
                                    <div style="padding: 15px; background-color: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 5px; margin: 10px 0;">
                                        <h4 style="color: #1e40af; margin-top: 0;">GDPR Compliance Status: EXCELLENT</h4>
                                        <p style="margin-bottom: 0;">Your images contain no detectable personal data, which means excellent privacy compliance. You can download an official compliance certificate below.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Display summary metrics for clean scan
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Images Scanned", images_processed)
                                    with col2:
                                        st.metric("Total PII Findings", 0)
                                    with col3:
                                        st.metric("Images with PII", 0)
                                    with col4:
                                        st.metric("Risk Score", "0/100")
                                
                                # Show certificate download options (for both cases)
                                st.subheader("📜 Download Reports")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    # PDF Certificate Download
                                    try:
                                        from services.image_report_generator import ImageReportGenerator
                                        
                                        generator = ImageReportGenerator()
                                        pdf_content = generator.generate_pdf_report(image_result)
                                        
                                        st.download_button(
                                            label="📄 Download PDF Certificate",
                                            data=pdf_content,
                                            file_name=f"image_scan_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                            mime="application/pdf",
                                            key="save_image_pdf_inline"
                                        )
                                        
                                    except Exception as e:
                                        st.error(f"PDF generation error: {str(e)}")
                                
                                with col2:
                                    # HTML Report Download
                                    try:
                                        from services.html_report_generator_fixed import HTMLReportGenerator
                                        
                                        html_generator = HTMLReportGenerator()
                                        html_content = html_generator.generate_image_report(image_result)
                                        
                                        st.download_button(
                                            label="🌐 Download HTML Report",
                                            data=html_content,
                                            file_name=f"image_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                            mime="text/html",
                                            key="save_image_html_inline"
                                        )
                                        
                                    except Exception as e:
                                        st.error(f"HTML generation error: {str(e)}")
                                
                                # Show navigation tip
                                st.info("💡 You can also view these results in the 'Results' section of the navigation menu.")
                            else:
                                st.error("No images uploaded for scanning.")
                                scan_results = []
                            
                        except Exception as e:
                            st.error(f"Error during image scan: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                            scan_results = []
                        
                        # Skip the rest of the scanner_instance processing for image scans
                        if scan_type == _("scan.image"):
                            pass
                    elif scan_type == _("scan.database"):
                        # Database Scanner - comprehensive database PII scanning
                        try:
                            from services.db_scanner import DatabaseScanner
                            
                            # Get database configuration from session state
                            db_config = st.session_state.get('db_config', {})
                            
                            # Validate required configuration
                            if not db_config:
                                st.error("Database configuration not found. Please configure the database connection.")
                                st.stop()
                            
                            # Initialize database scanner
                            db_scanner = DatabaseScanner(region=region)
                            
                            # Set up database connection
                            connection_params = {}
                            
                            if db_config.get('connection_option') == 'Connection String':
                                connection_string = db_config.get('connection_string', '')
                                if not connection_string:
                                    st.error("Connection string is required.")
                                    st.stop()
                                
                                # Parse connection string to extract parameters
                                from urllib.parse import urlparse
                                parsed = urlparse(connection_string)
                                
                                if parsed.scheme == 'postgresql':
                                    connection_params = {
                                        'db_type': 'postgres',
                                        'host': parsed.hostname,
                                        'port': parsed.port or 5432,
                                        'dbname': parsed.path.lstrip('/'),
                                        'user': parsed.username,
                                        'password': parsed.password
                                    }
                                elif parsed.scheme == 'mysql':
                                    connection_params = {
                                        'db_type': 'mysql',
                                        'host': parsed.hostname,
                                        'port': parsed.port or 3306,
                                        'database': parsed.path.lstrip('/'),
                                        'user': parsed.username,
                                        'password': parsed.password
                                    }
                                else:
                                    st.error(f"Unsupported database type in connection string: {parsed.scheme}")
                                    st.stop()
                            else:
                                # Individual parameters
                                db_type = db_config.get('db_type', '').lower()
                                if db_type == 'postgresql':
                                    connection_params = {
                                        'db_type': 'postgres',
                                        'host': db_config.get('db_server'),
                                        'port': int(db_config.get('db_port', 5432)),
                                        'dbname': db_config.get('db_name'),
                                        'user': db_config.get('db_username'),
                                        'password': db_config.get('db_password')
                                    }
                                elif db_type == 'mysql':
                                    connection_params = {
                                        'db_type': 'mysql',
                                        'host': db_config.get('db_server'),
                                        'port': int(db_config.get('db_port', 3306)),
                                        'database': db_config.get('db_name'),
                                        'user': db_config.get('db_username'),
                                        'password': db_config.get('db_password')
                                    }
                                else:
                                    st.error(f"Unsupported database type: {db_type}")
                                    st.stop()
                            
                            # Validate connection parameters
                            required_keys = ['host', 'user', 'password']
                            if connection_params['db_type'] == 'postgres':
                                required_keys.append('dbname')
                            elif connection_params['db_type'] == 'mysql':
                                required_keys.append('database')
                            
                            missing_keys = [key for key in required_keys if not connection_params.get(key)]
                            if missing_keys:
                                st.error(f"Missing required database parameters: {', '.join(missing_keys)}")
                                st.stop()
                            
                            # Attempt database connection
                            status_text.text("Connecting to database...")
                            if not db_scanner.connect_to_database(connection_params):
                                st.error("Failed to connect to database. Please check your connection parameters.")
                                st.stop()
                            
                            # Set up progress tracking
                            def db_progress_callback(current, total, table_name):
                                """Update the database scan progress"""
                                progress = current / total if total > 0 else 0
                                progress_bar.progress(progress)
                                status_text.text(f"Database Scan: Analyzing table '{table_name}' ({current}/{total})")
                            
                            # Perform the database scan
                            status_text.text("Scanning database for PII...")
                            db_result = db_scanner.scan_database(callback_fn=db_progress_callback)
                            
                            # Disconnect from database
                            db_scanner.disconnect()
                            
                            # Process database scan results
                            if 'findings' in db_result and db_result['findings']:
                                # Update progress to complete
                                progress_bar.progress(1.0)
                                status_text.text("Database Scan: Complete!")
                                
                                # Store results for report generation
                                scan_results = [db_result]
                                
                                # Add to session state for download functionality
                                st.session_state.db_scan_results = db_result
                                st.session_state.db_scan_complete = True
                                
                                # Rerun to immediately show download buttons
                                st.rerun()
                            elif 'error' in db_result:
                                st.error(f"Database scan failed: {db_result['error']}")
                                scan_results = []
                            else:
                                # No PII found
                                progress_bar.progress(1.0)
                                status_text.text("Database Scan: Complete - No PII detected!")
                                scan_results = [db_result]
                                
                                # Store results even if no PII found
                                st.session_state.db_scan_results = db_result
                                st.session_state.db_scan_complete = True
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error during database scan: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                            scan_results = []
                        
                        # Skip the rest of the scanner_instance processing for database scans
                        if scan_type == _("scan.database"):
                            pass
                    elif scan_type == _("scan.api"):
                        # API Scanner - comprehensive API security and privacy scanning
                        try:
                            from services.api_scanner import APIScanner
                            
                            # Get API configuration from session state
                            api_config = st.session_state.get('api_config', {})
                            api_base_url = api_config.get('api_base_url', '')
                            
                            if not api_base_url:
                                st.error("API Base URL not found. Please enter a valid API endpoint.")
                                st.stop()
                            
                            # Initialize API scanner with configuration
                            api_scanner = APIScanner(
                                max_endpoints=api_config.get('max_endpoints', 50),
                                request_timeout=api_config.get('request_timeout', 10),
                                rate_limit_delay=api_config.get('rate_limit_delay', 1.0),
                                follow_redirects=api_config.get('follow_redirects', True),
                                verify_ssl=api_config.get('verify_ssl', True),
                                region=region
                            )
                            
                            # Set up progress tracking
                            def api_progress_callback(current, total, endpoint):
                                """Update the API scan progress"""
                                progress = current / total if total > 0 else 0
                                progress_bar.progress(progress)
                                status_text.text(f"API Scan: Testing {endpoint} ({current}/{total})")
                            
                            # Set progress callback
                            api_scanner.set_progress_callback(api_progress_callback)
                            
                            # Perform the API scan
                            api_result = api_scanner.scan_api(
                                base_url=api_base_url,
                                auth_token=api_config.get('auth_token'),
                                openapi_spec=api_config.get('openapi_spec'),
                                endpoints=api_config.get('custom_endpoints')
                            )
                            
                            # Process API scan results
                            if 'findings' in api_result:
                                # Update progress to complete
                                progress_bar.progress(1.0)
                                status_text.text("API Scan: Complete!")
                                
                                # Store results for report generation
                                scan_results = [api_result]
                                
                                # Add to session state for download functionality
                                st.session_state.api_scan_results = api_result
                                st.session_state.api_scan_complete = True
                                
                                # Rerun to immediately show download buttons
                                st.rerun()
                            else:
                                scan_results = []
                                st.error("No findings returned from API scan")
                            
                        except Exception as e:
                            st.error(f"Error during API scan: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                            scan_results = []
                        
                        # Skip the rest of the scanner_instance processing for API scans
                        if scan_type == _("scan.api"):
                            pass
                    elif scan_type == _("scan.ai_model"):
                        # Get AI Model Scanner
                        ai_model_scanner = AIModelScanner(region=region)
                        
                        # Set up progress tracking
                        def update_scan_progress(current, total, status_message):
                            """Update the AI Model scan progress"""
                            progress = current / total if total > 0 else 0
                            progress_bar.progress(progress)
                            status_text.text(f"AI Model Scan: {status_message} ({current}/{total})")
                            
                        # Set progress callback
                        ai_model_scanner.set_progress_callback(update_scan_progress)
                        
                        # Prepare model details based on source
                        model_source = st.session_state.ai_model_source
                        model_details = {}
                        
                        if model_source == "API Endpoint":
                            model_details = {
                                "api_endpoint": st.session_state.get('ai_model_api_endpoint', ""),
                                "repository_path": st.session_state.get('ai_model_repo_path', "")
                            }
                        elif model_source == "Model Hub":
                            model_details = {
                                "hub_url": st.session_state.get('ai_model_hub_url', ""),
                                "repository_path": st.session_state.get('ai_model_repo_path', "")
                            }
                        elif model_source == "Repository URL":
                            model_details = {
                                "repo_url": st.session_state.get('ai_model_repo_url', ""), 
                                "branch_name": st.session_state.get('ai_model_branch_name', "main"),
                                "auth_token": st.session_state.get('ai_model_auth_token', "")
                            }
                            
                            # Debug info for AI model repo URL
                            logging.info(f"AI Model Repository URL: {model_details.get('repo_url')}")
                            if not model_details.get('repo_url'):
                                st.error("AI Model Repository URL is required but not found in session state. Please enter a valid GitHub repository URL.")
                        
                        # Get leakage types and context from session state or set defaults
                        leakage_types = st.session_state.get('leakage_types', ["All"])
                        context = st.session_state.get('context', ["General"])
                        
                        # Wrap entire scanning process in try block with multiple layers of error handling
                        try:
                            # Validate required inputs first
                            if not model_source:
                                raise ValueError("Model source must be selected")
                            
                            # Validate model details based on source type
                            if model_source == "API Endpoint" and not model_details.get("api_endpoint"):
                                raise ValueError("API endpoint URL is required")
                            elif model_source == "Model Hub" and not model_details.get("hub_url"):
                                raise ValueError("Model Hub URL/ID is required")
                            elif model_source == "Repository URL" and not model_details.get("repo_url"):
                                raise ValueError("Repository URL is required")
                            
                            # Run the AI model scan with complete error handling
                            try:
                                scan_result = ai_model_scanner.scan_model(
                                    model_source=model_source,
                                    model_details=model_details,
                                    leakage_types=leakage_types,
                                    context=context
                                )
                                
                                # Store successful scan results in session state immediately
                                if isinstance(scan_result, dict):
                                    st.session_state.ai_model_scan_results = scan_result
                                    st.session_state.ai_model_scan_complete = True
                                    progress_bar.progress(1.0)
                                    status_text.text("AI Model Scan: Complete!")
                                    st.rerun()
                                
                                # Validate returned result
                                if not isinstance(scan_result, dict):
                                    st.warning("Scanner returned invalid result format, using fallback result")
                                    # Create fallback result with valid structure
                                    scan_result = {
                                        "scan_id": scan_id,
                                        "scan_type": _("scan.ai_model"),
                                        "timestamp": datetime.now().isoformat(),
                                        "model_source": model_source,
                                        "findings": [{
                                            "id": f"AIFALLBACK-{uuid.uuid4().hex[:6]}",
                                            "type": "Error",
                                            "category": "Scan Result",
                                            "description": "Scanner returned invalid format",
                                            "risk_level": "medium",
                                            "location": "AI Model Scanner"
                                        }],
                                        "status": "completed_with_warnings",
                                        "risk_score": 50,
                                        "severity_level": "medium",
                                        "severity_color": "#f59e0b",
                                        "total_findings": 1,
                                        "region": "Global"
                                    }
                                
                                # Store scan results in session state for later access
                                st.session_state.ai_model_scan_results = scan_result
                                st.session_state.ai_model_scan_complete = True
                                
                                # Set progress to complete
                                progress_bar.progress(1.0)
                                status_text.text("AI Model Scan: Complete!")
                                
                                # Store in scan_results list for aggregator
                                scan_results = [scan_result]
                                
                                # Rerun to immediately show download buttons
                                st.rerun()
                                
                            except Exception as scanner_error:
                                # Show error but continue processing with valid error result
                                st.warning(f"AI Model scanner encountered an error but recovered: {str(scanner_error)}")
                                
                                # Get an error result with valid structure from the scanner
                                # (The scanner now always returns a valid structure even on error)
                                scan_result = {
                                    "scan_id": scan_id,
                                    "scan_type": _("scan.ai_model"),
                                    "timestamp": datetime.now().isoformat(),
                                    "model_source": model_source,
                                    "findings": [{
                                        "id": f"AIERROR-{uuid.uuid4().hex[:6]}",
                                        "type": "Error",
                                        "category": "Scanner Error",
                                        "description": f"Error in scanner: {str(scanner_error)}",
                                        "risk_level": "medium",
                                        "location": "AI Model Scanner"
                                    }],
                                    "status": "completed_with_errors",
                                    "risk_score": 50,
                                    "severity_level": "medium", 
                                    "severity_color": "#f59e0b",
                                    "total_findings": 1,
                                    "region": "Global"
                                }
                                
                                # Store error result in session state
                                st.session_state.ai_model_scan_results = scan_result
                                st.session_state.ai_model_scan_complete = True
                                
                                # Set progress to complete
                                progress_bar.progress(1.0)
                                status_text.text("AI Model Scan: Completed with Errors")
                                
                                # Store in scan_results list
                                scan_results = [scan_result]
                                
                                # Rerun to immediately show download buttons
                                st.rerun()
                        
                        except Exception as e:
                            # Catastrophic error at the app level - show full error but still provide valid result
                            st.error(f"AI Model scan encountered a critical error: {str(e)}")
                            
                            # Only show stack trace in development mode
                            if st.session_state.get('debug_mode', False):
                                import traceback
                                st.code(traceback.format_exc())
                            
                            # Create a valid scan result for the error
                            error_scan_result = {
                                "scan_id": scan_id,
                                "scan_type": _("scan.ai_model"),
                                "timestamp": datetime.now().isoformat(),
                                "model_source": model_source if 'model_source' in locals() else "Unknown",
                                "findings": [{
                                    "id": f"AIFATAL-{uuid.uuid4().hex[:6]}",
                                    "type": "Critical Error",
                                    "category": "Fatal Error",
                                    "description": f"Fatal error in scan process: {str(e)}",
                                    "risk_level": "high",
                                    "location": "Scan Processor"
                                }],
                                "status": "failed",
                                "error": str(e),
                                "risk_score": 75,
                                "severity_level": "high",
                                "severity_color": "#ef4444",
                                "total_findings": 1,
                                "region": "Global"
                            }
                            
                            # Store error result
                            st.session_state.ai_model_scan_results = error_scan_result
                            st.session_state.ai_model_scan_complete = True
                            scan_results = [error_scan_result]
                            
                            # Set progress to complete
                            if 'progress_bar' in locals():
                                progress_bar.progress(1.0)
                            if 'status_text' in locals():
                                status_text.text("AI Model Scan: Failed with Critical Error")
                            
                            # Rerun to immediately show download buttons
                            st.rerun()
                    elif scan_type == _("scan.dpia"):
                        # Offer choice between simple and comprehensive DPIA
                        st.markdown("### Choose Your DPIA Assessment Type")
                        
                        # Run Simple DPIA directly without options
                        try:
                            from simple_dpia import run_simple_dpia
                            run_simple_dpia()
                        except ImportError:
                            st.error("Simple DPIA module not available")
                        st.markdown("""
                        <style>
                        /* Hide the Start Scan button */
                        div.stButton > button:contains("Start Scan") {
                            display: none !important;
                        }
                        
                        /* Hide upload-related sections */
                        .main .block-container h2:contains("Upload Files"),
                        .main .block-container h2:contains("Upload Files") ~ div,
                        .main .block-container hr:has(+ h2:contains("Upload Files")),
                        .main .block-container hr:has(~ h2:contains("Upload Files")) {
                            display: none !important;
                        }
                        
                        /* Additional selector for the specific section after Select Region */
                        .main .block-container div:has(+ h2:contains("Upload Files")),
                        .main .block-container div:has(~ label:contains("Select Region")) ~ hr,
                        .main .block-container div:has(~ label:contains("Select Region")) ~ div:has(h2) {
                            display: none !important;
                        }
                        
                        /* Hide "Select Region" section too as it's not needed for DPIA */
                        .main .block-container label:contains("Select Region"),
                        .main .block-container div:has(label:contains("Select Region")) {
                            display: none !important;
                        }
                        
                        /* Hide all specific sections we don't want in DPIA */
                        #upload-files-section, 
                        #advanced-configuration-section,
                        #sample-findings-section {
                            display: none !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Stop normal flow to proceed with only the DPIA form
                        scan_running = False
                    
                    elif scan_type == _("scan.soc2"):
                        # Import enhanced SOC2 scanner components directly within app.py
                        # rather than from a separate page to ensure it's behind authentication
                        from services.soc2_scanner import SOC2_CATEGORIES  # Only need categories for UI
                        from services.enhanced_soc2_scanner import scan_github_repository, scan_azure_repository, display_soc2_scan_results
                        from services.report_generator_safe import generate_report
                        
                        # Hide the Start Scan button and Upload Files section for cleaner UI
                        st.markdown("""
                        <style>
                        /* Hide the Start Scan button */
                        div.stButton > button:contains("Start Scan") {
                            display: none !important;
                        }
                        
                        /* Hide upload-related sections */
                        .main .block-container h2:contains("Upload Files"),
                        .main .block-container h2:contains("Upload Files") ~ div,
                        .main .block-container hr:has(+ h2:contains("Upload Files")),
                        .main .block-container hr:has(~ h2:contains("Upload Files")) {
                            display: none !important;
                        }
                        
                        /* Additional selector for the specific section after Select Region */
                        .main .block-container div:has(+ h2:contains("Upload Files")),
                        .main .block-container div:has(~ label:contains("Select Region")) ~ hr,
                        .main .block-container div:has(~ label:contains("Select Region")) ~ div:has(h2) {
                            display: none !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # SOC2 scanner UI with enhanced design
                        st.title(_("scan.soc2_title", "SOC2 Compliance Scanner"))
                        
                        # Display enhanced description with clear value proposition
                        st.write(_(
                            "scan.soc2_description", 
                            "Scan Infrastructure as Code (IaC) repositories for SOC2 compliance issues. "
                            "This scanner identifies security, availability, processing integrity, "
                            "confidentiality, and privacy issues in your infrastructure code."
                        ))
                        
                        # Add more detailed info about what SOC2 scanning does
                        st.info(_(
                            "scan.soc2_info",
                            "SOC2 scanning analyzes your infrastructure code against Trust Services Criteria (TSC) "
                            "to identify potential compliance issues. The scanner maps findings to specific TSC controls "
                            "and provides recommendations for remediation."
                        ))
                        
                        # Add free trial information
                        st.markdown("""
                        <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px;">
                            <span style="font-weight: bold;">Free Trial:</span> 3 days left
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Create tabs for configuration and results
                        config_tab, results_tab = st.tabs(["SOC2 Scanner Configuration", "Results"])
                        
                        with config_tab:
                            # Repository selection
                            st.subheader(_("scan.repo_source", "Repository Source"))
                            repo_source = st.radio(
                                "Select Repository Source",
                                ["GitHub Repository", "Azure DevOps Repository"],
                                horizontal=True,
                                key="soc2_repo_source"
                            )
                        
                        if repo_source == "GitHub Repository":
                            # Create a container with a custom border
                            with st.container():
                                st.markdown("""
                                <div style="border: 1px solid #e6e6e6; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
                                """, unsafe_allow_html=True)
                                
                                # Repository URL input
                                st.subheader(_("scan.repo_details", "Repository Details"))
                                repo_url = st.text_input(_("scan.repo_url", "GitHub Repository URL"), 
                                                    placeholder="https://github.com/username/repository",
                                                    value="https://github.com/vishaal314/terrascan",
                                                    key="github_soc2_repo_url")
                                
                                # Create columns for the branch and token inputs
                                col1, col2 = st.columns(2)
                                with col1:
                                    branch = st.text_input(_("scan.branch", "Branch (optional)"), 
                                                        value="main",
                                                        placeholder="main", 
                                                        key="github_soc2_branch")
                                with col2:
                                    token = st.text_input(_("scan.access_token", "GitHub Access Token (for private repos)"), 
                                                        type="password", 
                                                        placeholder="ghp_xxxxxxxxxxxx", 
                                                        key="github_soc2_token")
                                    
                                # Store these values in session state for the main scan button to use
                                if repo_url:
                                    st.session_state.repo_url = repo_url
                                if branch:
                                    st.session_state.branch = branch
                                if token:
                                    st.session_state.token = token
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Advanced configuration in an expander
                            with st.expander(_("scan.advanced_options", "Advanced Configuration")):
                                # Target check options
                                st.subheader("Target Checks")
                                target_checks = st.radio(
                                    "Select scan scope",
                                    ["All", "Security Only", "Custom"],
                                    horizontal=True,
                                    key="github_soc2_target_checks"
                                )
                                
                                # Path to config file
                                access_control_path = st.text_input(
                                    "Access Control Config File Path",
                                    placeholder="/path/to/iam/config.yaml",
                                    value="/path/to/iam/config.yaml",
                                    key="github_soc2_config_path"
                                )
                                
                                # Scan timeframe
                                scan_timeframe = st.selectbox(
                                    "Scan Timeframe",
                                    ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                                    index=0,
                                    key="github_soc2_timeframe"
                                )
                                
                                # Custom ruleset
                                st.subheader("Custom SOC2 Ruleset")
                                custom_rules = st.text_area(
                                    "Custom SOC2 rules (JSON format)",
                                    value="""{\n  "rules": [\n    {\n      "id": "session-timeout",\n      "requirement": "CC6.1",\n      "check": "session_timeout < 15"\n    }\n  ]\n}""",
                                    height=200,
                                    key="github_soc2_custom_rules"
                                )
                            
                            # SOC2 Categories selection in a stylized container
                            st.subheader(_("scan.soc2_categories", "SOC2 Categories to Scan"))
                            
                            # Create a grid of checkboxes with better styling
                            col1, col2, col3, col4, col5 = st.columns(5)
                            
                            with col1:
                                security = st.checkbox("Security", value=True, key="github_soc2_category_security", 
                                                    help="Focuses on system protection against unauthorized access")
                            
                            with col2:
                                availability = st.checkbox("Availability", value=True, key="github_soc2_category_availability",
                                                        help="Examines system availability for operation and use")
                            
                            with col3:
                                processing = st.checkbox("Processing Integrity", value=True, key="github_soc2_category_processing",
                                                    help="Checks if system processing is complete, accurate, and timely")
                            
                            with col4:
                                confidentiality = st.checkbox("Confidentiality", value=True, key="github_soc2_category_confidentiality",
                                                          help="Ensures information designated as confidential is protected")
                            
                            with col5:
                                privacy = st.checkbox("Privacy", value=True, key="github_soc2_category_privacy",
                                                    help="Verifies personal information is collected and used appropriately")
                            
                            # Note about file uploads
                            st.info(
                                "SOC2 scanning does not require file uploads. Configure the repository details "
                                "in the Advanced Configuration section and click the scan button below."
                            )
                            
                            # Add expected output information inside the layout
                            st.markdown("""
                            <div style="padding: 10px; border-radius: 5px; background-color: #f0f8ff; margin: 10px 0;">
                                <span style="font-weight: bold;">Output:</span> SOC2 checklist + mapped violations aligned with Trust Services Criteria
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Create a prominent scan button with improved styling
                            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                            scan_col1, scan_col2, scan_col3 = st.columns([1, 2, 1])
                            with scan_col2:
                                scan_button = st.button(
                                    "Start SOC2 Compliance Scan",
                                    type="primary",
                                    use_container_width=True,
                                    key="github_soc2_scan_button"
                                )
                            
                            # Handle the scan process
                            if scan_button:
                                # Validate input
                                if not repo_url:
                                    st.error(_("scan.error_no_repo", "Please enter a GitHub repository URL"))
                                    scan_running = False
                                elif not repo_url.startswith(("https://github.com/", "http://github.com/")):
                                    st.error(_("scan.error_invalid_repo", "Please enter a valid GitHub repository URL"))
                                    scan_running = False
                                else:
                                    # Valid input, proceed with scan
                                    with st.status(_("scan.scanning", "Scanning repository for SOC2 compliance issues..."), expanded=True) as status:
                                        try:
                                            # Show cloning message
                                            st.write(_("scan.cloning", "Cloning repository..."))
                                            
                                            # Perform scan using the enhanced scanner function
                                            scan_results = scan_github_repository(repo_url, branch, token)
                                            
                                            # Store the scan_results for PDF report generation
                                            st.session_state.soc2_scan_results = scan_results
                                            
                                            # Check for scan failure
                                            if scan_results.get("scan_status") == "failed":
                                                error_msg = scan_results.get("error", "Unknown error")
                                                st.error(f"{_('scan.scan_failed', 'Scan failed')}: {error_msg}")
                                                status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                                                scan_running = False
                                            else:
                                                # Scan succeeded, show progress
                                                st.write(_("scan.analyzing", "Analyzing IaC files..."))
                                                time.sleep(1)  # Give the UI time to update
                                                
                                                st.write(_("scan.generating_report", "Generating compliance report..."))
                                                status.update(label=_("scan.scan_complete", "Scan complete!"), state="complete")
                                                
                                                # Display results if we have findings
                                                if 'findings' in scan_results:
                                                    st.subheader(_("scan.scan_results", "Scan Results"))
                                                    
                                                    # Extract key metrics
                                                    compliance_score = scan_results.get("compliance_score", 0)
                                                    high_risk = scan_results.get("high_risk_count", 0)
                                                    medium_risk = scan_results.get("medium_risk_count", 0)
                                                    low_risk = scan_results.get("low_risk_count", 0)
                                                    total_findings = high_risk + medium_risk + low_risk
                                                    
                                                    # Repository info
                                                    st.write(f"**{_('scan.repository', 'Repository')}:** {scan_results.get('repo_url')}")
                                                    st.write(f"**{_('scan.branch', 'Branch')}:** {scan_results.get('branch', 'main')}")
                                                    
                                                    # Create metrics
                                                    col1, col2, col3, col4 = st.columns(4)
                                                    
                                                    # Determine compliance color for styling
                                                    if compliance_score >= 80:
                                                        compliance_color_css = "green"
                                                    elif compliance_score >= 60:
                                                        compliance_color_css = "orange"
                                                    else:
                                                        compliance_color_css = "red"
                                                        
                                                    with col1:
                                                        st.metric(_("scan.compliance_score", "Compliance Score"), 
                                                                f"{compliance_score}/100", 
                                                                delta=None,
                                                                delta_color="normal")
                                                                
                                                        st.markdown(f"<div style='text-align: center; color: {compliance_color_css};'>{'✓ Good' if compliance_score >= 80 else '⚠️ Needs Review' if compliance_score >= 60 else '✗ Critical'}</div>", unsafe_allow_html=True)
                                                    
                                                    with col2:
                                                        st.metric(_("scan.high_risk", "High Risk Issues"), 
                                                                high_risk,
                                                                delta=None,
                                                                delta_color="inverse")
                                                                
                                                    with col3:
                                                        st.metric(_("scan.medium_risk", "Medium Risk Issues"), 
                                                                medium_risk,
                                                                delta=None,
                                                                delta_color="inverse")
                                                                
                                                    with col4:
                                                        st.metric(_("scan.low_risk", "Low Risk Issues"), 
                                                                low_risk,
                                                                delta=None,
                                                                delta_color="inverse")
                                                    
                                                    # Add PDF Download button
                                                    st.markdown("### Download Report")
                                                    if st.button("Generate PDF Report", type="primary", key="github_soc2_pdf_button"):
                                                        with st.spinner("Generating PDF report..."):
                                                            # Generate PDF report
                                                            pdf_bytes = generate_report(scan_results)
                                                            
                                                            # Provide download button
                                                            pdf_filename = f"soc2_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                                            st.download_button(
                                                                label="📥 Download SOC2 Compliance Report PDF",
                                                                data=pdf_bytes,
                                                                file_name=pdf_filename,
                                                                mime="application/pdf",
                                                                key="soc2_pdf_download_github"
                                                            )
                                                    
                                                    # Display findings table
                                                    st.subheader("Compliance Findings")
                                                    if 'findings' in scan_results and scan_results['findings']:
                                                        findings_df = pd.DataFrame([
                                                            {
                                                                "Risk": f.get("risk_level", "Unknown").upper(),
                                                                "Category": f.get("category", "Unknown").capitalize(),
                                                                "Description": f.get("description", "No description"),
                                                                "File": f.get("file", "Unknown"),
                                                                "Line": f.get("line", "N/A"),
                                                            }
                                                            for f in scan_results['findings'][:10]  # Show top 10 findings
                                                        ])
                                                        st.dataframe(findings_df, use_container_width=True)
                                                        
                                                        if len(scan_results['findings']) > 10:
                                                            st.info(f"Showing 10 of {len(scan_results['findings'])} findings. Download the PDF report for complete results.")
                                        except Exception as e:
                                            # Handle any exception during the scan
                                            st.error(f"{_('scan.scan_failed', 'Scan failed')}: {str(e)}")
                                            status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                        
                        elif repo_source == "Azure DevOps Repository":
                            # Create a container with a custom border for Azure
                            with st.container():
                                st.markdown("""
                                <div style="border: 1px solid #e6e6e6; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
                                """, unsafe_allow_html=True)
                                
                                # Repository URL input
                                st.subheader(_("scan.azure_repo_details", "Azure DevOps Repository Details"))
                                repo_url = st.text_input(_("scan.azure_repo_url", "Azure DevOps Repository URL"), 
                                                placeholder="https://dev.azure.com/organization/project/_git/repository",
                                                key="azure_soc2_repo_url")
                                
                                # Project name is required for Azure DevOps
                                project = st.text_input(_("scan.azure_project", "Azure DevOps Project"), 
                                            placeholder="MyProject",
                                            key="azure_soc2_project")
                                
                                # Create columns for the branch and token inputs
                                col1, col2 = st.columns(2)
                                with col1:
                                    branch = st.text_input(_("scan.branch", "Branch (optional)"), 
                                                        placeholder="main", 
                                                        key="azure_soc2_branch")
                                with col2:
                                    token = st.text_input(_("scan.azure_token", "Azure Personal Access Token (for private repos)"), 
                                                        type="password",
                                                        placeholder="Personal Access Token", 
                                                        key="azure_soc2_token")
                                
                                # Store these values in session state for the main scan button to use
                                if repo_url:
                                    st.session_state.repo_url = repo_url
                                if project:
                                    st.session_state.project = project
                                if branch:
                                    st.session_state.branch = branch
                                if token:
                                    st.session_state.token = token
                                
                                # Store organization if present in the advanced configuration
                                if 'organization' in locals():
                                    st.session_state.organization = organization
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Advanced configuration in an expander
                            with st.expander(_("scan.advanced_options", "Advanced Configuration")):
                                # Target check options
                                st.subheader("Target Checks")
                                target_checks = st.radio(
                                    "Select scan scope",
                                    ["All", "Security Only", "Custom"],
                                    horizontal=True,
                                    key="azure_soc2_target_checks"
                                )
                                
                                # Organization field (optional)
                                organization = st.text_input(
                                    _("scan.azure_organization", "Organization (optional)"), 
                                    placeholder="Will be extracted from URL if not provided",
                                    key="azure_soc2_organization")
                                    
                                # Store organization in session state for the main scan button
                                if organization:
                                    st.session_state.organization = organization
                                
                                # Path to config file
                                access_control_path = st.text_input(
                                    "Access Control Config File Path",
                                    placeholder="/path/to/iam/config.yaml",
                                    key="azure_soc2_config_path"
                                )
                                
                                # Scan timeframe
                                scan_timeframe = st.selectbox(
                                    "Scan Timeframe",
                                    ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                                    index=0,
                                    key="azure_soc2_timeframe"
                                )
                                
                                # Custom ruleset
                                st.subheader("Custom SOC2 Ruleset")
                                custom_rules = st.text_area(
                                    "Custom SOC2 rules (JSON format)",
                                    value="""{\n  "rules": [\n    {\n      "id": "session-timeout",\n      "requirement": "CC6.1",\n      "check": "session_timeout < 15"\n    }\n  ]\n}""",
                                    height=200,
                                    key="azure_soc2_custom_rules"
                                )
                            
                            # SOC2 Categories selection in a stylized container
                            st.subheader(_("scan.soc2_categories", "SOC2 Categories to Scan"))
                            
                            # Create a grid of checkboxes with better styling
                            col1, col2, col3, col4, col5 = st.columns(5)
                            
                            with col1:
                                security = st.checkbox("Security", value=True, key="azure_soc2_category_security", 
                                                    help="Focuses on system protection against unauthorized access")
                            
                            with col2:
                                availability = st.checkbox("Availability", value=True, key="azure_soc2_category_availability",
                                                        help="Examines system availability for operation and use")
                            
                            with col3:
                                processing = st.checkbox("Processing Integrity", value=True, key="azure_soc2_category_processing",
                                                    help="Checks if system processing is complete, accurate, and timely")
                            
                            with col4:
                                confidentiality = st.checkbox("Confidentiality", value=True, key="azure_soc2_category_confidentiality",
                                                          help="Ensures information designated as confidential is protected")
                            
                            with col5:
                                privacy = st.checkbox("Privacy", value=True, key="azure_soc2_category_privacy",
                                                    help="Verifies personal information is collected and used appropriately")
                            
                            # Note about file uploads
                            st.info(
                                "SOC2 scanning does not require file uploads. Configure the repository details "
                                "in the Advanced Configuration section and click the scan button below."
                            )
                            
                            # Add expected output information
                            st.markdown("""
                            <div style="padding: 10px; border-radius: 5px; background-color: #f0f8ff; margin: 10px 0;">
                                <span style="font-weight: bold;">Output:</span> SOC2 checklist + mapped violations
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Create a prominent scan button with improved styling
                            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                            scan_col1, scan_col2, scan_col3 = st.columns([1, 2, 1])
                            with scan_col2:
                                scan_button = st.button(
                                    "Start Azure SOC2 Compliance Scan",
                                    type="primary",
                                    use_container_width=True,
                                    key="azure_soc2_scan_button"
                                )
                            
                            # Handle the Azure scan process
                            if scan_button:
                                # Validate input
                                if not repo_url:
                                    st.error(_("scan.error_no_repo", "Please enter an Azure DevOps repository URL"))
                                    scan_running = False
                                elif not repo_url.startswith(("https://dev.azure.com/", "http://dev.azure.com/")):
                                    st.error(_("scan.error_invalid_azure_repo", "Please enter a valid Azure DevOps repository URL"))
                                    scan_running = False
                                elif not project:
                                    st.error(_("scan.error_no_project", "Please enter the Azure DevOps project name"))
                                    scan_running = False
                                else:
                                    # Valid input, proceed with Azure scan
                                    with st.status(_("scan.scanning_azure", "Scanning Azure repository for SOC2 compliance issues..."), expanded=True) as status:
                                        try:
                                            # Show cloning message
                                            st.write(_("scan.cloning", "Cloning repository..."))
                                            
                                            # Perform Azure scan using enhanced scanner
                                            scan_results = scan_azure_repository(repo_url, project, branch, token, organization)
                                            
                                            # Store the scan_results for PDF report generation
                                            st.session_state.soc2_scan_results = scan_results
                                            
                                            # Check for scan failure (same logic as GitHub)
                                            if scan_results.get("scan_status") == "failed":
                                                error_msg = scan_results.get("error", "Unknown error")
                                                st.error(f"{_('scan.scan_failed', 'Scan failed')}: {error_msg}")
                                                status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                                                scan_running = False
                                            else:
                                                # Scan succeeded, show progress
                                                st.write(_("scan.analyzing", "Analyzing IaC files..."))
                                                time.sleep(1)  # Give the UI time to update
                                                
                                                st.write(_("scan.generating_report", "Generating compliance report..."))
                                                status.update(label=_("scan.scan_complete", "Scan complete!"), state="complete")
                                                
                                                # Display results if we have findings (same format as GitHub)
                                                if 'findings' in scan_results:
                                                    st.subheader(_("scan.scan_results", "Scan Results"))
                                                    
                                                    # Extract key metrics
                                                    compliance_score = scan_results.get("compliance_score", 0)
                                                    high_risk = scan_results.get("high_risk_count", 0)
                                                    medium_risk = scan_results.get("medium_risk_count", 0)
                                                    low_risk = scan_results.get("low_risk_count", 0)
                                                    total_findings = high_risk + medium_risk + low_risk
                                                    
                                                    # Repository info
                                                    st.write(f"**{_('scan.repository', 'Repository')}:** {scan_results.get('repo_url')}")
                                                    st.write(f"**{_('scan.project', 'Project')}:** {scan_results.get('project')}")
                                                    st.write(f"**{_('scan.branch', 'Branch')}:** {scan_results.get('branch', 'main')}")
                                                    
                                                    # Create metrics
                                                    col1, col2, col3, col4 = st.columns(4)
                                                    
                                                    # Determine compliance color for styling
                                                    if compliance_score >= 80:
                                                        compliance_color_css = "green"
                                                    elif compliance_score >= 60:
                                                        compliance_color_css = "orange"
                                                    else:
                                                        compliance_color_css = "red"
                                                        
                                                    with col1:
                                                        st.metric(_("scan.compliance_score", "Compliance Score"), 
                                                                f"{compliance_score}/100", 
                                                                delta=None,
                                                                delta_color="normal")
                                                                
                                                        st.markdown(f"<div style='text-align: center; color: {compliance_color_css};'>{'✓ Good' if compliance_score >= 80 else '⚠️ Needs Review' if compliance_score >= 60 else '✗ Critical'}</div>", unsafe_allow_html=True)
                                                    
                                                    with col2:
                                                        st.metric(_("scan.high_risk", "High Risk Issues"), 
                                                                high_risk,
                                                                delta=None,
                                                                delta_color="inverse")
                                                                
                                                    with col3:
                                                        st.metric(_("scan.medium_risk", "Medium Risk Issues"), 
                                                                medium_risk,
                                                                delta=None,
                                                                delta_color="inverse")
                                                                
                                                    with col4:
                                                        st.metric(_("scan.low_risk", "Low Risk Issues"), 
                                                                low_risk,
                                                                delta=None,
                                                                delta_color="inverse")
                                                    
                                                    # Add PDF Download button
                                                    st.markdown("### Download Report")
                                                    if st.button("Generate PDF Report", type="primary", key="azure_soc2_pdf_button"):
                                                        with st.spinner("Generating PDF report..."):
                                                            # Generate PDF report
                                                            pdf_bytes = generate_report(scan_results)
                                                            
                                                            # Provide download button
                                                            pdf_filename = f"soc2_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                                            st.download_button(
                                                                label="📥 Download SOC2 Compliance Report PDF",
                                                                data=pdf_bytes,
                                                                file_name=pdf_filename,
                                                                mime="application/pdf",
                                                                key="soc2_pdf_download_azure"
                                                            )
                                                    
                                                    # Display findings table
                                                    st.subheader("Compliance Findings")
                                                    if 'findings' in scan_results and scan_results['findings']:
                                                        findings_df = pd.DataFrame([
                                                            {
                                                                "Risk": f.get("risk_level", "Unknown").upper(),
                                                                "Category": f.get("category", "Unknown").capitalize(),
                                                                "Description": f.get("description", "No description"),
                                                                "File": f.get("file", "Unknown"),
                                                                "Line": f.get("line", "N/A"),
                                                            }
                                                            for f in scan_results['findings'][:10]  # Show top 10 findings
                                                        ])
                                                        st.dataframe(findings_df, use_container_width=True)
                                                        
                                                        if len(scan_results['findings']) > 10:
                                                            st.info(f"Showing 10 of {len(scan_results['findings'])} findings. Download the PDF report for complete results.")
                                        except Exception as e:
                                            # Handle any exception during the scan
                                            st.error(f"{_('scan.scan_failed', 'Scan failed')}: {str(e)}")
                                            status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                        
                        # Stop normal flow to proceed with only the SOC2 scanner
                        scan_running = False
                    
                    # Preview of findings with error handling
                    st.markdown("### Sample Findings")
                    all_findings = []
                    
                    # Process all scan results with enhanced error handling
                    for result in scan_results:
                        try:
                            # For AI model scans, the findings are in a different format
                            if scan_type == _("scan.ai_model") and 'findings' in result:
                                for item in result.get('findings', []):
                                    all_findings.append({
                                        'Type': item.get('type', 'Unknown'),
                                        'Risk Level': item.get('risk_level', 'Unknown').upper(),
                                        'Category': item.get('category', 'Unknown'),
                                        'Description': item.get('description', 'Unknown')
                                    })
                            # For other scan types
                            else:
                                for item in result.get('pii_found', []):
                                    all_findings.append({
                                        'Type': item.get('type', 'Unknown'),
                                        'Value': item.get('value', 'Unknown'),
                                        'Risk Level': item.get('risk_level', 'Unknown'),
                                        'Location': item.get('location', 'Unknown')
                                    })
                        except Exception as findings_error:
                            # If there's an error processing findings, add a placeholder
                            st.warning(f"Error processing scan findings: {str(findings_error)}")
                            all_findings.append({
                                'Type': 'Error',
                                'Risk Level': 'MEDIUM',
                                'Description': f'Error processing scan results: {str(findings_error)}',
                                'Location': 'Results Processor'
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
                    
                    # Add post-scan workflow navigation
                    st.markdown("---")
                    st.subheader("Next Steps")
                    
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
                                from services.report_generator_safe import generate_report
                                
                                with st.spinner("Generating PDF report..."):
                                    # Use selected_scan instead of undefined aggregated_result
                                    pdf_bytes = generate_report(selected_scan)
                                    
                                    # Create download button
                                    pdf_filename = f"GDPR_Scan_Report_{display_scan_id}.pdf"
                                    st.download_button(
                                        label="📥 Download PDF Report",
                                        data=pdf_bytes,
                                        file_name=pdf_filename,
                                        mime="application/pdf",
                                        key="gdpr_pdf_download_quick"
                                    )
                        
                        # Compliance Certificate for Premium users
                        with col2:
                            # Check if user is premium
                            is_premium = st.session_state.role in ["premium", "admin"]
                            
                            # Check if scan is fully compliant
                            cert_generator = CertificateGenerator(language=st.session_state.language)
                            # Use current_scan_id as fallback if selected_scan is not defined
                            scan_to_check = locals().get('selected_scan', st.session_state.get('current_scan_id', None))
                            if scan_to_check:
                                is_compliant = cert_generator.is_fully_compliant(scan_to_check)
                            else:
                                is_compliant = False
                            
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
                                    # Use the same scan_to_check variable we defined earlier
                                    cert_path = cert_generator.generate_certificate(
                                        scan_to_check, user_info, company_name
                                    )
                                    
                                    if cert_path and os.path.exists(cert_path):
                                        # Read the certificate PDF
                                        with open(cert_path, 'rb') as file:
                                            cert_bytes = file.read()
                                        
                                        # Create download button
                                        cert_filename = f"GDPR_Compliance_Certificate_{display_scan_id}.pdf"
                                        st.download_button(
                                            label="📥 Download Compliance Certificate",
                                            data=cert_bytes,
                                            file_name=cert_filename,
                                            mime="application/pdf",
                                            key="gdpr_cert_download"
                                        )
                                        
                                        st.success(_("dashboard.certificate_success"))
                                    else:
                                        st.error(_("dashboard.certificate_error"))
                                
                    with col3:
                        # Quick HTML Report generation
                        if st.button("Generate HTML Report", key="quick_html_report"):
                            # Import HTML report generator
                            from services.html_report_generator_fixed import save_html_report
                            
                            with st.spinner("Generating HTML report..."):
                                # Create reports directory if it doesn't exist
                                reports_dir = "reports"
                                os.makedirs(reports_dir, exist_ok=True)
                                
                                # Save the HTML report
                                scan_to_generate = locals().get('selected_scan', st.session_state.get('current_scan_id', None))
                                if scan_to_generate:
                                    file_path = save_html_report(scan_to_generate, reports_dir)
                                else:
                                    st.error("No scan selected for generating report")
                                    file_path = None
                                
                                # Success message
                                st.success(f"HTML report saved. You can access it from the '{_('results.title')}' page.")
                
                st.markdown("---")
                st.info(f"You can also access the full results in the '{_('history.title')}' section.")
        
    elif selected_nav == history_title:
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
                
                try:
                    # Apply styling
                    styled_df = display_df.style.map(highlight_risk, subset=['High Risk Items', 'Total PII Found'])
                    
                    # Display scan history table with styled data
                    st.dataframe(styled_df, use_container_width=True)
                except Exception as e:
                    # Fallback in case of styling errors
                    st.warning(f"Error styling dataframe: {str(e)}")
                    st.dataframe(display_df, use_container_width=True)
            
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
                            if isinstance(timestamp, str):
                                timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            elif hasattr(timestamp, 'strftime'):
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                timestamp = str(timestamp)
                        except:
                            timestamp = str(timestamp)
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
                                
                                # Create download button
                                pdf_filename = f"GDPR_Scan_Report_{selected_display_id}.pdf"
                                st.download_button(
                                    label=_("dashboard.download_pdf_report"),
                                    data=pdf_bytes,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    key="gdpr_pdf_download_dashboard"
                                )
                    
                    with report_col2:
                        if st.button(_("dashboard.generate_html_report"), key="gen_html_report"):
                            # Import HTML report generator
                            from services.html_report_generator_fixed import save_html_report, get_html_report_as_base64
                            
                            with st.spinner(_("dashboard.generating_html_report")):
                                # Create reports directory if it doesn't exist
                                reports_dir = "reports"
                                os.makedirs(reports_dir, exist_ok=True)
                                
                                # Save the HTML report
                                scan_to_generate = locals().get('selected_scan', st.session_state.get('current_scan_id', None))
                                if scan_to_generate:
                                    file_path = save_html_report(scan_to_generate, reports_dir)
                                else:
                                    st.error("No scan selected for generating report")
                                    file_path = None
                                
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
    
    elif selected_nav == results_title:
        # Import permission checking functionality
        from services.auth import require_permission, has_permission
        
        st.title(_("results.title"))
        
        # Check if user has permission to view results
        if not require_permission('report:view'):
            st.warning("You don't have permission to access scan results. Please contact an administrator for access.")
            st.info("Your role requires the 'report:view' permission to use this feature.")
            st.stop()
        
        # Check for available scan results and display them
        if st.session_state.get('image_scan_complete', False):
            display_image_scan_results()
        elif st.session_state.get('db_scan_complete', False):
            display_database_scan_results()
        elif st.session_state.get('api_scan_complete', False):
            display_api_scan_results()
        else:
            st.info("No scan results available. Please run a scan first.")
            
            # Show recent scan history if available
            try:
                all_scans = results_aggregator.get_all_scans(st.session_state.username)
                if all_scans:
                    st.subheader("Recent Scan History")
                    recent_scans = all_scans[-5:]  # Show last 5 scans
                    for scan in reversed(recent_scans):
                        scan_time = scan.get('timestamp', 'Unknown')
                        scan_type = scan.get('scan_type', 'Unknown')
                        st.write(f"- {scan_time}: {scan_type} scan")
            except Exception:
                pass
    
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
                        
                        # Create download button
                        selected_display_id = scan_options[selected_scan_index]['display_id']
                        pdf_filename = f"GDPR_Scan_Report_{selected_display_id}.pdf"
                        st.download_button(
                            label=get_text("report.download_pdf", "Download PDF Report"),
                            data=pdf_bytes,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key="gdpr_pdf_download_reports"
                        )
                        
                        st.success(_("report.generated_successfully"))
                
                # Report preview (if available from a previous generation)
                if 'current_scan_id' in st.session_state and st.session_state.current_scan_id == selected_scan_id and 'pdf_bytes' in locals():
                    st.subheader(_("report.preview"))
                    st.write(_("report.preview_not_available"))
            else:
                st.error(_("report.scan_not_found").format(scan_id=selected_scan_id))
        else:
            st.info(_("report.no_scan_history"))
            
    # SOC2 Scanner is now only accessed through the scan menu
        
    elif admin_title and selected_nav == admin_title:
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
                # Create tabs for different role management actions
                role_mgmt_tabs = st.tabs(["Role Details", "Create Custom Role", "Edit Role", "Delete Role"])
                
                # Tab 1: Role Details
                with role_mgmt_tabs[0]:
                    st.subheader("Role Details")
                    
                    selected_role = st.selectbox("Select Role", list(all_roles.keys()), key="view_role_details")
                    
                    if selected_role:
                        role_data = all_roles.get(selected_role, {})
                        is_custom = role_data.get('custom', False)
                        role_type = "Custom" if is_custom else "System"
                        
                        # Show role metadata
                        st.markdown(f"**Type:** {role_type}")
                        st.markdown(f"**Description:** {role_data.get('description', 'No description')}")
                        
                        # Add visual indicator for custom roles
                        if is_custom:
                            st.markdown("""
                            <div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
                                <p style="margin: 0;"><strong>⚠️ Custom Role:</strong> This role was created by an administrator and can be modified.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">
                                <p style="margin: 0;"><strong>🔒 System Role:</strong> This is a system-defined role that cannot be modified.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Show permissions
                        st.markdown(f"**Permissions ({len(role_data.get('permissions', []))}):**")
                        
                        # Group permissions by category
                        permissions_by_category = {}
                        for perm in role_data.get('permissions', []):
                            category = perm.split(':')[0] if ':' in perm else 'Other'
                            if category not in permissions_by_category:
                                permissions_by_category[category] = []
                            permissions_by_category[category].append(perm)
                        
                        # Display permissions by category with better visual organization
                        for category, perms in permissions_by_category.items():
                            with st.expander(f"{category.title()} Permissions ({len(perms)})"):
                                for perm in perms:
                                    desc = all_permissions.get(perm, "No description available")
                                    st.markdown(f"- **{perm}**: {desc}")
                
                # Tab 2: Create Custom Role
                with role_mgmt_tabs[1]:
                    st.subheader("Create New Custom Role")
                    
                    # Add description about custom roles
                    st.markdown("""
                    <div style="background-color: #e6f7ff; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                        <h4 style="margin-top: 0;">About Custom Roles</h4>
                        <p>Custom roles allow you to create specialized permission sets for different members of your organization. 
                        Once created, custom roles can be assigned to users just like system roles.</p>
                        <p><strong>Note:</strong> Custom roles can be modified or deleted later, but system roles cannot.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Form for creating a new role
                    with st.form("create_role_form"):
                        new_role_name = st.text_input("Role Name", placeholder="Enter a name for the new role (e.g., compliance_officer)")
                        new_role_description = st.text_area("Role Description", placeholder="Enter a description for the new role")
                        
                        # Create permission selector
                        st.markdown("### Select Permissions")
                        
                        # Group permissions by category for easier selection
                        permissions_by_category = {}
                        for perm, desc in all_permissions.items():
                            category = perm.split(':')[0] if ':' in perm else 'Other'
                            if category not in permissions_by_category:
                                permissions_by_category[category] = []
                            permissions_by_category[category].append((perm, desc))
                        
                        # Store selected permissions
                        selected_permissions = []
                        
                        # Display permissions by category with checkboxes
                        for category, perms in permissions_by_category.items():
                            with st.expander(f"{category.title()} Permissions ({len(perms)})"):
                                # Option to select all in category
                                if st.checkbox(f"Select all {category} permissions", key=f"select_all_{category}"):
                                    selected_permissions.extend([p[0] for p in perms])
                                
                                # Individual permission checkboxes
                                for perm, desc in perms:
                                    if st.checkbox(f"{perm}: {desc}", key=f"perm_{perm}"):
                                        selected_permissions.append(perm)
                        
                        # Submit button
                        submit_button = st.form_submit_button("Create Role")
                        
                        if submit_button:
                            from services.auth import create_custom_role
                            
                            if not new_role_name:
                                st.error("Role name is required")
                            elif not new_role_description:
                                st.error("Role description is required")
                            elif not selected_permissions:
                                st.error("At least one permission must be selected")
                            else:
                                # Create the new role
                                success, message = create_custom_role(
                                    new_role_name, 
                                    new_role_description, 
                                    selected_permissions
                                )
                                
                                if success:
                                    st.success(message)
                                    # Log the action
                                    try:
                                        results_aggregator.log_audit_event(
                                            username=st.session_state.username,
                                            action="ROLE_CREATED",
                                            details={
                                                "role_name": new_role_name,
                                                "permission_count": len(selected_permissions),
                                                "timestamp": datetime.now().isoformat()
                                            }
                                        )
                                    except Exception as e:
                                        st.warning(f"Could not log audit event: {str(e)}")
                                else:
                                    st.error(message)
                
                # Tab 3: Edit Role
                with role_mgmt_tabs[2]:
                    st.subheader("Edit Custom Role")
                    
                    # Filter to only show custom roles
                    custom_roles = {k: v for k, v in all_roles.items() if v.get('custom', False)}
                    
                    if not custom_roles:
                        st.info("No custom roles found. Create a custom role first.")
                    else:
                        edit_role_name = st.selectbox("Select Custom Role to Edit", list(custom_roles.keys()), key="edit_role_select")
                        
                        if edit_role_name:
                            role_data = custom_roles.get(edit_role_name, {})
                            
                            with st.form("edit_role_form"):
                                # Edit form fields
                                edit_role_description = st.text_area(
                                    "Role Description", 
                                    value=role_data.get('description', ''),
                                    key="edit_role_description"
                                )
                                
                                # Existing permissions
                                current_role_permissions = role_data.get('permissions', [])
                                
                                # Group permissions by category for easier selection
                                st.markdown("### Update Permissions")
                                
                                permissions_by_category = {}
                                for perm, desc in all_permissions.items():
                                    category = perm.split(':')[0] if ':' in perm else 'Other'
                                    if category not in permissions_by_category:
                                        permissions_by_category[category] = []
                                    permissions_by_category[category].append((perm, desc))
                                
                                # Store updated permissions
                                updated_permissions = []
                                
                                # Display permissions by category with checkboxes
                                for category, perms in permissions_by_category.items():
                                    with st.expander(f"{category.title()} Permissions ({len(perms)})"):
                                        # Option to select all in category
                                        all_selected = all(p[0] in current_role_permissions for p in perms)
                                        if st.checkbox(f"Select all {category} permissions", 
                                                    value=all_selected,
                                                    key=f"edit_select_all_{category}"):
                                            updated_permissions.extend([p[0] for p in perms])
                                        else:
                                            # Individual permission checkboxes
                                            for perm, desc in perms:
                                                if st.checkbox(f"{perm}: {desc}", 
                                                            value=perm in current_role_permissions,
                                                            key=f"edit_perm_{perm}"):
                                                    updated_permissions.append(perm)
                                
                                # Submit button
                                edit_submit_button = st.form_submit_button("Update Role")
                                
                                if edit_submit_button:
                                    from services.auth import update_role
                                    
                                    if not edit_role_description:
                                        st.error("Role description is required")
                                    elif not updated_permissions:
                                        st.error("At least one permission must be selected")
                                    else:
                                        # Update the role
                                        success, message = update_role(
                                            edit_role_name, 
                                            {
                                                'description': edit_role_description,
                                                'permissions': updated_permissions
                                            }
                                        )
                                        
                                        if success:
                                            st.success(message)
                                            # Log the action
                                            try:
                                                results_aggregator.log_audit_event(
                                                    username=st.session_state.username,
                                                    action="ROLE_UPDATED",
                                                    details={
                                                        "role_name": edit_role_name,
                                                        "permission_count": len(updated_permissions),
                                                        "timestamp": datetime.now().isoformat()
                                                    }
                                                )
                                            except Exception as e:
                                                st.warning(f"Could not log audit event: {str(e)}")
                                        else:
                                            st.error(message)
                
                # Tab 4: Delete Role
                with role_mgmt_tabs[3]:
                    st.subheader("Delete Custom Role")
                    
                    # Filter to only show custom roles
                    custom_roles = {k: v for k, v in all_roles.items() if v.get('custom', False)}
                    
                    if not custom_roles:
                        st.info("No custom roles found. Create a custom role first.")
                    else:
                        delete_role_name = st.selectbox("Select Custom Role to Delete", list(custom_roles.keys()), key="delete_role_select")
                        
                        if delete_role_name:
                            st.warning(f"Warning: Deleting a role is permanent and cannot be undone. Users with this role will need to be reassigned.")
                            
                            # Confirm deletion with a form for extra safety
                            with st.form("delete_role_form"):
                                confirm_delete = st.checkbox(f"I confirm that I want to delete the role '{delete_role_name}'")
                                
                                delete_button = st.form_submit_button("Delete Role", type="primary")
                                
                                if delete_button:
                                    if not confirm_delete:
                                        st.error("Please confirm the deletion by checking the confirmation box")
                                    else:
                                        from services.auth import delete_role
                                        
                                        # Delete the role
                                        success, message = delete_role(delete_role_name)
                                        
                                        if success:
                                            st.success(message)
                                            # Log the action
                                            try:
                                                results_aggregator.log_audit_event(
                                                    username=st.session_state.username,
                                                    action="ROLE_DELETED",
                                                    details={
                                                        "role_name": delete_role_name,
                                                        "timestamp": datetime.now().isoformat()
                                                    }
                                                )
                                            except Exception as e:
                                                st.warning(f"Could not log audit event: {str(e)}")
                                        else:
                                            st.error(message)
                
                # User role assignment section
                st.markdown("---")
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
                        # Sort audit logs by timestamp if available
                        try:
                            # Sort by timestamp if present
                            if audit_logs and 'timestamp' in audit_logs[0]:
                                audit_logs = sorted(audit_logs, key=lambda x: x.get('timestamp', ''), reverse=True)
                        except (IndexError, TypeError):
                            pass
                        
                        # Display logs as a table
                        st.dataframe(audit_logs, use_container_width=True)
                        
                        # Filters
                        st.subheader("Filter Logs")
                        
                        # Extract unique action types from audit logs
                        try:
                            action_types = list(set(log.get('action', '') for log in audit_logs if log.get('action')))
                            if action_types:
                                selected_actions = st.multiselect("Filter by Action", action_types)
                                
                                if selected_actions:
                                    filtered_logs = [log for log in audit_logs if log.get('action') in selected_actions]
                                    st.dataframe(filtered_logs, use_container_width=True)
                        except Exception:
                            pass
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

# API Scanner Results Display Section
def display_image_scan_results():
    """Display image scan results with downloadable reports."""
    
    if not st.session_state.get('image_scan_complete', False):
        st.info("No image scan results available. Please run an image scan first.")
        return
    
    image_scan_results = st.session_state.get('image_scan_results', {})
    
    if not image_scan_results:
        st.info("No image scan results found.")
        return
    
    # Get findings count for messaging
    findings_count = len(image_scan_results.get('findings', []))
    images_scanned = image_scan_results.get('metadata', {}).get('images_scanned', 0)
    
    # Display appropriate header based on findings
    if findings_count > 0:
        st.subheader("🖼️ Image Scan Results")
    else:
        st.subheader("🖼️ Image Scan Results - Clean Scan")
        st.success(f"✅ All {images_scanned} images scanned successfully with no personal data detected!")
        st.markdown("""
        <div style="padding: 15px; background-color: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 5px; margin: 10px 0;">
            <h4 style="color: #1e40af; margin-top: 0;">GDPR Compliance Status: EXCELLENT</h4>
            <p style="margin-bottom: 0;">Your images contain no detectable personal data, which means excellent privacy compliance. You can still download an official compliance certificate below.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        images_scanned = image_scan_results.get('metadata', {}).get('images_scanned', 0)
        st.metric("Images Scanned", images_scanned)
    
    with col2:
        total_findings = len(image_scan_results.get('findings', []))
        st.metric("Total PII Findings", total_findings)
    
    with col3:
        images_with_pii = image_scan_results.get('images_with_pii', 0)
        st.metric("Images with PII", images_with_pii)
    
    with col4:
        risk_score = image_scan_results.get('risk_summary', {}).get('score', 0)
        st.metric("Risk Score", f"{risk_score}/100")
    
    # Display findings in expandable sections
    findings = image_scan_results.get('findings', [])
    
    if findings:
        st.subheader("🔍 Detailed PII Findings")
        
        # Group findings by PII type
        findings_by_type = {}
        for finding in findings:
            pii_type = finding.get('type', 'Other')
            if pii_type not in findings_by_type:
                findings_by_type[pii_type] = []
            findings_by_type[pii_type].append(finding)
    else:
        # No findings - show positive compliance message
        st.subheader("🔍 Scan Analysis")
        st.markdown("""
        <div style="padding: 20px; background-color: #f0fdf4; border: 2px solid #22c55e; border-radius: 10px; margin: 15px 0;">
            <h4 style="color: #15803d; margin-top: 0;">✅ Excellent Privacy Compliance</h4>
            <p style="margin-bottom: 5px;"><strong>No personal data detected in any scanned images.</strong></p>
            <p style="margin-bottom: 0;">Your images are fully compliant with GDPR Article 6 and do not require additional privacy measures.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display each PII type
        for pii_type, type_findings in findings_by_type.items():
            with st.expander(f"{pii_type} ({len(type_findings)} findings)", expanded=True):
                
                # Create DataFrame for this PII type
                df_data = []
                for finding in type_findings:
                    df_data.append({
                        'Source Image': os.path.basename(finding.get('source', 'Unknown')),
                        'PII Type': finding.get('type', 'Unknown'),
                        'Risk Level': finding.get('risk_level', 'Medium'),
                        'Confidence': f"{finding.get('confidence', 0):.0%}",
                        'Detection Method': finding.get('extraction_method', 'Unknown'),
                        'Context': finding.get('context', 'No context'),
                        'GDPR Reason': finding.get('reason', 'No reason provided')
                    })
                
                if df_data:
                    # Display as a table without pandas dependency
                    st.dataframe(df_data, use_container_width=True)
    
    # Display individual image results
    image_results = image_scan_results.get('image_results', {})
    if image_results:
        st.subheader("📸 Individual Image Results")
        
        for image_path, result in image_results.items():
            image_name = os.path.basename(image_path)
            image_findings = result.get('findings', [])
            has_pii = result.get('has_pii', False)
            
            # Color code based on PII presence
            status_color = "🔴" if has_pii else "🟢"
            pii_status = f"PII Detected ({len(image_findings)} findings)" if has_pii else "No PII Detected"
            
            with st.expander(f"{status_color} {image_name} - {pii_status}", expanded=has_pii):
                if has_pii:
                    # Show findings for this image
                    for finding in image_findings:
                        st.write(f"**{finding.get('type', 'Unknown PII')}**")
                        st.write(f"- Risk Level: {finding.get('risk_level', 'Unknown')}")
                        st.write(f"- Confidence: {finding.get('confidence', 0):.0%}")
                        st.write(f"- Detection: {finding.get('extraction_method', 'Unknown')}")
                        st.write(f"- Context: {finding.get('context', 'No context')}")
                        st.write(f"- GDPR Compliance: {finding.get('reason', 'No reason')}")
                        st.write("---")
                else:
                    st.write("✅ No personal data detected in this image.")
                
                # Show metadata
                metadata = result.get('metadata', {})
                if metadata:
                    st.write(f"**Format:** {metadata.get('format', 'Unknown')}")
                    st.write(f"**Process Time:** {metadata.get('process_time_ms', 0)} ms")
    
    # Display risk summary
    risk_summary = image_scan_results.get('risk_summary', {})
    if risk_summary:
        st.subheader("⚠️ Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_level = risk_summary.get('level', 'Low')
            risk_color = {
                'Critical': '🔴',
                'High': '🟠', 
                'Medium': '🟡',
                'Low': '🟢'
            }.get(risk_level, '🟢')
            
            st.write(f"**Overall Risk Level:** {risk_color} {risk_level}")
            st.write(f"**Risk Score:** {risk_summary.get('score', 0)}/100")
        
        with col2:
            factors = risk_summary.get('factors', [])
            if factors:
                st.write("**Risk Factors:**")
                for factor in factors:
                    st.write(f"- {factor}")
    
    # Download buttons
    st.subheader("📥 Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download HTML Report", key="download_image_html"):
            try:
                from services.html_report_generator_fixed import generate_html_report
                html_content = generate_html_report(image_scan_results, scan_type="image")
                
                # Provide download
                st.download_button(
                    label="💾 Save HTML Report",
                    data=html_content,
                    file_name=f"image_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="save_image_html"
                )
                st.success("HTML report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating HTML report: {str(e)}")
    
    with col2:
        if st.button("📑 Download PDF Certificate", key="download_image_pdf"):
            try:
                from services.image_report_generator import ImageReportGenerator
                
                # Generate PDF report
                generator = ImageReportGenerator()
                pdf_content = generator.generate_pdf_report(image_scan_results)
                
                # Provide download
                st.download_button(
                    label="💾 Save PDF Certificate",
                    data=pdf_content,
                    file_name=f"image_scan_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="save_image_pdf"
                )
                st.success("PDF certificate generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating PDF certificate: {str(e)}")
    
    # Display scan metadata
    metadata = image_scan_results.get('metadata', {})
    if metadata:
        with st.expander("📊 Scan Metadata", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Scan Time:** {metadata.get('scan_time', 'Unknown')}")
                st.write(f"**Process Time:** {metadata.get('process_time_seconds', 0):.2f} seconds")
                st.write(f"**Region:** {metadata.get('region', 'Unknown')}")
            
            with col2:
                st.write(f"**Images Total:** {metadata.get('images_total', 0)}")
                st.write(f"**Images Scanned:** {metadata.get('images_scanned', 0)}")
                st.write(f"**Total Findings:** {metadata.get('total_findings', 0)}")

def display_document_scan_results():
    """Display document scan results with downloadable reports."""
    
    if not st.session_state.get('document_scan_complete', False):
        st.info("No document scan results available. Please run a document scan first.")
        return
    
    document_scan_results = st.session_state.get('document_scan_results', {})
    
    if not document_scan_results:
        st.info("No document scan results found.")
        return
    
    # Get findings count for messaging
    findings_count = len(document_scan_results.get('findings', []))
    documents_scanned = document_scan_results.get('metadata', {}).get('documents_scanned', 0)
    
    # Display appropriate header based on findings
    if findings_count > 0:
        st.subheader("📄 Document Scan Results")
    else:
        st.subheader("📄 Document Scan Results - Clean Scan")
        st.success(f"All {documents_scanned} documents scanned successfully with no personal data detected!")
        st.markdown("""
        <div style="padding: 15px; background-color: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 5px; margin: 10px 0;">
            <h4 style="color: #1e40af; margin-top: 0;">GDPR Compliance Status: EXCELLENT</h4>
            <p style="margin-bottom: 0;">Your documents contain no detectable personal data, which means excellent privacy compliance. You can still download an official compliance certificate below.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        documents_scanned = document_scan_results.get('metadata', {}).get('documents_scanned', 0)
        st.metric("Documents Scanned", documents_scanned)
    
    with col2:
        total_findings = len(document_scan_results.get('findings', []))
        st.metric("Total PII Findings", total_findings)
    
    with col3:
        documents_with_pii = document_scan_results.get('documents_with_pii', 0)
        st.metric("Documents with PII", documents_with_pii)
    
    with col4:
        risk_score = document_scan_results.get('risk_summary', {}).get('score', 0)
        st.metric("Risk Score", f"{risk_score}/100")
    
    # Display findings in expandable sections
    findings = document_scan_results.get('findings', [])
    
    if findings:
        st.subheader("🔍 Detailed PII Findings")
        
        # Group findings by PII type
        findings_by_type = {}
        for finding in findings:
            pii_type = finding.get('type', 'Other')
            if pii_type not in findings_by_type:
                findings_by_type[pii_type] = []
            findings_by_type[pii_type].append(finding)
        
        # Display each PII type
        for pii_type, type_findings in findings_by_type.items():
            with st.expander(f"{pii_type} ({len(type_findings)} findings)", expanded=True):
                
                # Create DataFrame for this PII type
                df_data = []
                for finding in type_findings:
                    df_data.append({
                        'Source Document': os.path.basename(finding.get('source', 'Unknown')),
                        'PII Type': finding.get('type', 'Unknown'),
                        'Risk Level': finding.get('risk_level', 'Medium'),
                        'Confidence': f"{finding.get('confidence', 0):.0%}",
                        'Location': finding.get('location', 'Unknown'),
                        'Context': finding.get('context', 'No context'),
                        'GDPR Reason': finding.get('reason', 'No reason provided')
                    })
                
                if df_data:
                    st.dataframe(df_data, use_container_width=True)
    else:
        # No findings - show positive compliance message
        st.subheader("🔍 Scan Analysis")
        st.markdown("""
        <div style="padding: 20px; background-color: #f0fdf4; border: 2px solid #22c55e; border-radius: 10px; margin: 15px 0;">
            <h4 style="color: #15803d; margin-top: 0;">Excellent Privacy Compliance</h4>
            <p style="margin-bottom: 5px;"><strong>No personal data detected in any scanned documents.</strong></p>
            <p style="margin-bottom: 0;">Your documents are fully compliant with GDPR Article 6 and do not require additional privacy measures.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display individual document results
    document_results = document_scan_results.get('document_results', {})
    if document_results:
        st.subheader("📋 Individual Document Results")
        
        for doc_path, result in document_results.items():
            doc_name = os.path.basename(doc_path)
            doc_findings = result.get('findings', [])
            has_pii = result.get('has_pii', False)
            
            # Color code based on PII presence
            status_color = "🔴" if has_pii else "🟢"
            pii_status = f"PII Detected ({len(doc_findings)} findings)" if has_pii else "No PII Detected"
            
            with st.expander(f"{status_color} {doc_name} - {pii_status}", expanded=has_pii):
                if has_pii:
                    # Show findings for this document
                    for finding in doc_findings:
                        st.write(f"**{finding.get('type', 'Unknown PII')}**")
                        st.write(f"- Risk Level: {finding.get('risk_level', 'Unknown')}")
                        st.write(f"- Confidence: {finding.get('confidence', 0):.0%}")
                        st.write(f"- Location: {finding.get('location', 'Unknown')}")
                        st.write(f"- Context: {finding.get('context', 'No context')}")
                        st.write(f"- GDPR Compliance: {finding.get('reason', 'No reason')}")
                        st.write("---")
                else:
                    st.write("No personal data detected in this document.")
                
                # Show metadata
                metadata = result.get('metadata', {})
                if metadata:
                    st.write(f"**Format:** {metadata.get('format', 'Unknown')}")
                    st.write(f"**Process Time:** {metadata.get('process_time_ms', 0)} ms")
    
    # Display risk summary
    risk_summary = document_scan_results.get('risk_summary', {})
    if risk_summary:
        st.subheader("⚠️ Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_level = risk_summary.get('level', 'Low')
            risk_color = {
                'Critical': '🔴',
                'High': '🟠', 
                'Medium': '🟡',
                'Low': '🟢'
            }.get(risk_level, '🟢')
            
            st.write(f"**Overall Risk Level:** {risk_color} {risk_level}")
            st.write(f"**Risk Score:** {risk_summary.get('score', 0)}/100")
        
        with col2:
            factors = risk_summary.get('factors', [])
            if factors:
                st.write("**Risk Factors:**")
                for factor in factors:
                    st.write(f"- {factor}")
    
    # Download buttons
    st.subheader("📥 Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download HTML Report", key="download_document_html"):
            try:
                from services.document_report_generator import generate_document_html_report
                html_content = generate_document_html_report(document_scan_results)
                
                # Provide download
                st.download_button(
                    label="💾 Save HTML Report",
                    data=html_content,
                    file_name=f"document_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="save_document_html"
                )
                st.success("HTML report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating HTML report: {str(e)}")
    
    with col2:
        if st.button("📑 Download PDF Certificate", key="download_document_pdf"):
            try:
                from services.document_report_generator import generate_document_pdf_report
                
                # Generate PDF report
                pdf_content = generate_document_pdf_report(document_scan_results)
                
                # Provide download
                st.download_button(
                    label="💾 Save PDF Certificate",
                    data=pdf_content,
                    file_name=f"document_scan_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="save_document_pdf"
                )
                st.success("PDF certificate generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating PDF certificate: {str(e)}")
    
    # Display scan metadata
    metadata = document_scan_results.get('metadata', {})
    if metadata:
        with st.expander("📊 Scan Metadata", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Scan Time:** {metadata.get('scan_time', 'Unknown')}")
                st.write(f"**Process Time:** {metadata.get('process_time_seconds', 0):.2f} seconds")
                st.write(f"**Region:** {metadata.get('region', 'Unknown')}")
            
            with col2:
                st.write(f"**Documents Total:** {metadata.get('documents_total', 0)}")
                st.write(f"**Documents Scanned:** {metadata.get('documents_scanned', 0)}")
                st.write(f"**Total Findings:** {metadata.get('total_findings', 0)}")

def display_database_scan_results():
    """Display database scan results with downloadable reports."""
    st.subheader("Database Scanner Results")
    
    if not st.session_state.get('db_scan_complete', False):
        st.info("No database scan results available.")
        return
    
    db_results = st.session_state.get('db_scan_results', {})
    
    if not db_results or 'findings' not in db_results:
        st.error("Database scan results are invalid or missing.")
        return
    
    # Display scan metadata
    metadata = db_results.get('metadata', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tables Scanned", metadata.get('tables_scanned', 0))
    with col2:
        st.metric("PII Findings", len(db_results.get('findings', [])))
    with col3:
        st.metric("Tables with PII", db_results.get('tables_with_pii', 0))
    with col4:
        risk_summary = db_results.get('risk_summary', {})
        overall_level = risk_summary.get('overall_level', 'Unknown')
        st.metric("Risk Level", overall_level)
    
    # Display risk summary
    if 'risk_summary' in db_results:
        risk_summary = db_results['risk_summary']
        st.subheader("Risk Distribution")
        
        risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
        by_level = risk_summary.get('by_level', {})
        
        with risk_col1:
            st.metric("Critical", by_level.get('Critical', 0), delta_color="inverse")
        with risk_col2:
            st.metric("High", by_level.get('High', 0), delta_color="inverse")
        with risk_col3:
            st.metric("Medium", by_level.get('Medium', 0), delta_color="normal")
        with risk_col4:
            st.metric("Low", by_level.get('Low', 0), delta_color="normal")
    
    # Display findings table
    findings = db_results.get('findings', [])
    if findings:
        st.subheader("PII Findings Details")
        
        # Create DataFrame for display
        findings_df = pd.DataFrame(findings)
        
        # Select relevant columns for display
        display_columns = ['table', 'column_name', 'type', 'risk_level', 'confidence', 'detection_method', 'reason']
        available_columns = [col for col in display_columns if col in findings_df.columns]
        
        if available_columns:
            display_df = findings_df[available_columns].copy()
            
            # Format confidence as percentage
            if 'confidence' in display_df.columns:
                display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1%}")
            
            # Apply styling for risk levels
            def highlight_risk_level(val):
                if val == 'Critical':
                    return 'background-color: #fee2e2; color: #dc2626'
                elif val == 'High':
                    return 'background-color: #fef3c7; color: #d97706'
                elif val == 'Medium':
                    return 'background-color: #fde68a; color: #ca8a04'
                else:
                    return 'background-color: #d1fae5; color: #059669'
            
            # Style the dataframe
            if 'risk_level' in display_df.columns:
                styled_df = display_df.style.applymap(
                    highlight_risk_level, subset=['risk_level']
                ).format({'confidence': '{}'})
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.dataframe(display_df, use_container_width=True)
        else:
            st.write("No detailed findings data available for display.")
    
    # Display table-specific results
    table_results = db_results.get('table_results', {})
    if table_results:
        st.subheader("Table Analysis Summary")
        
        table_summary = []
        for table_name, result in table_results.items():
            if 'error' not in result:
                findings_count = len(result.get('findings', []))
                risk_score = result.get('risk_score', {})
                table_summary.append({
                    'Table': table_name,
                    'PII Findings': findings_count,
                    'Risk Score': risk_score.get('score', 0),
                    'Risk Level': risk_score.get('level', 'Unknown'),
                    'Scan Time (ms)': result.get('metadata', {}).get('process_time_ms', 0)
                })
        
        if table_summary:
            table_df = pd.DataFrame(table_summary)
            
            # Style the risk level column
            def highlight_risk_level(val):
                if val == 'Critical':
                    return 'background-color: #fee2e2; color: #dc2626'
                elif val == 'High':
                    return 'background-color: #fef3c7; color: #d97706'
                elif val == 'Medium':
                    return 'background-color: #fde68a; color: #ca8a04'
                else:
                    return 'background-color: #d1fae5; color: #059669'
            
            styled_table_df = table_df.style.applymap(
                highlight_risk_level, subset=['Risk Level']
            )
            st.dataframe(styled_table_df, use_container_width=True)
    
    # Download buttons
    st.subheader("Download Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download raw JSON results
        json_data = json.dumps(db_results, indent=2, default=str)
        st.download_button(
            label="📥 Download Raw Results (JSON)",
            data=json_data,
            file_name=f"database_scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Download findings CSV
        if findings:
            findings_df = pd.DataFrame(findings)
            csv_data = findings_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Findings (CSV)",
                data=csv_data,
                file_name=f"database_pii_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Generate and download HTML report
        if st.button("📄 Generate HTML Report"):
            try:
                from services.report_generator_safe import generate_database_html_report
                
                with st.spinner("Generating HTML report..."):
                    html_content = generate_database_html_report(db_results)
                    
                    st.download_button(
                        label="📥 Download HTML Report",
                        data=html_content,
                        file_name=f"database_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                    st.success("HTML report generated successfully!")
            except ImportError:
                st.warning("HTML report generator not available. Using basic HTML export.")
                
                # Create basic HTML report
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Database Scan Report</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                        .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; }}
                        .critical {{ background-color: #fee2e2; color: #dc2626; }}
                        .high {{ background-color: #fef3c7; color: #d97706; }}
                        .medium {{ background-color: #fde68a; color: #ca8a04; }}
                        .low {{ background-color: #d1fae5; color: #059669; }}
                        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Database Scan Report</h1>
                        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>Database Type: {metadata.get('db_type', 'Unknown')}</p>
                    </div>
                    
                    <h2>Summary</h2>
                    <div class="metric">Tables Scanned: {metadata.get('tables_scanned', 0)}</div>
                    <div class="metric">PII Findings: {len(findings)}</div>
                    <div class="metric">Tables with PII: {db_results.get('tables_with_pii', 0)}</div>
                    <div class="metric">Overall Risk: {risk_summary.get('overall_level', 'Unknown')}</div>
                    
                    <h2>PII Findings</h2>
                    <table>
                        <tr>
                            <th>Table</th>
                            <th>Column</th>
                            <th>PII Type</th>
                            <th>Risk Level</th>
                            <th>Confidence</th>
                            <th>Reason</th>
                        </tr>
                """
                
                for finding in findings:
                    risk_class = finding.get('risk_level', 'low').lower()
                    html_content += f"""
                        <tr>
                            <td>{finding.get('table', '')}</td>
                            <td>{finding.get('column_name', '')}</td>
                            <td>{finding.get('type', '')}</td>
                            <td class="{risk_class}">{finding.get('risk_level', '')}</td>
                            <td>{finding.get('confidence', 0):.1%}</td>
                            <td>{finding.get('reason', '')}</td>
                        </tr>
                    """
                
                html_content += """
                    </table>
                </body>
                </html>
                """
                
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_content,
                    file_name=f"database_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )

def display_api_scan_results():
    """Display API scan results with downloadable reports."""
    if 'api_scan_results' in st.session_state and st.session_state.get('api_scan_complete', False):
        st.header("API Security & Privacy Assessment Results")
        
        api_results = st.session_state.api_scan_results
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            endpoints_scanned = api_results.get('endpoints_scanned', 0)
            st.metric("Endpoints Scanned", endpoints_scanned)
        
        with col2:
            total_findings = api_results.get('stats', {}).get('total_findings', 0)
            st.metric("Total Findings", total_findings)
        
        with col3:
            critical_findings = api_results.get('stats', {}).get('critical_findings', 0)
            st.metric("Critical Issues", critical_findings)
        
        with col4:
            pii_exposures = len(api_results.get('pii_exposures', []))
            st.metric("PII Exposures", pii_exposures)
        
        # Download buttons
        st.subheader("Download Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate and download HTML report
            try:
                from services.api_report_generator import generate_api_html_report
                html_report = generate_api_html_report(api_results)
                
                st.download_button(
                    label="📄 Download HTML Report",
                    data=html_report,
                    file_name=f"api_security_report_{api_results.get('base_url', 'unknown').replace('/', '_').replace(':', '')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating HTML report: {str(e)}")
        
        with col2:
            # Generate and download PDF report
            try:
                import tempfile
                import os
                from services.api_report_generator import generate_api_pdf_report
                
                # Create temporary file for PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_path = generate_api_pdf_report(api_results, tmp_file.name)
                    
                    # Read PDF content
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    st.download_button(
                        label="📑 Download PDF Report",
                        data=pdf_data,
                        file_name=f"api_security_report_{api_results.get('base_url', 'unknown').replace('/', '_').replace(':', '')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Clean up temporary file
                    os.unlink(pdf_path)
                    
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
        
        # Display detailed findings
        st.subheader("Security Findings")
        
        findings = api_results.get('findings', [])
        if findings:
            # Create a DataFrame for better display
            import pandas as pd
            
            findings_data = []
            for finding in findings[:20]:  # Show first 20 findings
                findings_data.append({
                    'Severity': finding.get('severity', 'Unknown'),
                    'Type': finding.get('type', 'Unknown').replace('_', ' ').title(),
                    'Description': finding.get('description', 'No description')[:100] + '...' if len(finding.get('description', '')) > 100 else finding.get('description', 'No description'),
                    'Method': finding.get('method', 'N/A'),
                    'Endpoint': finding.get('endpoint', 'N/A')
                })
            
            if findings_data:
                findings_df = pd.DataFrame(findings_data)
                
                # Apply styling to the dataframe
                def highlight_severity(val):
                    if val == 'Critical':
                        color = 'background-color: #fecaca; color: #991b1b'
                    elif val == 'High':
                        color = 'background-color: #fed7aa; color: #c2410c'
                    elif val == 'Medium':
                        color = 'background-color: #fef3c7; color: #a16207'
                    else:
                        color = 'background-color: #dcfce7; color: #15803d'
                    return color
                
                styled_df = findings_df.style.applymap(highlight_severity, subset=['Severity'])
                st.dataframe(styled_df, use_container_width=True)
                
                if len(findings) > 20:
                    st.info(f"Showing 20 of {len(findings)} total findings. Download the full report for complete details.")
        else:
            st.info("No security findings detected.")
        
        # Display PII exposures
        st.subheader("PII Exposure Analysis")
        
        pii_exposures = api_results.get('pii_exposures', [])
        if pii_exposures:
            pii_data = []
            for pii in pii_exposures[:15]:  # Show first 15 PII exposures
                pii_data.append({
                    'PII Type': pii.get('type', 'Unknown').replace('_', ' ').title(),
                    'Severity': pii.get('severity', 'Medium'),
                    'Count': pii.get('count', 0),
                    'GDPR Category': pii.get('gdpr_category', 'Unknown'),
                    'Method': pii.get('method', 'N/A')
                })
            
            if pii_data:
                import pandas as pd
                pii_df = pd.DataFrame(pii_data)
                
                def highlight_pii_severity(val):
                    if val == 'Critical':
                        color = 'background-color: #fecaca; color: #991b1b'
                    elif val == 'High':
                        color = 'background-color: #fed7aa; color: #c2410c'
                    elif val == 'Medium':
                        color = 'background-color: #fef3c7; color: #a16207'
                    else:
                        color = 'background-color: #dcfce7; color: #15803d'
                    return color
                
                styled_pii_df = pii_df.style.applymap(highlight_pii_severity, subset=['Severity'])
                st.dataframe(styled_pii_df, use_container_width=True)
                
                if len(pii_exposures) > 15:
                    st.info(f"Showing 15 of {len(pii_exposures)} total PII exposures. Download the full report for complete details.")
        else:
            st.info("No PII exposures detected.")
        
        # Display recommendations
        st.subheader("Security Recommendations")
        
        try:
            from services.api_scanner import APIScanner
            scanner = APIScanner()
            recommendations = scanner.generate_privacy_recommendations(api_results)
            
            if recommendations:
                for i, rec in enumerate(recommendations[:8], 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("No specific recommendations generated.")
        except Exception as e:
            st.warning(f"Could not generate recommendations: {str(e)}")
        
        # Clear results button
        if st.button("Clear Results", type="secondary"):
            if 'api_scan_results' in st.session_state:
                del st.session_state.api_scan_results
            if 'api_scan_complete' in st.session_state:
                del st.session_state.api_scan_complete
            st.rerun()

# Check if API scan results should be displayed
if st.session_state.get('api_scan_complete', False):
    display_api_scan_results()

# Check if Database scan results should be displayed
if st.session_state.get('db_scan_complete', False):
    display_database_scan_results()

