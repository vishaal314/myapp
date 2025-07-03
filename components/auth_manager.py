"""
Authentication and Language Management Module
Extracted from app.py to improve modularity while preserving exact UI behavior
"""
import streamlit as st
import logging
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email
from services.stripe_payment import display_payment_button, handle_payment_callback, SCAN_PRICES, verify_payment
from services.subscription_manager import display_subscription_plans, SubscriptionManager
from utils.i18n import initialize, language_selector, get_text, set_language, LANGUAGES, _translations

logger = logging.getLogger(__name__)

# Define translation function
def _(key, default=None):
    return get_text(key, default)

def initialize_language_system():
    """
    Initialize language system - extracted from app.py lines 65-120
    This critical section ensures language preservation across app state changes
    """
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
    global _translations
    _translations = {}  # Reset translations for fresh load
    initialize()  # Initialize translations

def handle_forced_language_after_login():
    """Handle forced language setting after login - extracted from app.py lines 101-120"""
    if 'force_language_after_login' in st.session_state and st.session_state['force_language_after_login']:
        forced_language = st.session_state['force_language_after_login']
        print(f"LOGIN - Forcing language to: {forced_language}")
        
        # Set language immediately
        st.session_state['language'] = forced_language
        st.session_state['_persistent_language'] = forced_language
        
        # Clear the force flag
        st.session_state['force_language_after_login'] = None
        
        # Reinitialize translations with forced language
        set_language(forced_language)
        initialize()
        
        print(f"LOGIN - Language successfully set to: {forced_language}")

def preserve_language_during_operations():
    """Preserve language settings during various operations - extracted from app.py lines 475-520"""
    # Multi-layer language preservation system
    if 'language' in st.session_state:
        # Get language from session state sources
        lang_sources = []
        if 'language' in st.session_state and st.session_state['language']:
            lang_sources.append(st.session_state['language'])
        if '_persistent_language' in st.session_state and st.session_state['_persistent_language']:
            lang_sources.append(st.session_state['_persistent_language'])
        
        # Find the most reliable language
        key = f"language_preservation_{st.session_state.get('language', 'en')}"
        current_language = st.session_state.get('language', 'en')
        
        # Only update if we have a solid language reference
        if current_language in LANGUAGES:
            current_language = current_language
        elif len(lang_sources) > 0:
            current_language = lang_sources[0]
        
        # Preserve language with recursive fallback
        preserved_language = current_language
        
        # Store in multiple locations for redundancy
        if preserved_language and preserved_language in LANGUAGES:
            st.session_state['_persistent_language'] = preserved_language
            st.session_state['pre_login_language'] = preserved_language
            st.session_state['backup_language'] = preserved_language
            st.session_state['language'] = preserved_language
            
            # Ensure the translation system is using this language
            if get_text('app.title', 'DataGuardian Pro') == 'DataGuardian Pro':
                set_language(preserved_language)
                
        return preserved_language
    return 'en'

def debug_translations():
    """Print debug information about critical translation keys - extracted from app.py lines 140-180"""
    try:
        critical_keys = [
            'app.tagline', 'scan.new_scan_title', 'scan.select_type', 
            'scan.upload_files', 'scan.title', 'dashboard.welcome',
            'history.title', 'results.title', 'report.generate'
        ]
        print("TRANSLATION DEBUG - Critical Keys:")
        for key in critical_keys:
            value = get_text(key, f"MISSING: {key}")
            print(f"  {key}: '{value}'")
        
        # Save the current language
        temp_saved_lang = st.session_state.get('language', 'en')
        
        print(f"TRANSLATIONS DEBUG - Raw data for language {temp_saved_lang}:")
        
        # Get the current language setting
        current_language = st.session_state.get('language', 'en')
        
        if current_language in _translations:
            print(f"  Available top-level keys: {list(_translations[current_language].keys())}")
            
            # Check specific key categories
            if 'app' in _translations[current_language]:
                print(f"  app keys: {_translations[current_language]['app']}")
            if 'scan' in _translations[current_language]:
                print(f"  scan keys: {_translations[current_language]['scan']}")
        
        # Language state debugging
        preserved_language = st.session_state.get('_persistent_language', 'en')
        print("LANGUAGE DEBUG - Current state:")
        print(f"  language: {st.session_state.get('language', 'NOT_SET')}")
        print(f"  _persistent_language: {st.session_state.get('_persistent_language', 'NOT_SET')}")
        print(f"  pre_login_language: {st.session_state.get('pre_login_language', 'NOT_SET')}")
        print(f"  backup_language: {st.session_state.get('backup_language', 'NOT_SET')}")
        print(f"  force_language_after_login: {st.session_state.get('force_language_after_login', 'NOT_SET')}")
        
        # Set the current language properly
        current_language = st.session_state.get('language', 'en')
        if current_language in LANGUAGES:
            set_language(current_language)
            print(f"SET_LANGUAGE - Setting language to: {current_language}")
            initialize()
            print(f"INIT - Successfully initialized translations for: {current_language}")
    except Exception as e:
        print(f"DEBUG_TRANSLATIONS - Error: {e}")

def render_login_interface():
    """Render the complete login interface - extracted from app.py lines 290-470"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f2937; margin-bottom: 0.5rem;'>🛡️ DataGuardian Pro</h1>
        <h2 style='color: #4b5563; font-weight: 300; margin-bottom: 2rem;'>Enterprise Privacy Compliance Platform</h2>
        <p style='color: #6b7280; font-size: 1.1rem; margin-bottom: 3rem;'>Detect, Manage, and Report Privacy Compliance with AI-powered Precision</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector - centered and prominent
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        language_selector()
    
    # Get titles and subtitles
    title = _("app.title", "DataGuardian Pro")
    subtitle = _("app.subtitle", "Enterprise Privacy Compliance Platform")
    
    # Navigation tabs
    tab1, tab2 = st.tabs([_("login.signin", "Sign In"), _("login.signup", "Sign Up")])
    
    with tab1:
        render_signin_tab()
    
    with tab2:
        render_signup_tab()

def render_signin_tab():
    """Render sign-in tab content - extracted from app.py lines 320-470"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader(_("login.signin", "Sign In"))
        
        # Password Reset Section
        with st.expander(_("login.forgot_password", "Forgot Password?")):
            reset_col1, reset_col2 = st.columns(2)
            
            with reset_col1:
                st.subheader(_("login.reset_password", "Reset Password"))
                reset_email = st.text_input(_("login.email", "Email"), key="reset_email")
                new_password = st.text_input(_("login.new_password", "New Password"), type="password", key="reset_new_password")
                confirm_password = st.text_input(_("login.confirm_password", "Confirm Password"), type="password", key="reset_confirm_password")
                
                if st.button(_("login.reset_submit", "Reset Password"), key="reset_submit"):
                    if new_password != confirm_password:
                        st.error(_("login.password_mismatch", "Passwords don't match"))
                    elif len(new_password) < 6:
                        st.error(_("login.password_too_short", "Password must be at least 6 characters"))
                    else:
                        # Implement password reset logic
                        if reset_email and new_password:
                            success, message = create_user(reset_email, new_password, 'user', reset_email)
                            if success:
                                st.success(_("login.password_reset_success", "Password reset successful! Please sign in."))
                            else:
                                st.error(f"{_('login.reset_failed', 'Reset failed')}: {message}")
            
            with reset_col2:
                st.info(_("login.reset_instructions", "Enter your email and new password to reset your account."))
        
        # Main login form
        with st.form("login_form"):
            username_or_email = st.text_input(_("login.username_email", "Username or Email"))
            password = st.text_input(_("login.password", "Password"), type="password")
            login_button = st.form_submit_button(_("login.signin", "Sign In"))
        
        if login_button:
            user_data = authenticate(username_or_email, password)
            if user_data:
                st.session_state.authenticated = True
                st.session_state.user_data = user_data
                st.session_state.username = user_data['username']
                st.session_state.user_role = user_data['role']
                st.session_state.user_email = user_data['email']
                
                # Initialize session manager
                from utils.session_manager import SessionManager
                try:
                    session_manager = SessionManager(user_data['username'])
                except:
                    # Fallback if SessionManager doesn't accept username parameter
                    session_manager = SessionManager()
                
                # Handle language forcing after login
                if 'force_language_after_login' in st.session_state:
                    handle_forced_language_after_login()
                
                st.success(_("login.success", "Login successful!"))
                st.rerun()
            else:
                st.error(_("login.invalid", "Invalid username/email or password"))

def render_signup_tab():
    """Render sign-up tab content - extracted from app.py lines 570-630"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader(_("register.signup", "Sign Up"))
        
        # Role selection
        role_options = {
            'user': _("roles.user", "User - Basic scanning permissions"),
            'analyst': _("roles.analyst", "Analyst - Advanced analysis capabilities"),
            'manager': _("roles.manager", "Manager - Team management features"),
            'admin': _("roles.admin", "Admin - Full system access"),
            'auditor': _("roles.auditor", "Auditor - Compliance reporting"),
            'developer': _("roles.developer", "Developer - API access"),
            'security_officer': _("roles.security_officer", "Security Officer - Security oversight")
        }
        
        with st.form("register_form"):
            new_username = st.text_input(_("register.username", "Username"))
            new_email = st.text_input(_("register.email", "Email"))
            new_password = st.text_input(_("register.password", "Password"), type="password")
            new_role = st.selectbox(_("register.role", "Role"), options=list(role_options.keys()), format_func=lambda x: role_options[x])
            confirm_password = st.text_input(_("register.confirm_password", "Confirm Password"), type="password")
            terms = st.checkbox(_("register.terms", "I agree to the Terms of Service and Privacy Policy"))
            register_button = st.form_submit_button(_("register.signup", "Sign Up"))
        
        if register_button:
            success, message = create_user(new_username, new_password, new_role, new_email)
            if success:
                st.success(_("register.success", "Account created successfully! Please sign in."))
            else:
                st.error(f"{_('register.failed', 'Registration failed')}: {message}")