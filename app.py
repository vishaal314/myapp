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

# Import modular components
from components.auth_manager import (
    initialize_language_system, 
    handle_forced_language_after_login,
    preserve_language_during_operations,
    debug_translations,
    render_login_interface
)

from components.navigation_manager import (
    create_modern_sidebar_nav,
    get_navigation_options,
    render_user_profile_sidebar,
    render_membership_status,
    render_dashboard_content,
    render_scan_history,
    render_results_page,
    render_reports_page,
    render_admin_page
)

from components.scanner_interface import (
    render_scanner_interface,
    render_scan_submission
)

# Core service imports
from services.auth import is_authenticated, logout
from utils.i18n import get_text

# Define translation function
def _(key, default=None):
    return get_text(key, default)

def main():
    """
    Main application entry point - refactored from 7,627 lines to modular architecture
    Preserves exact UI behavior while improving maintainability
    """
    
    # Initialize language system
    initialize_language_system()
    
    # Handle forced language after login
    handle_forced_language_after_login()
    
    # Preserve language during operations
    preserve_language_during_operations()
    
    # Debug translations in development
    debug_translations()
    
    # Check authentication status
    if not is_authenticated():
        render_login_interface()
        return
    
    # Authenticated user interface
    render_authenticated_interface()

def render_authenticated_interface():
    """
    Render the main authenticated user interface
    Extracted from the main navigation logic in original app.py
    """
    
    # Get user info
    user_role = st.session_state.get('user_role', 'user')
    username = st.session_state.get('username', 'Unknown')
    
    # Get navigation options based on user role
    nav_options = get_navigation_options(user_role)
    
    # Render sidebar
    render_sidebar(nav_options, user_role, username)
    
    # Get selected navigation
    selected_nav = st.session_state.get('selected_nav', nav_options[0] if nav_options else None)
    
    # Route to appropriate page based on navigation selection
    route_to_page(selected_nav, user_role)

def render_sidebar(nav_options, user_role, username):
    """
    Render the complete sidebar with navigation, profile, and membership info
    """
    
    # Create navigation
    selected_nav = create_modern_sidebar_nav(nav_options)
    
    # User profile section
    render_user_profile_sidebar()
    
    # Membership status
    render_membership_status()
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

def route_to_page(selected_nav, user_role):
    """
    Route to appropriate page based on navigation selection
    Extracted from the massive if/elif chain in original app.py
    """
    
    # Get navigation titles with translations
    scan_title = _("scan.title", "Scan")
    dashboard_title = _("dashboard.welcome", "Dashboard")
    history_title = _("history.title", "History")
    results_title = _("results.title", "Results")
    report_title = _("report.generate", "Reports")
    simple_dpia_title = _("dpia.simple_assessment", "Simple DPIA")
    admin_title = _("admin.title", "Admin")
    
    # Route based on selection
    if selected_nav == scan_title:
        render_scanner_interface()
        render_scan_submission()
        
    elif selected_nav == simple_dpia_title:
        # Simple DPIA page - clean, minimal interface
        from simple_dpia import run_simple_dpia
        run_simple_dpia()
        
    elif selected_nav == dashboard_title:
        render_dashboard_content()
        
    elif selected_nav == history_title:
        render_scan_history()
        
    elif selected_nav == results_title:
        render_results_page()
        
    elif selected_nav == report_title:
        render_reports_page()
        
    elif selected_nav == admin_title and user_role == 'admin':
        render_admin_page()
        
    else:
        # Default fallback
        st.title(_("app.welcome", "Welcome to DataGuardian Pro"))
        st.info(_("app.select_option", "Please select an option from the sidebar to get started."))

if __name__ == "__main__":
    main()